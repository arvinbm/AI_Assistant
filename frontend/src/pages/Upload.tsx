import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { uploadDocument, type UploadResult } from '../api'

function Upload() {
  // The selected file, the in-flight state, and the result/error of an upload.
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [result, setResult] = useState<UploadResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  // A handle to the hidden file input so the drop zone can open it.
  const inputRef = useRef<HTMLInputElement>(null)

  // Select a file (from the picker or a drop) and clear any previous result.
  function selectFile(selected: File | null) {
    setFile(selected)
    setResult(null)
    setError(null)
  }

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    selectFile(event.target.files?.[0] ?? null)
  }

  function handleDrop(event: React.DragEvent) {
    event.preventDefault()
    setIsDragging(false)
    selectFile(event.dataTransfer.files?.[0] ?? null)
  }

  async function handleUpload() {
    if (!file || isUploading) return
    setIsUploading(true)
    setResult(null)
    setError(null)
    try {
      const data = await uploadDocument(file)
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div
      className="relative min-h-screen bg-cover bg-center"
      style={{ backgroundImage: "url('/Payvand_Background.jpg')" }}
    >
      {/* Same dark overlay as the other pages */}
      <div className="absolute inset-0 bg-black/60" />

      <div className="relative z-10 flex min-h-screen flex-col">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 sm:px-10">
          <h1 className="font-display text-2xl font-bold text-habasit">
            Payvand AI Assistant
          </h1>
          <Link
            to="/"
            className="font-display rounded-lg bg-gray-700 px-5 py-2.5 text-sm font-bold text-white shadow-md transition duration-200 hover:bg-gray-600"
          >
            Back to Home
          </Link>
        </header>

        {/* Centered upload panel */}
        <main className="flex flex-1 items-center justify-center px-4 py-10">
          <div className="w-full max-w-lg rounded-2xl bg-gray-900/70 p-8 shadow-xl">
            <h2 className="font-display text-center text-3xl font-bold text-white">
              Upload Documents
            </h2>
            <p className="font-display mt-2 text-center text-gray-300">
              Add a PDF to the assistant&apos;s knowledge base.
            </p>

            {/* Hidden file input, opened by clicking the zone below. */}
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
              className="hidden"
            />

            {/* Click to open the picker, or drag a file onto the zone. */}
            <div
              onClick={() => inputRef.current?.click()}
              onDragOver={(event) => {
                event.preventDefault()
                setIsDragging(true)
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              className={`mt-6 flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-12 text-center transition ${
                isDragging
                  ? 'border-habasit bg-habasit/10'
                  : 'border-gray-500 hover:border-habasit'
              }`}
            >
              {file ? (
                <p className="font-display font-semibold break-all text-white">
                  {file.name}
                </p>
              ) : (
                <>
                  <p className="font-display text-gray-300">
                    Drag a file here, or click to choose
                  </p>
                  <p className="font-display mt-1 text-sm text-gray-500">
                    PDF files
                  </p>
                </>
              )}
            </div>

            {/* Upload button — enabled only once a file is selected. */}
            <button
              type="button"
              onClick={handleUpload}
              disabled={!file || isUploading}
              className={`font-display mt-6 w-full rounded-lg py-3 text-lg font-bold text-white shadow-md transition duration-200 ${
                file && !isUploading
                  ? 'bg-habasit hover:bg-green-600'
                  : 'cursor-not-allowed bg-gray-600'
              }`}
            >
              {isUploading ? 'Uploading…' : 'Upload'}
            </button>

            {/* Result / error message */}
            {result?.status === 'ingested' && (
              <p className="font-display mt-4 rounded-lg bg-green-900/50 px-4 py-3 text-center text-green-200">
                ✓ Added <span className="font-semibold break-all">{result.filename}</span>{' '}
                to the knowledge base ({result.chunks} chunks).
              </p>
            )}
            {result?.status === 'skipped' && (
              <p className="font-display mt-4 rounded-lg bg-amber-900/50 px-4 py-3 text-center text-amber-200">
                ⚠ Skipped <span className="font-semibold break-all">{result.filename}</span> — {result.reason}.
              </p>
            )}
            {error && (
              <p className="font-display mt-4 rounded-lg bg-red-900/50 px-4 py-3 text-center text-red-200">
                {error}
              </p>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

export default Upload
