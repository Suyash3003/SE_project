import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { login } from '../../api/auth'
import { useAuth } from '../../contexts/AuthContext'

const roles = [
  { id: 'admin', title: 'Manufacturer Admin', icon: '🏭', color: 'blue' },
  { id: 'dealer', title: 'Dealer', icon: '🏪', color: 'emerald' },
  { id: 'customer', title: 'Customer', icon: '🎨', color: 'orange' },
]

export default function LoginPage() {
  const { session, saveSession } = useAuth()
  const navigate = useNavigate()
  const [role, setRole] = useState('customer')
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (session?.token) return <Navigate to={`/${session.role}`} replace />

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await login({ identifier, password, role })
      saveSession(data)
      navigate(`/${data.role}`, { replace: true })
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to sign in. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-950 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <Link to="/" className="block text-center text-3xl font-bold text-white mb-8">
          Paint<span className="text-emerald-400">Flow</span>.ai
        </Link>
        <section className="bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-2xl">
          <h1 className="text-2xl font-bold text-white">Welcome back</h1>
          <p className="text-gray-400 text-sm mt-1 mb-6">Choose your portal to continue</p>
          <div className="grid grid-cols-3 gap-2 mb-6">
            {roles.map((item) => (
              <button key={item.id} type="button" onClick={() => setRole(item.id)}
                className={`rounded-xl p-3 text-center border text-xs transition-colors ${role === item.id ? `border-${item.color}-400 bg-${item.color}-500/10 text-white` : 'border-gray-700 text-gray-400 hover:border-gray-500'}`}>
                <span className="block text-xl mb-1">{item.icon}</span>{item.title}
              </button>
            ))}
          </div>
          <form onSubmit={submit} className="space-y-4">
            <label className="block text-sm text-gray-300">Email or phone
              <input value={identifier} onChange={(e) => setIdentifier(e.target.value)} required className="mt-1 w-full rounded-lg bg-gray-800 border border-gray-700 px-3 py-2.5 text-white outline-none focus:border-emerald-400" />
            </label>
            <label className="block text-sm text-gray-300">Password
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="mt-1 w-full rounded-lg bg-gray-800 border border-gray-700 px-3 py-2.5 text-white outline-none focus:border-emerald-400" />
            </label>
            {error && <p className="text-sm text-red-400">{error}</p>}
            <button disabled={loading} className="w-full rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-gray-950 font-semibold py-2.5">
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>
          <div className="flex justify-between mt-5 text-sm">
            <Link to="/forgot-password" className="text-gray-400 hover:text-white">Forgot password?</Link>
            {role !== 'admin' && <Link to={`/register/${role}`} className="text-emerald-400 hover:text-emerald-300">Create account</Link>}
          </div>
        </section>
      </div>
    </main>
  )
}
