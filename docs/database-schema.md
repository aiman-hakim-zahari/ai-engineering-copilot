# Database Schema

PostgreSQL 16 with the `pgvector` extension. A **single shared database** serves both the C# gateway and the Python ML service.

## Service Ownership

To preserve the clean boundary described in [architecture.md](architecture.md#key-principle), table ownership is strict:

| Table             | Written by      | Read by                          |
|-------------------|-----------------|----------------------------------|
| `users`           | C# gateway only | C# gateway only                  |
| `refresh_tokens`  | C# gateway only | C# gateway only                  |
| `documents`       | C# gateway only | C# gateway + Python ML (read-only) |
| `conversations`   | C# gateway only | C# gateway only                  |
| `messages`        | C# gateway only | C# gateway only                  |
| `audit_logs`      | C# gateway only | C# gateway only                  |
| `chunks`          | Python ML only  | C# gateway (read-only) + Python ML |

The Python service never writes user/business state; the C# gateway never writes embeddings.

## Extensions

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## Tables (target shape)

### users
| Column         | Type         | Notes                          |
|----------------|--------------|--------------------------------|
| id             | uuid PK      |                                |
| email          | citext UNIQUE|                                |
| password_hash  | text         | argon2id                       |
| role           | text         | `user` \| `admin`              |
| created_at     | timestamptz  |                                |

### documents
| Column         | Type         | Notes                          |
|----------------|--------------|--------------------------------|
| id             | uuid PK      |                                |
| user_id        | uuid FK      | → users.id                     |
| filename       | text         |                                |
| mime_type      | text         |                                |
| status         | text         | `pending` / `processing` / `ready` / `failed` |
| uploaded_at    | timestamptz  |                                |

### chunks
| Column         | Type             | Notes                          |
|----------------|------------------|--------------------------------|
| id             | uuid PK          |                                |
| document_id    | uuid FK          | → documents.id                 |
| chunk_index    | int              | ordinal within document        |
| page           | int              | nullable                       |
| text           | text             |                                |
| embedding      | vector(768)      | `nomic-embed-text` dimension   |
| tsv            | tsvector         | generated from `text`          |

### conversations
| Column         | Type         | Notes                          |
|----------------|--------------|--------------------------------|
| id             | uuid PK      |                                |
| user_id        | uuid FK      | → users.id                     |
| title          | text         | auto-generated from first message, user-editable |
| created_at     | timestamptz  |                                |
| updated_at     | timestamptz  | bumped on every new message    |

### messages
| Column           | Type         | Notes                                                                  |
|------------------|--------------|------------------------------------------------------------------------|
| id               | uuid PK      |                                                                        |
| conversation_id  | uuid FK      | → conversations.id                                                     |
| role             | text         | `user` \| `assistant` \| `system`                                      |
| content          | text         | rendered answer or user prompt                                         |
| sources          | jsonb        | array of `{ document_id, chunk_id, page, score }` for assistant rows   |
| latency_ms       | int          | nullable; populated for assistant rows                                 |
| tokens_in        | int          | nullable                                                               |
| tokens_out       | int          | nullable                                                               |
| created_at       | timestamptz  |                                                                        |

### audit_logs
| Column         | Type         | Notes                                                            |
|----------------|--------------|------------------------------------------------------------------|
| id             | uuid PK      |                                                                  |
| user_id        | uuid FK      | nullable for system events                                       |
| action         | text         | e.g. `document.upload`, `chat.ask`, `auth.login`                 |
| resource_type  | text         | e.g. `document`, `conversation`                                  |
| resource_id    | uuid         | nullable                                                         |
| metadata       | jsonb        | request shape, IP, user-agent, correlation id                    |
| created_at     | timestamptz  |                                                                  |

### refresh_tokens
| Column         | Type         | Notes                          |
|----------------|--------------|--------------------------------|
| id             | uuid PK      |                                |
| user_id        | uuid FK      |                                |
| token_hash     | text         |                                |
| expires_at     | timestamptz  |                                |
| revoked_at     | timestamptz  | nullable                       |

## Indexes

- `chunks USING hnsw (embedding vector_cosine_ops)` — semantic search
- `chunks USING gin (tsv)` — lexical search
- `documents (user_id, status)` — list filters
- `conversations (user_id, updated_at DESC)` — conversation list
- `messages (conversation_id, created_at)` — message paging
- `audit_logs (user_id, created_at DESC)` — admin queries
