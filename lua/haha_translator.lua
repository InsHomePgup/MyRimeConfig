-- encoding: utf-8
--- 连按 h 输出同样个数的「哈」：hhhhh → 哈哈哈哈哈
-- 虎码（rime.lua 注册全局变量，写 lua_translator@haha_translator）和
-- 雾凇双拼（写 lua_translator@*haha_translator）共用；最少几个 h 才触发在 schema 里配置：
--   haha_translator:
--     min_length: 5

local M = {}

function M.init(env)
   local config = env.engine.schema.config
   local ns = env.name_space:gsub("^%*", "")
   env.min_length = config:get_int(ns .. "/min_length") or 3
end

function M.func(input, seg, env)
   local n = #input
   if n < env.min_length or input:find("[^h]") then
      return
   end
   local cand = Candidate("haha", seg.start, seg._end, string.rep("哈", n), "")
   cand.quality = 10000
   yield(cand)
end

return M
