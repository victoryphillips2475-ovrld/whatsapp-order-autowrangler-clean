# TypeScript + Hono Pattern — OVERLORD Empire Standard

## Project Structure
```
project/
├── src/
│   ├── index.ts         ← app entry point
│   ├── routes/
│   │   └── users.ts     ← one file per domain
│   ├── services/
│   │   └── users.ts     ← business logic
│   ├── models/
│   │   └── users.ts     ← Zod schemas + TypeScript types
│   └── middleware/
│       └── auth.ts      ← auth middleware
├── package.json
├── tsconfig.json
└── .env
```

## package.json
```json
{
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "hono": "^4.6.0",
    "@hono/node-server": "^1.13.0",
    "zod": "^3.23.0",
    "dotenv": "^16.4.0"
  },
  "devDependencies": {
    "typescript": "^5.6.0",
    "tsx": "^4.19.0",
    "@types/node": "^22.0.0"
  }
}
```

## Hono Entry Point
```typescript
import { serve } from '@hono/node-server'
import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { usersRouter } from './routes/users'

const app = new Hono()

app.use('*', logger())
app.use('*', cors({
  origin: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
}))

app.get('/health', (c) => c.json({ status: 'ok' }))
app.route('/users', usersRouter)

serve({ fetch: app.fetch, port: Number(process.env.PORT) || 3000 })
```

## Models — Zod First
```typescript
import { z } from 'zod'

export const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
})

export const UserResponseSchema = z.object({
  id: z.string(),
  email: z.string(),
  name: z.string(),
  createdAt: z.string().datetime(),
})

export type CreateUserInput = z.infer<typeof CreateUserSchema>
export type UserResponse = z.infer<typeof UserResponseSchema>
```

## Route Pattern
```typescript
import { Hono } from 'hono'
import { zValidator } from '@hono/zod-validator'
import { CreateUserSchema } from '../models/users'
import { UserService } from '../services/users'

export const usersRouter = new Hono()

usersRouter.post('/', zValidator('json', CreateUserSchema), async (c) => {
  const payload = c.req.valid('json')
  try {
    const user = await UserService.create(payload)
    return c.json(user, 201)
  } catch (err) {
    if (err instanceof Error && err.message.includes('already exists')) {
      return c.json({ error: err.message }, 409)
    }
    return c.json({ error: 'Internal error' }, 500)
  }
})
```

## Async HTTP — fetch with AbortSignal
```typescript
async function callExternal(url: string, payload: unknown): Promise<unknown> {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.API_KEY}`,
    },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(30_000),
  })

  if (!response.ok) {
    throw new Error(`External call failed: ${response.status}`)
  }

  return response.json()
}
```

## tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "strict": true,
    "noImplicitAny": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
```

## NEVER
- Never use any type — define proper interfaces or use unknown
- Never use fetch() without AbortSignal.timeout()
- Never use var — const or let only
- Never suppress TypeScript errors with @ts-ignore unless absolutely necessary