-- user_predict.lua：从输入习惯学习联想（只在元书上启用，见 double_pinyin.custom.yaml）
--
-- librime-predict 插件提供底库联想，但它只拿“上一次上屏的整段文字”去精确匹配，
-- 也不会学习。这个模块补上两点：
--   1. 学习：每次上屏，记录「上一段 → 这一段」的次数，存在 user_predict.userdb，
--      格式与 Rime 用户词典相同（c= d= t=），会随 Rime「同步」在设备间合并。
--   2. 联想：在联想分段里把学到的搭配排在底库前面；整段查不到时退回到结尾的 3、2、1 个字。
--      插件没查到底库、但学到过的时候，由这里创建联想分段。
--
-- 用法（schema）：
--   engine/processors: lua_processor@*user_predict*processor   （放在 predictor 之后：
--       update_notifier 按连接顺序回调，要让插件先按底库建分段，这里再补）
--   engine/translators: lua_translator@*user_predict*translator（放在 predict_translator 之前）
--   user_predict: { max_candidates: 5 }

local DB_NAME = "user_predict"
local MAX_CONTEXT = 4        -- 上文最多取结尾 4 个字
local MAX_NEXT = 6           -- 超过 6 个字的上屏（多半是整句）不当作联想词记
local CONTEXT_TIMEOUT = 60   -- 两次上屏间隔超过 60 秒不算上下文
local UNDO_WINDOW = 5        -- 上屏后 5 秒内删除，撤销刚学到的记录
local QUALITY = 1000         -- 排在插件联想（quality 0）前面

-- ---------------------------------------------------------------- 数据库
-- 同一个数据库在处理器和翻译器之间共用；每个会话的状态（上一段文字等）放在 env 里共用的 state 表
local db
local db_refs = 0

local function open_db()
    if not db then
        db = UserDb(DB_NAME, "userdb")
    end
    if not db:loaded() then
        db:open()
    end
    db_refs = db_refs + 1
    return db
end

local function close_db()
    db_refs = db_refs - 1
    if db_refs <= 0 and db then
        if db:loaded() then db:close() end
        db = nil
        db_refs = 0
    end
end

local function parse_count(value)
    return tonumber(value and value:match("c=(%-?%d+)") or 0) or 0
end

-- 次数 <= 0 时不直接删除，而是像 Rime 用户词典一样写成负数（删除标记）：
-- 「同步」会把 sync/ 下所有快照（包括本机自己的）合并回来，合并时保留绝对值大的一方，
-- 直接删掉的记录会被旧快照恢复，写成 -n 才能盖过快照里的 n。
local function write_count(key, c)
    db:update(key, string.format("c=%d d=0 t=0", c))
end

local function add_count(key, delta)
    if not (db and db:loaded()) then return end
    local old = parse_count(db:fetch(key))
    local c
    if old < 0 and delta > 0 then
        c = delta                -- 删过的又学到：从头计数
    else
        c = old + delta
    end
    if c > 0 then
        write_count(key, c)
    elseif old ~= 0 then
        write_count(key, -math.max(math.abs(old), 1))
    end
end

-- 一次性清理：2026-11-13 测试时来回点联想词，把这两条刷到了十几次
-- （防来回刷的逻辑加上之后不会再出现）。清理过的数据库记一个标记，只做一次。
local CLEANUP_FLAG = "\001/user_predict_cleanup"
local CLEANUP_KEYS = { "的 \t人", "人 \t的" }

local function cleanup_once()
    if not (db and db:loaded()) or db:fetch(CLEANUP_FLAG) then return end
    for _, key in ipairs(CLEANUP_KEYS) do
        local c = parse_count(db:fetch(key))
        if c > 0 then write_count(key, -c) end
    end
    db:update(CLEANUP_FLAG, "20261113")
end

-- ---------------------------------------------------------------- 文字处理
local function chars(text)
    local out = {}
    for _, cp in utf8.codes(text) do
        out[#out + 1] = utf8.char(cp)
    end
    return out
end

-- 只学纯汉字：标点、字母、数字、Emoji 都打断上下文
local function is_hanzi(text)
    if text == "" then return false end
    for _, cp in utf8.codes(text) do
        if not ((cp >= 0x4E00 and cp <= 0x9FFF) or (cp >= 0x3400 and cp <= 0x4DBF)
                or (cp >= 0x20000 and cp <= 0x323AF) or cp == 0x3007) then
            return false
        end
    end
    return true
end

-- 上文的结尾 n 个字，从长到短
local function context_keys(text)
    local cs = chars(text)
    local keys = {}
    for n = math.min(#cs, MAX_CONTEXT), 1, -1 do
        keys[#keys + 1] = table.concat(cs, "", #cs - n + 1)
    end
    return keys
end

local function make_key(context, next_text)
    return context .. " \t" .. next_text
end

-- 按上文查学到的联想：先用最长的上文，不够再用短的；同一层里按次数排
local function lookup(context, limit)
    local result, seen = {}, {}
    if not (db and db:loaded()) or not context then return result end
    for _, ctx in ipairs(context_keys(context)) do
        local prefix = ctx .. " \t"
        local found = {}
        local da = db:query(prefix)
        if da then
            for key, value in da:iter() do
                if key:sub(1, #prefix) ~= prefix then break end
                local text = key:sub(#prefix + 1)
                local c = parse_count(value)
                if c > 0 and not seen[text] then
                    found[#found + 1] = { text = text, count = c }
                end
            end
            da = nil
        end
        table.sort(found, function(a, b) return a.count > b.count end)
        for _, f in ipairs(found) do
            if not seen[f.text] then
                seen[f.text] = true
                result[#result + 1] = f.text
                if #result >= limit then return result end
            end
        end
    end
    return result
end

-- ---------------------------------------------------------------- 会话状态
-- 状态放在处理器的 env 里；翻译器只需要“上一段文字”，通过 context 属性传过去
-- （env.engine 每次访问都是新的包装对象，不能拿来当表的键）
local PROP_LAST = "user_predict/last"

local function set_last(ctx, s, text)
    s.last_text = text
    ctx:set_property(PROP_LAST, text or "")
end

local function learn(ctx, s, text)
    local now = os.time()
    s.learned = nil
    if not is_hanzi(text) then
        set_last(ctx, s, nil)
        return
    end
    local cs = chars(text)
    -- 来回点联想词（A → B → A → B）会互相刷次数：刚记过 A → B，这次又是 B → A，就不记
    -- （跳过的这一对也要记住，否则 A → B 会每隔一次又被记上）
    local ping_pong = s.pair and s.pair.from == text and s.pair.to == s.last_text
    s.pair = s.last_text and { from = s.last_text, to = text } or nil
    if s.last_text and now - s.last_time <= CONTEXT_TIMEOUT and #cs <= MAX_NEXT and not ping_pong then
        local keys = {}
        for _, context in ipairs(context_keys(s.last_text)) do
            local key = make_key(context, text)
            add_count(key, 1)
            keys[#keys + 1] = key
        end
        s.learned = { keys = keys, time = now }
    end
    set_last(ctx, s, text)
    s.last_time = now
end

-- 上屏后马上删除：说明刚才那次上屏不对，撤销学到的记录，并断开上下文
local function undo(ctx, s)
    if s.learned and os.time() - s.learned.time <= UNDO_WINDOW then
        for _, key in ipairs(s.learned.keys) do
            add_count(key, -1)
        end
    end
    s.learned = nil
    set_last(ctx, s, nil)
end

-- ---------------------------------------------------------------- 处理器：学习 + 补联想分段
local processor = {}

function processor.init(env)
    local ctx = env.engine.context
    local s = { last_text = nil, last_time = 0, learned = nil, creating = false, just_committed = false }
    env.state = s
    open_db()
    cleanup_once()
    env.commit_conn = ctx.commit_notifier:connect(function(c)
        learn(c, s, c:get_commit_text())
        s.just_committed = true
    end)
    -- 插件（predictor）在 update_notifier 里按底库创建联想分段；这里排在它后面，
    -- 底库没查到、但学到过时，自己创建一个同样的分段
    env.update_conn = ctx.update_notifier:connect(function(c)
        if s.creating or not s.just_committed then return end
        s.just_committed = false
        if not c:get_option("prediction") or c.input ~= "" or not c.composition:empty() then
            return
        end
        if #lookup(s.last_text, 1) == 0 then return end
        local seg = Segment(0, 0)
        seg.tags = Set({ "prediction", "placeholder" })
        c.composition:push_back(seg)
        s.creating = true
        c.input = ""   -- 触发重新组合，翻译器为这个分段出候选（插件也是这样做的）
        s.creating = false
    end)
end

function processor.func(key, env)
    if key:release() then return 2 end
    -- 有联想分段时删除键只是关掉联想（predictor 会处理），不算撤销
    local ctx = env.engine.context
    if key:repr() == "BackSpace" and ctx.input == "" and ctx.composition:empty() then
        undo(ctx, env.state)
    end
    return 2   -- kNoop：不拦截任何按键
end

function processor.fini(env)
    if env.commit_conn then env.commit_conn:disconnect() end
    if env.update_conn then env.update_conn:disconnect() end
    close_db()
end

-- ---------------------------------------------------------------- 翻译器：学到的联想
local translator = {}

function translator.init(env)
    open_db()
    env.max_candidates = env.engine.schema.config:get_int("user_predict/max_candidates") or 5
end

function translator.func(input, seg, env)
    if not seg:has_tag("prediction") then return end
    local last = env.engine.context:get_property(PROP_LAST)
    if last == "" then return end
    for _, text in ipairs(lookup(last, env.max_candidates)) do
        local cand = Candidate("prediction", seg.start, seg._end, text, "")
        cand.quality = QUALITY
        yield(cand)
    end
end

function translator.fini(env)
    close_db()
end

return { processor = processor, translator = translator }
