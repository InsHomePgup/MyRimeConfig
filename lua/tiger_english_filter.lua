-- encoding: utf-8
--- 虎码直接打英文：4 码以内只显示虎码候选（空码时才显示英文），超过 4 码只剩英文
-- 英文候选来自无前缀的 table_translator@english_auto，靠文本里有没有中文/全角字符来区分

local function is_english(text)
   -- 中文、全角符号都是 3 字节以上的 UTF-8，首字节 >= 0xE0；英文（含带音标的拉丁字母）都在此以下
   return not text:find("[\224-\255]")
end

local function func(input, env)
   local has_tiger = false
   for cand in input:iter() do
      if not is_english(cand.text) then
         has_tiger = true
         yield(cand)
      elseif not has_tiger or cand._end - cand._start > 4 then
         yield(cand)
      else
         -- 英文候选权重低，都排在虎码之后，后面不会再有虎码了；
         -- 不 break 的话会把成千上万条英文补全全部遍历一遍，打字明显卡顿
         break
      end
   end
end

return func
