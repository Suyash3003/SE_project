import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { registerCustomer, registerDealer } from '../../api/auth'

export default function RegisterPage() {
  const { role = 'customer' } = useParams()
  const isDealer = role === 'dealer'
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', city: '', state: '', email: '', phone: '', password: '' })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const update = (key) => (event) => setForm({ ...form, [key]: event.target.value })
  const submit = async (event) => {
    event.preventDefault()
    setError('')
    try {
      const { data } = await (isDealer ? registerDealer(form) : registerCustomer(form))
      setMessage(data.message)
      setTimeout(() => navigate('/login'), 1200)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create your account.')
    }
  }

  return (
    <main className="min-h-screen bg-gray-950 flex items-center justify-center p-6">
      <section className="w-full max-w-md bg-gray-900 border border-gray-800 rounded-2xl p-8">
        <Link to="/login" className="text-emerald-400 text-sm">← Back to sign in</Link>
        <h1 className="text-2xl font-bold text-white mt-5">Create {isDealer ? 'dealer' : 'customer'} account</h1>
        {isDealer && <p className="text-gray-400 text-sm mt-1">Your account will be reviewed by a manufacturer admin.</p>}
        <form onSubmit={submit} className="space-y-4 mt-6">
          {isDealer && [['name', 'Business name'], ['city', 'City'], ['state', 'State']].map(([key, label]) => (
            <input key={key} value={form[key]} onChange={update(key)} placeholder={label} required className="w-full rounded-lg bg-gray-800 border border-gray-700 px-3 py-2.5 text-white" />
          ))}
          <input type="email" value={form.email} onChange={update('email')} placeholder="Email" required className="w-full rounded-lg bg-gray-800 border border-gray-700 px-3 py-2.5 text-white" />
          <input value={form.phone} onChange={update('phone')} placeholder="Phone (optional)" className="w-full rounded-lg bg-gray-800 border border-gray-700 px-3 py-2.5 text-white" />
          <input type="password" minLength="8" value={form.password} onChange={update('password')} placeholder="Password (8+ characters)" required className="w-full rounded-lg bg-gray-800 border border-gray-700 px-3 py-2.5 text-white" />
          {error && <p className="text-sm text-red-400">{error}</p>}
          {message && <p className="text-sm text-emerald-400">{message}</p>}
          <button className="w-full rounded-lg bg-emerald-500 text-gray-950 font-semibold py-2.5">Create account</button>
        </form>
      </section>
    </main>
  )
}
