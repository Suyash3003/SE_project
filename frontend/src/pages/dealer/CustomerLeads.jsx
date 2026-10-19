import { useState, useEffect } from 'react'
import {
  UserIcon, PhoneIcon, CheckCircleIcon,
  XCircleIcon, ChatBubbleLeftEllipsisIcon,
} from '@heroicons/react/24/outline'
import AlertBadge from '../../components/common/AlertBadge'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { fetchCustomerRequests, updateCustomerRequestStatus } from '../../api/dealer'
import { useAuth } from '../../contexts/AuthContext'
import { formatDate } from '../../utils/formatters'

const STATUS_ACTIONS = [
  { value: 'contacted', label: 'Mark Contacted', icon: ChatBubbleLeftEllipsisIcon, color: 'blue' },
  { value: 'fulfilled', label: 'Mark Fulfilled', icon: CheckCircleIcon, color: 'emerald' },
  { value: 'cancelled', label: 'Cancel', icon: XCircleIcon, color: 'red' },
]

export default function CustomerLeads() {
  const { session } = useAuth()
  const dealerId = session?.dealerId || 1
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(null)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    setError(null)
    fetchCustomerRequests(dealerId)
      .then(r => setRequests(r.data))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load customer leads'))
      .finally(() => setLoading(false))
  }, [dealerId])

  const handleStatusUpdate = async (requestId, newStatus) => {
    setUpdating(requestId)
    try {
      await updateCustomerRequestStatus(dealerId, requestId, newStatus)
      setRequests(prev =>
        prev.map(r => r.id === requestId ? { ...r, status: newStatus } : r)
      )
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update status')
    } finally {
      setUpdating(null)
    }
  }

  if (loading) return <LoadingSpinner />

  const filtered = filter === 'all'
    ? requests
    : requests.filter(r => r.status === filter)

  const counts = {
    all: requests.length,
    requested: requests.filter(r => r.status === 'requested').length,
    contacted: requests.filter(r => r.status === 'contacted').length,
    fulfilled: requests.filter(r => r.status === 'fulfilled').length,
    cancelled: requests.filter(r => r.status === 'cancelled').length,
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Customer Leads</h1>
        <p className="text-sm text-gray-500 mt-1">
          Manage customer order requests and enquiries
        </p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-xl text-sm">
          {error}
        </div>
      )}

      {/* Filter tabs */}
      <div className="flex gap-2 flex-wrap">
        {Object.entries(counts).map(([key, count]) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filter === key
                ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700 border border-gray-700'
            }`}
          >
            {key === 'all' ? 'All' : key.charAt(0).toUpperCase() + key.slice(1)}
            <span className="ml-2 text-xs opacity-70">({count})</span>
          </button>
        ))}
      </div>

      {/* Leads list */}
      {filtered.length === 0 ? (
        <div className="glass rounded-xl p-10 border border-gray-800 text-center">
          <UserIcon className="w-10 h-10 mx-auto text-gray-600 mb-3" />
          <p className="text-gray-500 text-sm">No customer leads found</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(req => (
            <div
              key={req.id}
              className="glass rounded-xl p-5 border border-gray-800 hover:border-gray-700 transition-all"
            >
              <div className="flex flex-col md:flex-row md:items-center gap-4">
                {/* Customer & shade info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <div
                      className="w-8 h-8 rounded-lg border border-gray-700 shadow-inner flex-shrink-0"
                      style={{ backgroundColor: req.hex_color || '#000' }}
                    />
                    <div>
                      <h3 className="text-white font-medium text-sm">
                        {req.shade_name}
                        <span className="text-gray-500 text-xs ml-2">{req.shade_code}</span>
                      </h3>
                      <p className="text-gray-500 text-xs">{req.product_name} · {req.size_preference}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    <span className="flex items-center gap-1">
                      <UserIcon className="w-3.5 h-3.5" />
                      {req.customer_name}
                    </span>
                    <span className="flex items-center gap-1">
                      <PhoneIcon className="w-3.5 h-3.5" />
                      {req.customer_phone}
                    </span>
                    {req.created_at && (
                      <span className="text-gray-600">{formatDate(req.created_at)}</span>
                    )}
                  </div>
                </div>

                {/* Status + Actions */}
                <div className="flex items-center gap-3 flex-shrink-0">
                  <AlertBadge status={req.status} />
                  {req.status !== 'fulfilled' && req.status !== 'cancelled' && (
                    <div className="flex gap-1.5">
                      {STATUS_ACTIONS.filter(a => a.value !== req.status).map(action => (
                        <button
                          key={action.value}
                          disabled={updating === req.id}
                          onClick={() => handleStatusUpdate(req.id, action.value)}
                          className={`p-1.5 rounded-lg transition-all border text-xs disabled:opacity-50 ${
                            action.color === 'emerald'
                              ? 'border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10'
                              : action.color === 'blue'
                              ? 'border-blue-500/30 text-blue-400 hover:bg-blue-500/10'
                              : 'border-red-500/30 text-red-400 hover:bg-red-500/10'
                          }`}
                          title={action.label}
                        >
                          <action.icon className="w-4 h-4" />
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
