import { useState } from 'react'
import { Link } from 'react-router-dom'
import { requestPasswordReset } from '../../api/auth'

export default function ForgotPasswordPage() {
  const [identifier, setIdentifier] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    try {
      const { data } = await requestPasswordReset(identifier)
      setMessage(data.reset_token ? `${data.message} Development reset token: ${data.reset_token}` : data.message)
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to process the request.')
    }
  }

  return (
    <main className="min-h-screen bg-gray-950 flex items-center justify-center p-6">
      <section className="w-full max-w-md bg-gray-900 border border-gray-800 rounded-2xl p-8">
        <Link to="/login" className="text-emerald-400 text-sm">← Back to sign in</Link>
        <h1 className="text-2xl font-bold text-white mt-5">Reset your password</h1>
        <p className="text-gray-400 text-sm mt-1 mb-6">Enter the email or phone associated with your account.</p>
        <form onSubmit={submit} className="space-y-4">
          <input value={identifier} onChange={(e) => setIdentifier(e.target.value)} required placeholder="Email or phone" className="w-full rounded-lg bg-gray-800 border border-gray-700 px-3 py-2.5 text-white" />
          {error && <p className="text-sm text-red-400">{error}</p>}
          {message && <p className="text-sm text-emerald-400 break-words">{message}</p>}
          <button className="w-full rounded-lg bg-emerald-500 text-gray-950 font-semibold py-2.5">Request reset</button>
        </form>
      </section>
    </main>
  )
}
