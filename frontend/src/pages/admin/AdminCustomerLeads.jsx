import { useState, useEffect } from 'react'
import { UserIcon } from '@heroicons/react/24/outline'
import DataTable from '../../components/common/DataTable'
import AlertBadge from '../../components/common/AlertBadge'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { fetchAdminCustomerRequests } from '../../api/admin'
import { formatDate } from '../../utils/formatters'

export default function AdminCustomerLeads() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    setError(null)
    fetchAdminCustomerRequests()
      .then(r => setRequests(r.data))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load customer leads'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner text="Loading customer leads..." />

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

  const columns = [
    {
      key: 'id',
      label: 'ID',
      render: v => <span className="font-mono text-gray-400">#{v}</span>,
    },
    {
      key: 'customer_name',
      label: 'Customer',
      render: (v, row) => (
        <div>
          <span className="text-white text-sm">{v}</span>
          <span className="block text-xs text-gray-500">{row.customer_phone}</span>
        </div>
      ),
    },
    {
      key: 'shade_name',
      label: 'Shade',
      render: (v, row) => (
        <div className="flex items-center gap-2">
          <span
            className="w-4 h-4 rounded border border-gray-700"
            style={{ backgroundColor: row.hex_color || '#000' }}
          />
          <div>
            <span className="text-white text-sm">{v}</span>
            <span className="block text-xs text-gray-500">{row.shade_code}</span>
          </div>
        </div>
      ),
    },
    { key: 'product_name', label: 'Product' },
    { key: 'size_preference', label: 'Size' },
    {
      key: 'dealer_name',
      label: 'Dealer',
      render: (v, row) => (
        <div>
          <span className="text-white text-sm">{v}</span>
          {row.dealer_city && (
            <span className="block text-xs text-gray-500">{row.dealer_city}</span>
          )}
        </div>
      ),
    },
    {
      key: 'status',
      label: 'Status',
      render: v => <AlertBadge status={v} />,
    },
    {
      key: 'created_at',
      label: 'Date',
      render: v => v ? <span className="text-xs text-gray-400">{formatDate(v)}</span> : '-',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Customer Order Leads</h1>
        <p className="text-sm text-gray-500 mt-1">
          Supply chain overview of all customer enquiries and fulfilment statuses
        </p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-xl text-sm">
          {error}
        </div>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {Object.entries(counts).map(([key, count]) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={`rounded-xl p-3 text-center transition-all border ${
              filter === key
                ? 'bg-blue-600/10 border-blue-500/30 text-blue-400'
                : 'glass border-gray-800 text-gray-400 hover:border-gray-700'
            }`}
          >
            <div className="text-2xl font-bold">{count}</div>
            <div className="text-xs mt-1 capitalize">{key}</div>
          </button>
        ))}
      </div>

      {/* Table */}
      {filtered.length === 0 ? (
        <div className="glass rounded-xl p-10 border border-gray-800 text-center">
          <UserIcon className="w-10 h-10 mx-auto text-gray-600 mb-3" />
          <p className="text-gray-500 text-sm">No customer leads found</p>
        </div>
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}
    </div>
  )
}
