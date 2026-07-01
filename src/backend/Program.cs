using System.Net.Http.Json;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var allowedOrigins = (builder.Configuration["ALLOWED_ORIGINS"] ?? "http://localhost:3000")
    .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

builder.Services.AddCors(options =>
{
    options.AddPolicy("Frontend", policy =>
    {
        policy.WithOrigins(allowedOrigins)
            .AllowAnyHeader()
            .AllowAnyMethod();
    });
});

var mlServiceBaseUrl = builder.Configuration["ML_SERVICE_BASE_URL"]
    ?? builder.Configuration["MlService:BaseUrl"]
    ?? "http://localhost:8001";

builder.Services.AddHttpClient("MlService", client =>
{
    client.BaseAddress = new Uri(mlServiceBaseUrl);
    client.Timeout = TimeSpan.FromSeconds(20);
});

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();
app.UseCors("Frontend");

app.MapGet("/health", () => Results.Ok(new HealthResponse("ok", "gateway")))
    .WithName("Health")
    .WithOpenApi();

app.MapPost("/documents", async (
        HttpRequest request,
        IHttpClientFactory httpClientFactory,
        CancellationToken cancellationToken) =>
    {
        var document = await ReadDocumentRequestAsync(request, cancellationToken);
        if (!document.IsValid)
        {
            return Results.ValidationProblem(new Dictionary<string, string[]>
            {
                [document.Field ?? "text"] = [document.Error ?? "Document text is required."],
            });
        }

        var client = httpClientFactory.CreateClient("MlService");

        try
        {
            var response = await client.PostAsJsonAsync(
                "/ingest",
                new MlIngestRequest(document.Text!, document.Source!),
                cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                return Results.Problem(
                    title: "ML service ingest failed.",
                    detail: await ReadResponseDetailAsync(response, cancellationToken),
                    statusCode: StatusCodes.Status502BadGateway);
            }

            var payload = await response.Content.ReadFromJsonAsync<IngestResponse>(
                cancellationToken: cancellationToken);
            return payload is null
                ? Results.Problem("ML service returned an empty ingest response.", statusCode: 502)
                : Results.Ok(payload);
        }
        catch (Exception ex) when (IsMlUnavailable(ex))
        {
            return Results.Problem(
                title: "ML service is unavailable.",
                detail: "Start the Python FastAPI service and try again.",
                statusCode: StatusCodes.Status503ServiceUnavailable);
        }
    })
    .Accepts<DocumentRequest>("application/json", "multipart/form-data")
    .Produces<IngestResponse>()
    .ProducesValidationProblem()
    .ProducesProblem(StatusCodes.Status502BadGateway)
    .ProducesProblem(StatusCodes.Status503ServiceUnavailable)
    .WithName("IngestDocument")
    .WithOpenApi();

app.MapPost("/chat", async (
        ChatRequest request,
        IHttpClientFactory httpClientFactory,
        CancellationToken cancellationToken) =>
    {
        if (string.IsNullOrWhiteSpace(request.Question))
        {
            return Results.ValidationProblem(new Dictionary<string, string[]>
            {
                [nameof(request.Question)] = ["Question is required."],
            });
        }

        var client = httpClientFactory.CreateClient("MlService");

        try
        {
            var response = await client.PostAsJsonAsync(
                "/answer",
                new MlAnswerRequest(request.Question.Trim(), request.TopK),
                cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                return Results.Problem(
                    title: "ML service answer failed.",
                    detail: await ReadResponseDetailAsync(response, cancellationToken),
                    statusCode: StatusCodes.Status502BadGateway);
            }

            var payload = await response.Content.ReadFromJsonAsync<ChatResponse>(
                cancellationToken: cancellationToken);
            return payload is null
                ? Results.Problem("ML service returned an empty chat response.", statusCode: 502)
                : Results.Ok(payload);
        }
        catch (Exception ex) when (IsMlUnavailable(ex))
        {
            return Results.Problem(
                title: "ML service is unavailable.",
                detail: "Start the Python FastAPI service and try again.",
                statusCode: StatusCodes.Status503ServiceUnavailable);
        }
    })
    .Produces<ChatResponse>()
    .ProducesValidationProblem()
    .ProducesProblem(StatusCodes.Status502BadGateway)
    .ProducesProblem(StatusCodes.Status503ServiceUnavailable)
    .WithName("Chat")
    .WithOpenApi();

app.Run();

static async Task<DocumentReadResult> ReadDocumentRequestAsync(
    HttpRequest request,
    CancellationToken cancellationToken)
{
    if (request.HasFormContentType)
    {
        var form = await request.ReadFormAsync(cancellationToken);
        var source = form["source"].ToString();
        var text = form["text"].ToString();
        var file = form.Files.GetFile("file") ?? form.Files.FirstOrDefault();

        if (file is not null)
        {
            var extension = Path.GetExtension(file.FileName).ToLowerInvariant();
            if (extension is not ".txt" and not ".md" and not ".markdown")
            {
                return DocumentReadResult.Invalid(
                    "file",
                    "Only .txt, .md, and .markdown files are supported in this demo.");
            }

            await using var stream = file.OpenReadStream();
            using var reader = new StreamReader(stream);
            text = await reader.ReadToEndAsync(cancellationToken);
            source = string.IsNullOrWhiteSpace(source) ? file.FileName : source;
        }

        return BuildDocumentResult(text, source);
    }

    var body = await request.ReadFromJsonAsync<DocumentRequest>(cancellationToken);
    return BuildDocumentResult(body?.Text, body?.Source);
}

static DocumentReadResult BuildDocumentResult(string? text, string? source)
{
    if (string.IsNullOrWhiteSpace(text))
    {
        return DocumentReadResult.Invalid("text", "Document text is required.");
    }

    const int maxDocumentCharacters = 200_000;
    if (text.Length > maxDocumentCharacters)
    {
        return DocumentReadResult.Invalid(
            "text",
            $"Document text must be {maxDocumentCharacters:N0} characters or fewer.");
    }

    return DocumentReadResult.Valid(text.Trim(), string.IsNullOrWhiteSpace(source) ? "document" : source.Trim());
}

static async Task<string> ReadResponseDetailAsync(
    HttpResponseMessage response,
    CancellationToken cancellationToken)
{
    var content = await response.Content.ReadAsStringAsync(cancellationToken);
    return string.IsNullOrWhiteSpace(content)
        ? $"ML service returned {(int)response.StatusCode} {response.ReasonPhrase}."
        : content;
}

static bool IsMlUnavailable(Exception exception) =>
    exception is HttpRequestException or TaskCanceledException;

record HealthResponse(string Status, string Service);

record DocumentRequest(string Text, string? Source);

record ChatRequest(string Question, int TopK = 4);

record MlIngestRequest(
    [property: JsonPropertyName("text")] string Text,
    [property: JsonPropertyName("source")] string Source);

record MlAnswerRequest(
    [property: JsonPropertyName("question")] string Question,
    [property: JsonPropertyName("top_k")] int TopK);

record IngestResponse(
    [property: JsonPropertyName("document_id")] string DocumentId,
    [property: JsonPropertyName("chunks_indexed")] int ChunksIndexed,
    [property: JsonPropertyName("sources")] IReadOnlyList<string> Sources);

record ChatResponse(
    [property: JsonPropertyName("answer")] string Answer,
    [property: JsonPropertyName("sources")] IReadOnlyList<SourceResponse> Sources,
    [property: JsonPropertyName("matched_chunks")] IReadOnlyList<MatchedChunkResponse> MatchedChunks);

record SourceResponse(
    [property: JsonPropertyName("source")] string Source,
    [property: JsonPropertyName("chunk_id")] string ChunkId,
    [property: JsonPropertyName("score")] double Score);

record MatchedChunkResponse(
    [property: JsonPropertyName("source")] string Source,
    [property: JsonPropertyName("chunk_id")] string ChunkId,
    [property: JsonPropertyName("score")] double Score,
    [property: JsonPropertyName("text")] string Text);

record DocumentReadResult(bool IsValid, string? Text, string? Source, string? Field, string? Error)
{
    public static DocumentReadResult Valid(string text, string source) =>
        new(true, text, source, null, null);

    public static DocumentReadResult Invalid(string field, string error) =>
        new(false, null, null, field, error);
}
