import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'

function Upload() {
  // The file the user has selected (null until they pick one).
  const [file, setFile] = useState<File | null>(null)
  // A handle to the hidden file input so the drop zone can open it.
  const inputRef = useRef<HTMLInputElement>(null)

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null)
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

            {/* Click the zone to open the file picker; shows the chosen file. */}
            <div
              onClick={() => inputRef.current?.click()}
              className="mt-6 flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-500 px-6 py-12 text-center transition hover:border-habasit"
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
              disabled={!file}
              className={`font-display mt-6 w-full rounded-lg py-3 text-lg font-bold text-white shadow-md transition duration-200 ${
                file
                  ? 'bg-habasit hover:bg-green-600'
                  : 'cursor-not-allowed bg-gray-600'
              }`}
            >
              Upload
            </button>
          </div>
        </main>
      </div>
    </div>
  )
}

export default Upload
