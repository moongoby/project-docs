---
project: AADS
task_id: ERROR
completed_at: 2026-03-06 15:14:57 KST
status: error
exit_code: 1
---
## 에러 종료
{"type":"result","subtype":"success","is_error":true,"duration_ms":432725,"duration_api_ms":429984,"num_turns":54,"result":"Credit balance is too low","stop_reason":"stop_sequence","session_id":"d49e278e-0071-491d-9aef-2cbe2a033032","total_cost_usd":2.0034312499999998,"usage":{"input_tokens":52,"cache_creation_input_tokens":64815,"cache_read_input_tokens":1815855,"output_tokens":27606,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":64815},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{"claude-sonnet-4-6":{"inputTokens":52,"outputTokens":27606,"cacheReadInputTokens":1815855,"cacheCreationInputTokens":64815,"webSearchRequests":0,"costUSD":2.0034312499999998,"contextWindow":200000,"maxOutputTokens":32000}},"permission_denials":[],"fast_mode_state":"off","uuid":"71124cd7-6b6a-467c-8451-9741a0e017f0"}
[2026-03-06 15:14:47 KST] [RETRY] rate_limit 감지 — 계정 스위치 후 재시도
[2026-03-06 15:14:47 KST] [RETRY] [SWITCH] OAuth token2 → token1 교체 완료
{"type":"result","subtype":"success","is_error":true,"duration_ms":479,"duration_api_ms":0,"num_turns":1,"result":"Credit balance is too low","stop_reason":"stop_sequence","session_id":"92cc953a-b1d7-4f37-b96b-b84352e31e41","total_cost_usd":0,"usage":{"input_tokens":0,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{},"permission_denials":[],"fast_mode_state":"off","uuid":"11873ac7-b067-48cc-a39b-cba3c4acd668"}
[2026-03-06 15:14:57 KST] [RETRY] 재시도 완료 (exit_code: 1)
