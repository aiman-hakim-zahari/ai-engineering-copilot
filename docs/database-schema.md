# Database Schema

PostgreSQL 16 with the `pgvector` extension.

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
