-- 所有窗口共用同一个方案
--
-- Rime 每个窗口一个会话，会话只在创建时读一次 user.yaml 的 var/previously_selected_schema，
-- 之后就各管各的：在 A 窗口从方案选单换了方案，切回早已打开的 B 窗口还是旧方案。
-- 这个处理器在每次按键时比对「最近一次从方案选单选中的方案」和当前方案，
-- 不一致就切过去，再把这次按键交给新方案处理。
--
-- user.yaml 由方案选单（switcher）在内存里改写，所有会话共用同一份，读它只是一次查表。
-- 放在 processors 第一个；虎码在 rime.lua 里注册为 schema_sync，雾凇用 lua_processor@*schema_sync。

local kAccepted, kNoop = 1, 2

local function schema_exists(id)
  local f = io.open(rime_api.get_user_data_dir() .. "/build/" .. id .. ".schema.yaml", "r")
  if f then f:close() return true end
  return false
end

local M = {}

function M.init(env)
  env.switcher = Switcher(env.engine)  -- 要留着 switcher，user_config 归它所有
  env.user_config = env.switcher.user_config
end

function M.func(key, env)
  local engine = env.engine
  local target = env.user_config and env.user_config:get_string("var/previously_selected_schema")
  if not target or target == "" or target == engine.schema.schema_id then
    return kNoop
  end
  if engine.context:is_composing() or not schema_exists(target) then
    return kNoop
  end
  -- apply_schema 会重建处理器（包括本处理器），之后只能返回 kAccepted，不能让旧的处理器链继续跑
  engine:apply_schema(Schema(target))
  engine:process_key(key)
  return kAccepted
end

return M
