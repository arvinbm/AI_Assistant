import { useNavigate } from 'react-router-dom'

function Landing() {
  const navigate = useNavigate()

  return (
    <div
      className="relative min-h-screen bg-cover bg-center"
      style={{ backgroundImage: "url('/Payvand_Background.jpg')" }}
    >
      {/* Dark overlay so the text stays readable over the photo */}
      <div className="absolute inset-0 bg-black/60" />

      {/* Left-aligned content column, vertically centered */}
      <div className="relative z-10 flex min-h-screen items-center px-8 sm:px-16 lg:px-24">
        <div className="max-w-2xl">
          <h1 className="font-display text-5xl font-extrabold leading-tight text-white sm:text-6xl">
            <span className="text-habasit"> Hello Payvand&apos;s Executives</span>
          </h1>

          <p className="font-display mt-4 text-xl font-semibold text-gray-100 sm:text-2xl">
            Your AI assistant for instant answers from your company&apos;s documents.
          </p>

          <div className="font-display mt-6 space-y-4 text-justify text-base leading-relaxed text-gray-300 sm:text-lg">
            <p>
              Ask any work question in plain language in Persian or English and
              get a clear answer drawn straight from Payvand&apos;s own documents,
              with the source cited.
            </p>
            <p>
              <span className="font-semibold text-white">Start Chatting</span> to ask
              a question, or{' '}
              <span className="font-semibold text-white">Upload Documents</span> to
              expand its knowledge base.
            </p>
          </div>

          <div className="mt-10 flex flex-col gap-8 sm:flex-row">
            <button
              type="button"
              onClick={() => navigate('/chat')}
              className="font-display w-60 rounded-lg bg-habasit py-4 text-lg font-bold text-white shadow-lg transition duration-200 hover:scale-105 hover:bg-green-600"
            >
              Start Chatting
            </button>
            <button
              type="button"
              onClick={() => navigate('/upload')}
              className="font-display w-60 rounded-lg bg-habasit py-4 text-lg font-bold text-white shadow-lg transition duration-200 hover:scale-110 hover:bg-green-600"
            >
              Upload Documents
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Landing
