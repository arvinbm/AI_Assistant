import { useState } from 'react'
import { Link } from 'react-router-dom'

type Message = {
  role: 'user' | 'assistant'
  text: string
}

function Chat() {
  // The conversation so far, and the current text in the input box.
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')

  function handleSend(event: React.SyntheticEvent) {
    event.preventDefault() // stop the form from reloading the page
    const question = input.trim()
    if (!question) return // ignore empty sends

    setMessages((prev) => [...prev, { role: 'user', text: question }])
    setInput('') // clear the box
  }

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
            {messages.length === 0 ? (
              <p className="font-display mt-20 text-center text-gray-400">
                Ask a question to get started.
              </p>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`font-display max-w-[80%] rounded-2xl px-4 py-3 shadow-md ${
                      message.role === 'user'
                        ? 'bg-habasit text-white'
                        : 'bg-gray-800/90 text-gray-100'
                    }`}
                  >
                    {message.text}
                  </div>
                </div>
              ))
            )}
          </div>
        </main>

        {/* Input bar pinned to the bottom */}
        <footer className="px-4 pb-6 sm:px-10">
          <form
            onSubmit={handleSend}
            className="mx-auto flex max-w-3xl items-center gap-3"
          >
            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask a question…"
              className="font-display flex-1 rounded-lg border border-gray-600 bg-gray-900/80 px-4 py-3 text-white placeholder:text-gray-400 focus:border-habasit focus:outline-none"
            />
            <button
              type="submit"
              className="font-display rounded-lg bg-habasit px-6 py-3 font-bold text-white transition duration-200 hover:bg-green-600"
            >
              Send
            </button>
          </form>
        </footer>
      </div>
    </div>
  )
}

export default Chat
