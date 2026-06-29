import { Link } from 'react-router-dom'

function Chat() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-900 px-6 text-center">
      <h1 className="font-display text-4xl font-bold text-habasit">Chat</h1>
      <p className="font-display mt-4 text-gray-300">The chat interface arrives in Step 6.</p>
      <Link
        to="/"
        className="font-display mt-8 text-gray-400 underline transition hover:text-white"
      >
        ← Back to home
      </Link>
    </div>
  )
}

export default Chat
