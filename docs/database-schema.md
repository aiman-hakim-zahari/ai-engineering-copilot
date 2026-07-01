# Database Schema

There is no database schema in the implemented demo.

The Python ML service stores document chunks in memory so the full stack can run
without PostgreSQL, pgvector, migrations, or seed data.

## Future PostgreSQL Shape

A later version could add:

- `documents` for uploaded document metadata
- `chunks` for text chunks and vector embeddings
- `conversations` and `messages` for persisted chat history
- `sources` metadata stored with assistant answers

That future schema should be added only when persistence is implemented.
