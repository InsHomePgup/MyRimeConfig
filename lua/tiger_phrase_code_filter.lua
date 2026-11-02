-- encoding: utf-8
--- 双拼反查词组时，逐字注释虎码编码
-- 虎码词典只有单字，反查出的词组本身没有编码提示，这里按字拼出来，如：你好 jx xx

local M = {}

function M.init(env)
   local dict = env.engine.schema.config:get_string("translator/dictionary") or "tiger"
   env.rev = ReverseLookup(dict)
end

-- 一个字可能有多个编码，取最短的
local function shortest_code(rev, char)
   local best
   for code in rev:lookup(char):gmatch("%S+") do
      if not best or #code < #best then best = code end
   end
   return best
end

function M.func(input, env)
   for cand in input:iter() do
      if utf8.len(cand.text) > 1 and cand.comment:match("^%s*$") then
         local codes = {}
         for _, cp in utf8.codes(cand.text) do
            codes[#codes + 1] = shortest_code(env.rev, utf8.char(cp)) or "?"
         end
         yield(ShadowCandidate(cand, cand.type, cand.text, " " .. table.concat(codes, " ")))
      else
         yield(cand)
      end
   end
end

return M
