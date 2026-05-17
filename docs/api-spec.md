# API Specification

Base URL: `http://localhost:5000`
Auth: Bearer JWT (issued by `POST /auth/login`)

Endpoints are documented here in addition to the live OpenAPI spec at `/swagger`.

## Auth

| Method | Path             | Description                              |
|--------|------------------|------------------------------------------|
| POST   | `/auth/register` | Create a new user account                |
| POST   | `/auth/login`    | Exchange credentials for a JWT pair      |
| POST   | `/auth/refresh`  | Rotate an access token via refresh token |

## Documents

| Method | Path                    | Description                                  |
|--------|-------------------------|----------------------------------------------|
| POST   | `/documents`            | Upload a document (multipart/form-data)      |
| GET    | `/documents`            | List user's documents                        |
| GET    | `/documents/{id}`       | Get document metadata + processing status    |
| DELETE | `/documents/{id}`       | Soft-delete a document and its embeddings    |

## Chat / Search

| Method | Path                    | Description                                  |
|--------|-------------------------|----------------------------------------------|
| POST   | `/chat`                 | Ask a question; server-sent event response   |
| POST   | `/search`               | Hybrid semantic + keyword search             |

## Admin

| Method | Path                    | Description                                  |
|--------|-------------------------|----------------------------------------------|
| GET    | `/admin/metrics`        | Ingestion + embedding throughput stats       |
| GET    | `/admin/users`          | List users (role: admin)                     |

_Request and response schemas are defined alongside controllers and exposed via Swagger._
