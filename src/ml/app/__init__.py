"""AI Engineering Copilot — Python ML Service.

FastAPI application that owns chunking, embedding, vector search,
reranking, prompt construction, LLM inference, and the evaluation
harness. The C# application backend orchestrates calls to this
service over REST; this service is stateless with respect to
user / auth / business data.
"""

__version__ = "0.1.0"
