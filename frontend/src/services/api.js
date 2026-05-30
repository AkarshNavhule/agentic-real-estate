const API_BASE_URL = 'http://localhost:8000/api/v1';

export async function* sendChatMessageStream(message, sessionId = null) {
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  // Extract the session ID from custom response headers
  const returnedSessionId = response.headers.get('X-Session-ID');

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Decode the binary chunk into text
      const token = decoder.decode(value, { stream: true });

      // Yield both the token and the session ID back to the component
      yield { token, sessionId: returnedSessionId };
    }
  } finally {
    reader.releaseLock();
  }
}