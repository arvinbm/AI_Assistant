// Talks to the FastAPI backend.
// During development the backend runs on port 8000; in production the frontend
// is served from the same origin, so an empty base means "same site" (Step 9).
const API_BASE = import.meta.env.DEV ? 'http://localhost:8000' : ''

export type ChatResponse = {
  answer: string
  sources: string[]
}

/** Send a question to the RAG backend and return its full answer + sources. */
export async function askQuestion(question: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })

  if (!response.ok) {
    throw new Error(`Backend returned ${response.status}`)
  }

  return response.json()
}

export type StreamHandlers = {
  onSources?: (sources: string[]) => void
  onToken: (text: string) => void
}

/**
 * Stream the answer from the backend, calling `onToken` for each piece of text
 * as it arrives (and `onSources` once with the cited documents).
 */
export async function askQuestionStream(
  question: string,
  handlers: StreamHandlers,
): Promise<void> {
  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })

  if (!response.ok || !response.body) {
    throw new Error(`Backend returned ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  // The backend sends newline-delimited JSON; read chunks and parse whole lines.
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    let newlineIndex: number
    while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
      const line = buffer.slice(0, newlineIndex).trim()
      buffer = buffer.slice(newlineIndex + 1)
      if (!line) continue

      const event = JSON.parse(line)
      if (event.type === 'sources') handlers.onSources?.(event.sources)
      else if (event.type === 'token') handlers.onToken(event.text)
    }
  }
}
