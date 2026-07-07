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

export type UploadResult = {
  status: 'ingested' | 'skipped'
  filename: string
  chunks?: number // present when ingested
  reason?: string // present when skipped
}

/** Upload a document to be ingested into the knowledge base. */
export async function uploadDocument(file: File): Promise<UploadResult> {
  // Files are sent as multipart/form-data; the field name "file" must match the
  // FastAPI endpoint's parameter. Do NOT set Content-Type — the browser adds the
  // multipart boundary automatically.
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    // The backend returns 400 with { detail: "..." } for unsupported types.
    let message = `Upload failed (${response.status})`
    try {
      const data = await response.json()
      if (data?.detail) message = data.detail
    } catch {
      // response wasn't JSON — keep the generic message
    }
    throw new Error(message)
  }

  return response.json()
}
