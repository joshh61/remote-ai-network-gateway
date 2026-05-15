"""FastAPI server for the Secure Mobile AI Assistant Gateway project.

Run with:
    uvicorn server.app:app --host 0.0.0.0 --port 8080

Then open from the Mac:
    http://127.0.0.1:8080/chat

Or from an iPhone on the same Wi-Fi:
    http://<MAC_LAN_IP>:8080/chat
"""

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from server.anthropic_client import AnthropicBackend

load_dotenv()

app = FastAPI(
    title="Secure Mobile AI Assistant Gateway",
    description="Computer Networks final project: iPhone client -> local FastAPI gateway -> Anthropic API.",
    version="1.0.0",
)

backend: AnthropicBackend | None = None
request_history: list[dict] = []


class AskRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class AskResponse(BaseModel):
    response: str
    client_ip: str
    timestamp_utc: str
    network_path: str


def get_backend() -> AnthropicBackend:
    global backend
    if backend is None:
        backend = AnthropicBackend()
    return backend


def require_token(authorization: str | None) -> None:
    expected_token = os.getenv("AI_GATEWAY_TOKEN", "class-demo-token")
    expected_header = f"Bearer {expected_token}"
    if authorization != expected_header:
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token")


@app.get("/")
def root() -> dict:
    return {
        "project": "Secure Mobile AI Assistant Gateway",
        "status": "running",
        "try": "/chat for browser demo or /docs for API docs",
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "ai-gateway",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/ask", response_model=AskResponse)
def ask_ai(
    body: AskRequest,
    request: Request,
    authorization: str | None = Header(default=None),
) -> AskResponse:
    require_token(authorization)

    client_ip = request.client.host if request.client else "unknown"
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        answer = get_backend().ask(body.message)
    except Exception as exc:
        # Return a JSON error so the browser demo can display the problem clearly.
        raise HTTPException(status_code=502, detail=f"AI backend error: {exc}") from exc

    request_history.append(
        {
            "timestamp_utc": timestamp,
            "client_ip": client_ip,
            "message_length": len(body.message),
        }
    )

    return AskResponse(
        response=answer,
        client_ip=client_ip,
        timestamp_utc=timestamp,
        network_path="client -> HTTP/TCP port 8080 -> FastAPI gateway -> HTTPS/TCP 443 -> Anthropic API",
    )


@app.get("/history")
def history(authorization: str | None = Header(default=None)) -> dict:
    require_token(authorization)
    return {"count": len(request_history), "requests": request_history[-10:]}


@app.get("/chat", response_class=HTMLResponse)
def chat_page() -> str:
    """Simple browser UI for demoing from iPhone Safari."""
    return """
<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Mobile AI Gateway</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 24px; background: #101827; color: #f5f7fb; }
    .card { max-width: 760px; margin: auto; background: #172033; border: 1px solid #2f3b52; border-radius: 16px; padding: 20px; }
    textarea, input, button { width: 100%; box-sizing: border-box; font-size: 16px; border-radius: 10px; border: 1px solid #3d4b66; padding: 12px; margin-top: 8px; }
    textarea, input { background: #0f1726; color: #f5f7fb; }
    button { background: #66d9ef; color: #08111f; font-weight: 700; cursor: pointer; }
    pre { white-space: pre-wrap; background: #0f1726; padding: 14px; border-radius: 10px; border: 1px solid #2f3b52; }
    .small { color: #a7b1c2; font-size: 14px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Secure Mobile AI Assistant Gateway</h1>
    <p class="small">iPhone/browser client → HTTP over TCP port 8080 → Mac FastAPI gateway → Anthropic HTTPS API</p>

    <label>Bearer token</label>
    <input id="token" value="class-demo-token" />

    <label>Message</label>
    <textarea id="message" rows="5">Explain TCP in two sentences.</textarea>

    <button onclick="ask()">Send to AI Gateway</button>

    <h2>Response</h2>
    <pre id="output">Waiting...</pre>
  </div>

<script>
async function ask() {
  const output = document.getElementById('output');
  output.textContent = 'Sending request over HTTP/TCP...';
  try {
    const res = await fetch('/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + document.getElementById('token').value
      },
      body: JSON.stringify({ message: document.getElementById('message').value })
    });
    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch (parseErr) {
      throw new Error('Server returned non-JSON response: ' + text.slice(0, 300));
    }
    if (!res.ok) {
      throw new Error(data.detail || JSON.stringify(data));
    }
    output.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    output.textContent = 'Error: ' + err;
  }
}
</script>
</body>
</html>
    """
