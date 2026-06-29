import { Link } from 'react-router-dom'

function Chat() {
  return (
    <div
      className="relative min-h-screen bg-cover bg-center"
      style={{ backgroundImage: "url('/Payvand_Background.jpg')" }}
    >
      {/* Dark Overlay */}
      <div className="absolute inset-0 bg-black/60" />

      {/* Foreground: a full-height column — header, thread, input bar */}
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

        {/* Message thread (scrolls when it overflows) */}
        <main className="flex-1 overflow-y-auto px-4 sm:px-10">
          <div className="mx-auto max-w-3xl space-y-4 py-6">
            {/* Sample messages — placeholders to show the styling (Step 6.2 makes them real) */}
            <div className="flex justify-end">
              <div className="font-display max-w-[80%] rounded-2xl bg-habasit px-4 py-3 text-white shadow-md">
                What belts do we supply to Donya Mes?
              </div>
            </div>
            <div className="flex justify-start">
              <div className="font-display max-w-[80%] rounded-2xl bg-gray-800/90 px-4 py-3 text-gray-100 shadow-md">
                The assistant&apos;s answer will appear here, drawn from your
                documents with the sources cited.
              </div>
            </div>
          </div>
        </main>

        {/* Input bar pinned to the bottom */}
        <footer className="px-4 pb-6 sm:px-10">
          <div className="mx-auto flex max-w-3xl items-center gap-3">
            <input
              type="text"
              placeholder="Ask a question…"
              className="font-display flex-1 rounded-lg border border-gray-600 bg-gray-900/80 px-4 py-3 text-white placeholder:text-gray-400 focus:border-habasit focus:outline-none"
            />
            <button
              type="button"
              className="font-display rounded-lg bg-habasit px-6 py-3 font-bold text-white transition duration-200 hover:bg-green-600"
            >
              Send
            </button>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default Chat
