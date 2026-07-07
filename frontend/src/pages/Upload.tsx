import { Link } from 'react-router-dom'

function Upload() {
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

            {/* Drop / pick zone (static for now — wired up in 7.2) */}
            <div className="mt-6 flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-500 px-6 py-12 text-center">
              <p className="font-display text-gray-300">
                Drag a file here, or click to choose
              </p>
              <p className="font-display mt-1 text-sm text-gray-500">PDF files</p>
            </div>

            {/* Upload button (inert for now) */}
            <button
              type="button"
              className="font-display mt-6 w-full rounded-lg bg-habasit py-3 text-lg font-bold text-white shadow-md transition duration-200 hover:bg-green-600"
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
