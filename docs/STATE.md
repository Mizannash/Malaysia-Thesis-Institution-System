# State

Store: **PostgreSQL and Redis**.

## Limits
- AI calls per person: 10 a minute.
- AI calls per customer: 5 a day (the plan limit; higher plans raise it).

## What is kept from each AI call
- The input and the result, for audit, for one year. Never in the logs.

## Keys (every key starts with the tenant)
| Key | What | Expires |
|---|---|---|
| `malaysian-thesis-institution-system-mtis:{tenant}:session:{session id}` | the conversation (Full history) | 7 days |
| `malaysian-thesis-institution-system-mtis:{tenant}:{user}:rl:{minute}` | a person's AI calls this minute (limit 10) | 60 seconds |
| `malaysian-thesis-institution-system-mtis:{tenant}:rl:{day}` | the customer's AI calls today (limit 5) | 1 day |

## Rules
- The server decides the session id from the signed-in user; never trust one the browser sends.
- Load the history into every call (Module 6: history in Redis is useless if it is not passed to the model).
- Count with one atomic step (INCR with EXPIRE in a Lua script, as in Module 6), never a separate GET and SET.
- Over a limit: refuse with a clear message and when to retry.
- If Redis is down: answer without the cache; refuse new model calls when the limiter cannot count (fail closed), because unlimited calls cost money.
