import { useEffect, useState } from 'react'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { fetchCustomerOrders } from '../../api/customer'

const statusStyles = {
  requested: 'bg-blue-100 text-blue-700',
  contacted: 'bg-amber-100 text-amber-700',
  fulfilled: 'bg-emerald-100 text-emerald-700',
  cancelled: 'bg-red-100 text-red-700',
}

export default function CustomerOrders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCustomerOrders()
      .then(({ data }) => setOrders(data))
      .catch(() => setOrders([]))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner text="Loading your orders..." />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">My Orders</h1>
        <p className="text-gray-500 mt-1">Track requests placed with your local paint dealers</p>
      </div>

      {orders.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-gray-300 bg-white p-10 text-center text-gray-500">
          You have not placed any orders yet. Choose a shade from the catalog to get started.
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map(order => (
            <article key={order.id} className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="flex gap-3">
                  <div className="mt-0.5 h-11 w-11 rounded-lg border border-gray-200" style={{ backgroundColor: order.hex_color }} />
                  <div>
                    <h2 className="font-semibold text-gray-900">{order.shade_name}</h2>
                    <p className="text-sm text-gray-500">{order.product_name} · {order.size} × {order.quantity}</p>
                    <p className="mt-1 text-xs text-gray-400">{order.dealer_name}, {order.dealer_city}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold capitalize ${statusStyles[order.status] || 'bg-gray-100 text-gray-600'}`}>
                    {order.status}
                  </span>
                  <p className="mt-2 text-sm font-semibold text-gray-900">₹{order.estimated_amount?.toLocaleString('en-IN')}</p>
                </div>
              </div>
              {order.delivery_address && <p className="mt-3 border-t border-gray-100 pt-3 text-sm text-gray-500">Deliver to: {order.delivery_address}</p>}
            </article>
          ))}
        </div>
      )}
    </div>
  )
}
