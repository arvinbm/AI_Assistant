import { Link } from 'react-router-dom'

function Upload() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-900 px-6 text-center">
      <h1 className="font-display text-4xl font-bold text-habasit">Upload Documents</h1>
      <p className="font-display mt-4 text-gray-300">The upload panel arrives in Step 7.</p>
      <Link
        to="/"
        className="font-display mt-8 text-gray-400 underline transition hover:text-white"
      >
        ← Back to home
      </Link>
    </div>
  )
}

export default Upload
