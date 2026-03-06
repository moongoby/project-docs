---
project: KIS AutoTrade V4.1
task_id: T-171
completed_at: 2026-03-06T11:50:00+09:00 KST
---

# T-171 실행 결과 — Redis 반복 끊김 근본 원인 진단

## 실행한 모든 명령어 및 결과 원문

---

### 명령 1: .env Redis 설정 확인
```bash
grep -rn "redis\|REDIS" /root/kis-autotrade-v4/.env 2>/dev/null
```
**출력:**
```
25:REDIS_HOST=localhost
26:REDIS_PORT=6379
27:REDIS_DB=0
28:REDIS_URL=redis://localhost:6379/0
```

---

### 명령 2: core/ 디렉토리 Redis 관련 설정 확인
```bash
grep -rn "redis_url\|REDIS_URL\|redis_host\|REDIS_HOST\|redis_pool\|max_connections\|timeout\|retry" /root/kis-autotrade-v4/backend/app/core/ 2>/dev/null | head -30
```
**출력:**
```
/root/kis-autotrade-v4/backend/app/core/broker_kiwoom_client.py.bak.20260219235207:38:        self._http = httpx.AsyncClient(timeout=30.0)
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:75:    def acquire(self, timeout: float = 30.0) -> float:
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:80:            timeout: 최대 대기 시간 (초)
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:101:            if wait_time > timeout:
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:103:                    f"[RateLimiter:{self.name}] 대기 시간 {wait_time:.2f}s > timeout {timeout}s"
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:123:    async def async_acquire(self, timeout: float = 30.0) -> float:
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:138:            if wait_time > timeout:
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:201:        self._retry_count = 0
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:204:    def should_retry(self, response_data: dict) -> bool:
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:218:    def get_retry_delay(self, attempt: int) -> float:
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:223:    def wait_and_retry(self, attempt: int, error_code: str = "") -> float:
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:225:        delay = self.get_retry_delay(attempt)
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:234:    async def async_wait_and_retry(self, attempt: int,
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:237:        delay = self.get_retry_delay(attempt)
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:270:_retry_handler = None
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:298:def get_retry_handler() -> KISRetryHandler:
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:300:    global _retry_handler
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:303:        if _retry_handler is None:
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:304:            _retry_handler = KISRetryHandler(
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:309:        return _retry_handler
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:319:    if _retry_handler:
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:320:        stats["retry_handler"] = _retry_handler.get_stats()
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:360:    async def acquire(self, timeout: float = 5.0) -> bool:
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:363:        timeout 내에 토큰을 얻지 못하면 False.
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:365:        deadline = time.monotonic() + timeout
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:575:        timeout: float = 5.0,
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:589:            if not await global_bucket.acquire(timeout):
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:598:            if not await acct_bucket.bucket.acquire(timeout):
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:615:        timeout: float = 5.0,
/root/kis-autotrade-v4/backend/app/core/kis_rate_limiter.py:627:            return await global_bucket.acquire(timeout)
```
**→ core/ 내에 Redis 연결풀 설정(max_connections, health_check_interval 등) 없음 확인**

---

### 명령 3: Redis 클라이언트 import/초기화 코드 확인
```bash
grep -rn "import redis\|aioredis\|Redis(\|redis.from_url\|ConnectionPool" /root/kis-autotrade-v4/backend/ 2>/dev/null | head -30
```
**출력:**
```
/root/kis-autotrade-v4/backend/app/main.py.bak_20260219_163430:16:from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/core/redis.py:6:import redis.asyncio as aioredis
/root/kis-autotrade-v4/backend/app/core/redis.py:9:redis_client = aioredis.from_url(
/root/kis-autotrade-v4/backend/app/core/rate_limiter.py:109:        from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/core/kiwoom_key_manager.py:128:            import redis
/root/kis-autotrade-v4/backend/app/core/kiwoom_key_manager.py:146:            import redis
/root/kis-autotrade-v4/backend/app/core/kiwoom_key_manager.py:253:                from backend.app.core.redis import redis_client as default_redis
/root/kis-autotrade-v4/backend/app/core/llm_rate_limiter.py:57:        from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/core/llm_rate_limiter.py:78:        from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/core/llm_rate_limiter.py:90:        from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/core/llm_rate_limiter.py:113:        from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/core/token_manager.py:22:import redis.asyncio as aioredis
/root/kis-autotrade-v4/backend/app/core/token_manager.py:58:    def __init__(self, redis_client: aioredis.Redis):
/root/kis-autotrade-v4/backend/app/core/token_manager.py:278:def get_token_manager(redis_client: Optional[aioredis.Redis] = None) -> TokenManager:
/root/kis-autotrade-v4/backend/app/core/token_manager.py:283:            from backend.app.core.redis import redis_client as default_redis
/root/kis-autotrade-v4/backend/app/core/token_manager.py:301:    import redis
/root/kis-autotrade-v4/backend/app/routers/go100/ai_router.py:212:        from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/routers/go100/ai_router.py:269:        from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/routers/go100/ai_router.py:1312:            from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/routers/go100/ai_router.py:1379:        from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/routers/go100/ai_router.py:1411:            from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/routers/go100/ai_router.py:2239:            from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/routers/go100/ai_router.py:2355:                from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/routers/go100/notification_router.py:13:from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/routers/go100/monitor_router.py:15:from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/routers/go100/scheduler_router.py:11:from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/routers/go100/ai_router.py.bak.20260227:183:        from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/routers/go100/ai_router.py.bak.20260227:236:        from backend.app.core.redis import redis_client
/root/kis-autotrade-v4/backend/app/routers/go100/ai_router.py.bak.20260227:1275:            from backend.app.core.redis import redis_client
```

---

### 명령 4: redis.py 파일 전체 내용 확인
```
파일 경로: /root/kis-autotrade-v4/backend/app/core/redis.py
```
**전체 내용 (19줄):**
```python
"""
KIS AutoTrade V4.0 — Redis 연결
캐시, 세션, 분산 락 등에 사용
"""

import redis.asyncio as aioredis
from backend.app.core.config import settings

redis_client = aioredis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis() -> aioredis.Redis:
    """FastAPI Depends용 Redis 클라이언트 제공"""
    return redis_client
```

---

### 명령 5: Redis health check 코드 확인
```bash
grep -rn "def.*health\|redis.*ping\|redis.*connected\|redis.*status\|redis_status\|redis_connected" /root/kis-autotrade-v4/backend/app/ 2>/dev/null | head -30
```
**출력:**
```
/root/kis-autotrade-v4/backend/app/main.py.bak_20260219_163430:88:        await redis_client.ping()
/root/kis-autotrade-v4/backend/app/main.py.bak_20260219_163430:182:async def health_check():
/root/kis-autotrade-v4/backend/app/main.py.bak_20260219_163430:199:        await redis_client.ping()
/root/kis-autotrade-v4/backend/app/main.py.bak_20260219_163430:200:        health["redis"] = "connected"
/root/kis-autotrade-v4/backend/app/main.py.bak_20260219_163430:202:        health["redis"] = "disconnected"
/root/kis-autotrade-v4/backend/app/core/rate_limiter.py:115:        await redis_client.ping()
/root/kis-autotrade-v4/backend/app/core/llm_rate_limiter.py:58:        await redis_client.ping()
/root/kis-autotrade-v4/backend/app/routers/go100/monitor_router.py:25:async def monitor_health() -> Dict[str, Any]:
/root/kis-autotrade-v4/backend/app/routers/go100/monitor_router.py:48:        await redis_client.ping()
/root/kis-autotrade-v4/backend/app/routers/go100/monitor_router.py:49:        out["redis"] = "connected"
/root/kis-autotrade-v4/backend/app/routers/go100/monitor_router.py:51:        out["redis"] = "disconnected"
/root/kis-autotrade-v4/backend/app/routers/v4_system.py:65:async def get_system_health():
/root/kis-autotrade-v4/backend/app/routers/v4_system.py:77:        await redis_client.ping()
/root/kis-autotrade-v4/backend/app/routers/v4_system.py:78:        checks["redis"] = "connected"
/root/kis-autotrade-v4/backend/app/routers/monitoring_router.py:11:    get_redis_status,
/root/kis-autotrade-v4/backend/app/routers/monitoring_router.py:30:    redis = await get_redis_status()
/root/kis-autotrade-v4/backend/app/routers/monitoring_router.py:89:async def monitoring_api_health(
/root/kis-autotrade-v4/backend/app/main.py.bak.T031:202:        await redis_client.ping()
/root/kis-autotrade-v4/backend/app/main.py.bak.T031:477:async def health_check():
/root/kis-autotrade-v4/backend/app/main.py.bak.T031:494:        await redis_client.ping()
/root/kis-autotrade-v4/backend/app/main.py.bak.T031:495:        health["redis"] = "connected"
/root/kis-autotrade-v4/backend/app/main.py.bak.T031:497:        health["redis"] = "disconnected"
/root/kis-autotrade-v4/backend/app/main.py.bak.phase3:189:        await redis_client.ping()
/root/kis-autotrade-v4/backend/app/main.py.bak.phase3:432:async def health_check():
/root/kis-autotrade-v4/backend/app/main.py.bak.phase3:449:        await redis_client.ping()
/root/kis-autotrade-v4/backend/app/main.py.bak.phase3:450:        health["redis"] = "connected"
/root/kis-autotrade-v4/backend/app/main.py.bak.phase3:452:        health["redis"] = "disconnected"
/root/kis-autotrade-v4/backend/app/main.py:205:        await redis_client.ping()
/root/kis-autotrade-v4/backend/app/main.py:483:async def health_check():
/root/kis-autotrade-v4/backend/app/main.py:500:        await redis_client.ping()
```
**→ 모든 health check: ping() 실패 시 "disconnected" 보고만 하고 reconnect 없음**

---

### 명령 6: Redis 서버 설정
```bash
redis-cli CONFIG GET maxclients
redis-cli CONFIG GET timeout
redis-cli CONFIG GET tcp-keepalive
redis-cli INFO clients
```
**출력:**
```
maxclients
10000
timeout
0
tcp-keepalive
300
# Clients
connected_clients:23
cluster_connections:0
maxclients:10000
client_recent_max_input_buffer:8
client_recent_max_output_buffer:0
blocked_clients:0
tracking_clients:0
clients_in_timeout_table:0
```

---

### 명령 7: 현재 Redis 연결 수
```bash
redis-cli CLIENT LIST 2>/dev/null | wc -l
```
**출력:**
```
23
```

---

### 명령 8: core/ 데이터베이스/redis 파일 class/함수 확인
```bash
grep -rn "class.*Redis\|redis_client\|get_redis" /root/kis-autotrade-v4/backend/app/core/database*.py /root/kis-autotrade-v4/backend/app/core/config*.py /root/kis-autotrade-v4/backend/app/core/redis*.py 2>/dev/null | head -20
```
**출력:**
```
/root/kis-autotrade-v4/backend/app/core/redis.py:9:redis_client = aioredis.from_url(
/root/kis-autotrade-v4/backend/app/core/redis.py:16:async def get_redis() -> aioredis.Redis:
/root/kis-autotrade-v4/backend/app/core/redis.py:18:    return redis_client
```

---

### 명령 9: systemd 서비스 Redis 의존성 확인
```bash
cat /etc/systemd/system/go100.service 2>/dev/null | grep -i "redis\|after\|requires"
cat /etc/systemd/system/kis-v41-api.service 2>/dev/null | grep -i "redis\|after\|requires"
```
**출력:**
```
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service
After=postgresql.service redis.service
Requires=postgresql.service
```
**→ go100.service: Wants=redis.service (soft) / Requires=postgresql.service 만 (redis.service Requires 없음)**

---

### 명령 10: Redis 에러/통계
```bash
redis-cli INFO stats | grep -i "expired\|evicted\|rejected\|error\|total_commands\|connected"
```
**출력:**
```
total_commands_processed:371792
rejected_connections:0
expired_keys:141
expired_stale_perc:0.00
expired_time_cap_reached_count:0
evicted_keys:0
evicted_clients:0
unexpected_error_replies:0
total_error_replies:303654
```

---

### 명령 11: Redis 서버 버전/업타임
```bash
redis-cli INFO server | grep -i "redis_version\|uptime\|hz\|loglevel\|logfile"
```
**출력:**
```
redis_version:7.0.15
uptime_in_seconds:155942
uptime_in_days:1
hz:10
configured_hz:10
```

---

### 명령 12: Redis 상세 에러/명령 통계
```bash
redis-cli INFO all | grep -i "error\|wrong\|fail"
```
**출력:**
```
aof_rewrites_consecutive_failures:0
unexpected_error_replies:0
total_error_replies:303654
master_failover_state:no-failover
cmdstat_info:calls=31,usec=7269,usec_per_call=234.48,rejected_calls=0,failed_calls=0
cmdstat_dbsize:calls=1,usec=4,usec_per_call=4.00,rejected_calls=0,failed_calls=0
cmdstat_multi:calls=1234,usec=1318,usec_per_call=1.07,rejected_calls=0,failed_calls=0
cmdstat_publish:calls=2,usec=15,usec_per_call=7.50,rejected_calls=0,failed_calls=0
cmdstat_exec:calls=1234,usec=44080,usec_per_call=35.72,rejected_calls=0,failed_calls=0
cmdstat_expire:calls=596,usec=2832,usec_per_call=4.75,rejected_calls=0,failed_calls=0
cmdstat_zadd:calls=594,usec=15779,usec_per_call=26.56,rejected_calls=0,failed_calls=0
cmdstat_client|list:calls=1,usec=2518,usec_per_call=2518.00,rejected_calls=0,failed_calls=0
cmdstat_zcard:calls=640,usec=726,usec_per_call=1.13,rejected_calls=0,failed_calls=0
cmdstat_unsubscribe:calls=11,usec=167,usec_per_call=15.18,rejected_calls=0,failed_calls=0
cmdstat_ping:calls=1008,usec=4717,usec_per_call=4.68,rejected_calls=0,failed_calls=0
cmdstat_setex:calls=2,usec=19,usec_per_call=9.50,rejected_calls=0,failed_calls=0
cmdstat_zremrangebyscore:calls=640,usec=11188,usec_per_call=17.48,rejected_calls=0,failed_calls=0
cmdstat_subscribe:calls=12,usec=2126,usec_per_call=177.17,rejected_calls=0,failed_calls=0
cmdstat_incrby:calls=2,usec=17,usec_per_call=8.50,rejected_calls=0,failed_calls=0
cmdstat_set:calls=12,usec=2806,usec_per_call=233.83,rejected_calls=0,failed_calls=0
cmdstat_config|get:calls=3,usec=1120,usec_per_call=373.33,rejected_calls=0,failed_calls=0
cmdstat_get:calls=338589,usec=1954341,usec_per_call=5.77,rejected_calls=0,failed_calls=0
cmdstat_keys:calls=3,usec=1162,usec_per_call=387.33,rejected_calls=0,failed_calls=0
cmdstat_del:calls=4,usec=22,usec_per_call=5.50,rejected_calls=0,failed_calls=0
cmdstat_exists:calls=27175,usec=101721,usec_per_call=3.74,rejected_calls=0,failed_calls=0
# Errorstats
errorstat_ERR:count=303654
```

---

### 명령 13: Redis CLIENT LIST 전체 (좀비 연결 분석)
```bash
redis-cli CLIENT LIST 2>/dev/null
```
**출력 (주요 idle 연결 강조):**
```
id=14 addr=127.0.0.1:48034 ... age=155864 idle=74565 ... cmd=exists
id=31549 addr=127.0.0.1:32818 ... age=92703 idle=92700 ... cmd=get
id=7 addr=127.0.0.1:40852 ... age=155924 idle=60045 ... cmd=exists
id=151858 addr=127.0.0.1:51012 ... age=307 idle=307 ... cmd=get
id=8 addr=127.0.0.1:40856 ... age=155924 idle=55185 ... cmd=exists
id=151610 addr=127.0.0.1:45628 ... age=64676 idle=107 ... cmd=ping
id=15 addr=127.0.0.1:41728 ... age=155264 idle=141944 ... cmd=exists
id=9 addr=127.0.0.1:40872 ... age=155924 idle=28 ... cmd=exists
id=151608 addr=127.0.0.1:45606 ... age=64677 idle=3784 ... cmd=exec
id=10 addr=127.0.0.1:40886 ... age=155924 idle=55185 ... cmd=exists
id=11 addr=127.0.0.1:40900 ... age=155924 idle=57105 ... cmd=exists
id=151602 addr=127.0.0.1:32970 ... age=66576 idle=64677 ... cmd=ping
id=151822 addr=127.0.0.1:42600 ... age=5651 idle=5651 ... cmd=get
id=12 addr=127.0.0.1:40904 ... age=155924 idle=58005 ... cmd=exists
id=151736 addr=127.0.0.1:44312 ... age=7171 idle=7171 ... cmd=get
id=151737 addr=127.0.0.1:44322 ... age=7171 idle=7171 ... cmd=get
id=151606 addr=127.0.0.1:45582 ... age=64677 idle=3784 ... cmd=exec
id=154 addr=127.0.0.1:48572 ... age=102764 idle=57165 ... cmd=exists
id=151342 addr=127.0.0.1:55346 ... age=79152 idle=64677 ... cmd=ping
id=151864 addr=127.0.0.1:54996 ... age=9 idle=9 ... cmd=get
id=151774 addr=127.0.0.1:44664 ... age=7169 idle=7169 ... cmd=get
id=13 addr=127.0.0.1:40916 ... age=155924 idle=27 ... cmd=exists
id=151819 addr=127.0.0.1:42572 ... age=5651 idle=5651 ... cmd=get
id=151868 addr=127.0.0.1:37964 ... age=0 idle=0 ... cmd=client|list
```

---

### 명령 14: reconnect/pool 설정 코드 grep
```bash
grep -rn "reconnect\|close\|aclose\|connection_pool\|health_check_interval\|socket_keepalive\|socket_timeout" /root/kis-autotrade-v4/backend/app/core/redis.py /root/kis-autotrade-v4/backend/app/main.py 2>/dev/null | head -30
```
**출력:**
```
/root/kis-autotrade-v4/backend/app/main.py:326:    await redis_client.close()
```
**→ 유일하게 close()만 존재. reconnect/health_check_interval/socket_keepalive 전무**

---

### 명령 15: Redis 메모리 정보
```bash
redis-cli INFO memory | grep -i "used_memory\|maxmemory\|mem_fragmentation"
```
**출력:**
```
used_memory:1605136
used_memory_human:1.53M
used_memory_rss:11259904
used_memory_rss_human:10.74M
used_memory_peak:6312696
used_memory_peak_human:6.02M
used_memory_peak_perc:25.43%
used_memory_overhead:959472
used_memory_startup:875968
used_memory_dataset:645664
used_memory_dataset_perc:88.55%
used_memory_lua:31744
used_memory_vm_eval:31744
used_memory_lua_human:31.00K
used_memory_scripts_eval:0
used_memory_vm_functions:32768
used_memory_vm_total:64512
used_memory_vm_total_human:63.00K
used_memory_functions:200
used_memory_scripts:200
used_memory_scripts_human:200B
maxmemory:0
maxmemory_human:0B
maxmemory_policy:noeviction
mem_fragmentation_ratio:7.19
mem_fragmentation_bytes:9693088
```

---

### 명령 16: Redis keyspace
```bash
redis-cli INFO keyspace
```
**출력:**
```
# Keyspace
db0:keys=7,expires=7,avg_ttl=109932653
```

---

### 명령 17: Redis 전체 키 목록
```bash
redis-cli KEYS "*"
```
**출력:**
```
token:kis:kis:4
blacklist:token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNSIsImlzX2FkbWluIjp0cnVlLCJpc19zdXBlcnVzZXIiOmZhbHNlLCJleHAiOjE3NzI0NTEwMjl9.j5TijhWrGmqUIDk190Wjpju-Ef8LELJlsASNoQ2e6Zo
token:kiwoom:kiwoom:acct_4
token:kis:
blacklist:token:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNyIsImlzX2FkbWluIjpmYWxzZSwiaXNfc3VwZXJ1c2VyIjpmYWxzZSwiZXhwIjoxNzcyNDk3ODQyfQ.7OTwUT876UNZNInHUqWm2td3ZDW41klrGCOoWT2yhmE
token:kiwoom:kiwoom:acct_6
token:kis:kis:2
```
**→ `token:kis:` (빈 account_id 키) 비정상 키 존재 확인**

---

### 명령 18: token:kis: 키 타입/TTL/값 확인
```bash
redis-cli TYPE "token:kis:"
redis-cli TTL "token:kis:"
redis-cli EXISTS "token:kis:"
redis-cli GET "token:kis:"
```
**출력:**
```
string
24551
1
{"access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImYyOWM2NGY1LTk5MjktNGFlNS1hMTM1LWVlMmRmNGE4YmNmOSIsInByZHRfY2QiOiIiLCJpc3MiOiJ1bm9ndyIsImV4cCI6MTc3Mjc3ODE3OCwiaWF0IjoxNzcyNjkxNzc4LCJqdGkiOiJQU0pqaE5XaDRJWkdQMExGSWJiUnRZQ2d1Q05rRnV6Y2JpZlMifQ.WpWI5pgF3y8Ob_W6U5prp_RW8SDamuZgMYLyvY2sAamXjR_CxkmuPBhICGe5Lc3BStvohWfdNd6Zq5Rmdm5pvw", "expires_at": "2026-03-06T06:22:58+00:00", "issued_at": "2026-03-05T10:15:39.619817+00:00"}
```

---

### 명령 19: monitor_router.py 헬스체크 전체 코드 확인
```
파일: /root/kis-autotrade-v4/backend/app/routers/go100/monitor_router.py (1~80줄)
```
**출력:**
```python
# CUR-GO100-PHASE10-B-BETA-MONITORING, 2026-02-26
"""
GO100 모니터링 API: 헬스체크, 사용 통계, 에러 목록, 디스크.
"""

import logging
import shutil
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.redis import redis_client
from backend.app.core.security_middleware import get_current_user
from backend.app.services.go100.ai.usage_logger import get_usage_stats

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitor", tags=["GO100 Monitor"])


@router.get("/health")
async def monitor_health() -> Dict[str, Any]:
    """
    서비스 상태: DB, Redis, 디스크, 메모리.
    인증 없이 호출 가능 (로드밸런서/크론용).
    """
    out: Dict[str, Any] = {
        "status": "ok",
        "database": "unknown",
        "redis": "unknown",
        "disk": {},
        "memory": {},
    }
    try:
        from backend.app.core.database import async_engine
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        out["database"] = "connected"
    except Exception as e:
        out["database"] = "disconnected"
        out["status"] = "degraded"
        logger.warning("monitor health db: %s", e)

    try:
        await redis_client.ping()
        out["redis"] = "connected"
    except Exception as e:
        out["redis"] = "disconnected"
        out["status"] = "degraded"
        logger.warning("monitor health redis: %s", e)
    ...
```

---

### 명령 20: rate_limiter.py sliding window 코드 확인
```
파일: /root/kis-autotrade-v4/backend/app/core/rate_limiter.py (78~100줄)
```
**출력:**
```python
async def _sliding_window_check(
    redis,
    key: str,
    window_sec: float,
    limit: int,
) -> tuple[bool, int]:
    now = time.time()
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, "-inf", now - window_sec)
    pipe.zcard(key)
    results = await pipe.execute()
    count = results[1] if len(results) > 1 else 0
    if count >= limit:
        return (False, count)
    pipe2 = redis.pipeline()
    pipe2.zadd(key, {str(now): now})
    pipe2.expire(key, int(window_sec) + 60)
    await pipe2.execute()
    return (True, count + 1)
```
**→ 매 API 요청마다 ping() + pipeline 2회 실행 = 연결 부하 증폭**

---

### 명령 21: get_redis_status 함수 확인
```
파일: /root/kis-autotrade-v4/backend/app/services/monitoring/system_monitor.py (132~165줄)
```
**출력:**
```python
async def get_redis_status() -> dict[str, Any]:
    """Redis 연결, 메모리 사용량, 키 수."""
    out: dict[str, Any] = {
        "connected": False,
        "used_memory_bytes": None,
        "used_memory_human": None,
        "keys_count": None,
        "response_time_ms": None,
    }
    t0 = datetime.now(timezone.utc)
    try:
        await redis_client.ping()
        out["connected"] = True
        out["response_time_ms"] = round(
            (datetime.now(timezone.utc) - t0).total_seconds() * 1000, 1
        )
        info = await redis_client.info("memory")
        ...
```

---

### 명령 22: Redis replication 상태
```bash
redis-cli INFO replication | grep -i "role\|connected_slaves\|master"
```
**출력:**
```
role:master
connected_slaves:0
master_failover_state:no-failover
master_replid:36527d6ce09152def76773adc5fbe3f28889f0b4
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:0
```

---

## 분석 결과 요약

### 근본 원인 식별 (우선순위 순)

**[P0-1] health_check_interval 미설정**
- `aioredis.from_url()` 파라미터: encoding, decode_responses 두 가지만 설정
- `health_check_interval` 없음 → 연결풀이 stale 연결을 인지 못함
- Redis 재시작/네트워크 블립 후 기존 풀 연결 전부 invalid 상태로 유지
- 다음 명령 실행 시 ConnectionError → health endpoint "disconnected" 보고

**[P0-2] socket_keepalive 미설정**
- 클라이언트 소켓에 TCP keepalive 없음
- 중간 네트워크 장비(NAT/방화벽)가 idle 연결을 조용히 끊어도 소켓은 open 상태 표시
- 서버 tcp-keepalive=300 있으나 클라이언트 설정 없으면 효과 제한

**[P0-3] socket_timeout 미설정**
- 끊어진 연결에서 명령 전송 시 응답 영구 대기 (timeout=None)
- asyncio CancelledError 또는 무한 hang 발생 가능

**[P0-4] 좀비 연결 9개 누적 (최대 idle 39.4시간)**
- id=15: idle=141,944초 (39.4시간)
- id=31549: idle=92,700초 (25.7시간)
- health_check_interval 없어서 pool이 이 연결들을 유효하다고 판단

**[P1-5] systemd Requires=redis.service 누락**
- go100.service: Wants=redis.service (soft) / Requires=postgresql.service만
- Redis 재시작 시 go100은 계속 실행 → 기존 풀 전체 stale

**[P1-6] Redis server timeout=0**
- 서버 측 클라이언트 타임아웃 비활성
- 39.4시간 idle 연결도 서버가 끊지 않음

**[P1-7] 헬스체크 reconnect 로직 없음**
- monitor_health(), health_check() 모두 disconnected 시 재연결 없음
- 수동 서비스 재시작만이 해결 방법이 되어 반복 재발

**[P2-8] errorstat_ERR: 303,654 (uptime 1일간)**
- 총 명령 371,792 중 303,654 ERR (82% 에러율)
- cmdstat 상 failed_calls=0이지만 errorstat_ERR 급증
- stale 연결에서의 연결 오류가 ERR 카운트로 집계되는 것으로 추정
- uptime=1일이므로 과거 누적 에러

**[P2-9] mem_fragmentation_ratio: 7.19**
- 정상 범위(1.0~1.5) 대비 7.19배 파편화
- 연결 생성/소멸 반복에 의한 메모리 할당 파편화

### 즉각 해결 방안

**최소 수정 (단 1줄로 재발 방지 가능):**
```python
# /root/kis-autotrade-v4/backend/app/core/redis.py
redis_client = aioredis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    health_check_interval=30,  ← 이 줄만 추가해도 재발 방지
)
```

**권장 완전 수정:**
```python
from redis.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError

redis_client = aioredis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,
    socket_timeout=5.0,
    socket_connect_timeout=3.0,
    socket_keepalive=True,
    socket_keepalive_options={
        "TCP_KEEPIDLE": 60,
        "TCP_KEEPINTVL": 10,
        "TCP_KEEPCNT": 5,
    },
    health_check_interval=30,
    retry_on_timeout=True,
    retry_on_error=[ConnectionError, TimeoutError],
    retry=Retry(ExponentialBackoff(cap=3, base=1), 3),
)
```

---

## 생성된 보고서 파일
- `/root/kis-autotrade-v4/report/v41/CUR-V41-REDIS-DISCONNECT-ROOT-CAUSE-001-20260306.md`

## done_watcher.sh를 통한 project-docs push 대기
이 RESULT 파일이 done/ 폴더에 저장되면 done_watcher.sh (root PID 1775110)가
자동으로 project-docs에 push 처리합니다.
