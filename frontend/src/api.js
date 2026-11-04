const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(
  /\/$/,
);

export async function apiRequest(path, { token, ...options } = {}) {
  const headers = new Headers(options.headers || {});
  if (typeof options.body === "string" && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const body = await response.text();
    let message = body || `HTTP ${response.status}`;
    try {
      const parsed = JSON.parse(body);
      message = typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail || parsed);
    } catch {
      // The response body is not JSON; show the original text below.
    }
    throw new Error(`${response.status}: ${message}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

export async function* streamMessage({ sessionId, content, token, signal }) {
  const headers = new Headers({ "Content-Type": "application/json" });
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_URL}/api/v1/sessions/${sessionId}/messages/stream`, {
    method: "POST",
    headers,
    body: JSON.stringify({ content, stream_options: {} }),
    signal,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status}: ${body || response.statusText}`);
  }
  if (!response.body) throw new Error("Сервер не вернул потоковый ответ.");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      buffer = buffer.replace(/\r\n/g, "\n");
      let boundary = buffer.indexOf("\n\n");
      while (boundary !== -1) {
        const block = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        const event = { type: "message", data: [] };
        for (const line of block.split("\n")) {
          if (line.startsWith("event:")) event.type = line.slice(6).trim();
          if (line.startsWith("data:")) event.data.push(line.slice(5).replace(/^ /, ""));
        }
        if (event.data.length) yield { type: event.type, data: event.data.join("\n") };
        boundary = buffer.indexOf("\n\n");
      }
      if (done) break;
    }
  } finally {
    reader.releaseLock();
  }
}
