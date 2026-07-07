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
