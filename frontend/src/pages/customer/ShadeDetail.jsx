import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { createOrderRequest, fetchShadeDetail, fetchShadeAvailability } from '../../api/customer'
import { fetchCurrentUser } from '../../api/auth'
import { FireIcon, MapPinIcon, XMarkIcon } from '@heroicons/react/24/solid'

export default function ShadeDetail() {
  const { shadeId } = useParams()
  const [shade, setShade] = useState(null)
  const [availability, setAvailability] = useState([])
  const [loading, setLoading] = useState(true)
  const [orderOpen, setOrderOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [orderError, setOrderError] = useState('')
  const [orderResult, setOrderResult] = useState(null)
  const [order, setOrder] = useState({ customer_name: '', customer_phone: '', size_preference: '', dealer_id: '', quantity: 1, delivery_address: '', notes: '' })

  useEffect(() => {
    Promise.all([
      fetchShadeDetail(shadeId),
      fetchShadeAvailability(shadeId, 19.07, 72.87),
      fetchCurrentUser(),
    ]).then(([s, a, me]) => {
      setShade(s.data)
      setAvailability(a.data)
      setOrder(current => ({
        ...current,
        customer_name: me.data.email?.split('@')[0]?.replace(/[._-]/g, ' ') || '',
        customer_phone: me.data.phone || '',
        size_preference: s.data.sizes?.[0]?.size || '',
        dealer_id: a.data.find(dealer => dealer.stock_status !== 'Out of Stock')?.dealer_id || '',
      }))
    }).catch(() => {}).finally(() => setLoading(false))
  }, [shadeId])

  if (loading) return <LoadingSpinner />
  if (!shade) return <p className="text-gray-500">Shade not found</p>

  const orderableDealers = availability.filter(dealer => dealer.stock_status !== 'Out of Stock')
  const selectedSize = shade.sizes?.find(size => size.size === order.size_preference)
  const selectedDealer = availability.find(dealer => dealer.dealer_id === Number(order.dealer_id))
  const estimatedTotal = (selectedSize?.mrp || 0) * Number(order.quantity || 0)

  const openOrder = () => {
    setOrderError('')
    setOrderResult(null)
    setOrderOpen(true)
  }

  const submitOrder = async (event) => {
    event.preventDefault()
    setOrderError('')
    if (!order.dealer_id) {
      setOrderError('Please select a dealer with this shade in stock.')
      return
    }
    setSubmitting(true)
    try {
      const { data } = await createOrderRequest({
        ...order,
        shade_id: Number(shadeId),
        dealer_id: Number(order.dealer_id),
        quantity: Number(order.quantity),
      })
      setOrderResult(data.order)
    } catch (error) {
      setOrderError(error.response?.data?.detail || 'We could not place your order. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <Link to="/customer" className="text-orange-500 hover:text-orange-600 text-sm">&larr; Back to catalog</Link>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Color preview */}
        <div>
          <div
            className="h-64 rounded-2xl shadow-xl"
            style={{ backgroundColor: shade.hex_color }}
          />
          <div className="mt-4 flex items-center gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{shade.shade_name}</h1>
              <p className="text-gray-500">{shade.shade_code} | {shade.shade_family}</p>
            </div>
            {shade.is_trending && (
              <span className="flex items-center gap-1 bg-orange-100 text-orange-600 px-3 py-1 rounded-full text-xs font-medium">
                <FireIcon className="w-3.5 h-3.5" /> Trending
              </span>
            )}
          </div>

          <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
            <div className="bg-gray-50 rounded-lg p-3">
              <span className="text-gray-500">HEX</span>
              <p className="font-mono text-gray-900">{shade.hex_color}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <span className="text-gray-500">RGB</span>
              <p className="font-mono text-gray-900">
                {shade.rgb?.r}, {shade.rgb?.g}, {shade.rgb?.b}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <span className="text-gray-500">Product</span>
              <p className="text-gray-900">{shade.product?.name}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <span className="text-gray-500">Finish</span>
              <p className="text-gray-900">{shade.product?.finish}</p>
            </div>
          </div>
        </div>

        {/* Sizes + availability */}
        <div className="space-y-6">
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Available Sizes</h3>
            <div className="grid grid-cols-2 gap-3">
              {shade.sizes?.map(s => (
                <button type="button" onClick={() => { setOrder(current => ({ ...current, size_preference: s.size })); openOrder() }} key={s.sku_code} className="bg-white border border-gray-200 rounded-xl p-4 text-left hover:shadow-md hover:border-orange-300 transition-shadow">
                  <p className="font-bold text-gray-900">{s.size}</p>
                  <p className="text-xs text-gray-500">{s.sku_code}</p>
                  <p className="text-lg font-bold text-orange-600 mt-1">{`\u20B9${s.mrp?.toLocaleString('en-IN')}`}</p>
                </button>
              ))}
            </div>
            <button onClick={openOrder} disabled={!orderableDealers.length} className="mt-4 w-full rounded-xl bg-orange-500 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-orange-400 disabled:cursor-not-allowed disabled:bg-gray-300">
              {orderableDealers.length ? 'Order this paint' : 'Currently unavailable nearby'}
            </button>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <MapPinIcon className="w-4 h-4 text-orange-500" />
              Nearby Dealers
            </h3>
            {availability.length === 0 ? (
              <p className="text-sm text-gray-400">No nearby dealers found</p>
            ) : (
              <div className="space-y-2">
                {availability.map(d => (
                  <div key={d.dealer_id} className="bg-white border border-gray-200 rounded-xl p-3 flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900 text-sm">{d.dealer_name}</p>
                      <p className="text-xs text-gray-500">{d.city} | {d.distance_km} km away</p>
                    </div>
                    <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                      d.stock_status === 'In Stock' ? 'bg-emerald-100 text-emerald-700' :
                      d.stock_status === 'Low Stock' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {d.stock_status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {orderOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-950/50 p-4">
          <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl">
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Order {shade.shade_name}</h2>
                <p className="text-sm text-gray-500">Your selected dealer will contact you to confirm delivery and payment.</p>
              </div>
              <button onClick={() => setOrderOpen(false)} className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-700" aria-label="Close order form"><XMarkIcon className="h-5 w-5" /></button>
            </div>

            {orderResult ? (
              <div className="rounded-xl bg-emerald-50 p-5 text-center">
                <p className="text-lg font-bold text-emerald-800">Order request sent</p>
                <p className="mt-2 text-sm text-emerald-700">{orderResult.dealer_name} will contact you about {orderResult.quantity} × {orderResult.size} of {orderResult.shade_name}.</p>
                <button onClick={() => setOrderOpen(false)} className="mt-5 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500">Done</button>
              </div>
            ) : (
              <form onSubmit={submitOrder} className="space-y-4">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <label className="text-sm font-medium text-gray-700">Name<input required value={order.customer_name} onChange={e => setOrder(current => ({ ...current, customer_name: e.target.value }))} className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 font-normal outline-none focus:ring-2 focus:ring-orange-300" /></label>
                  <label className="text-sm font-medium text-gray-700">Phone<input required minLength="10" value={order.customer_phone} onChange={e => setOrder(current => ({ ...current, customer_phone: e.target.value }))} className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 font-normal outline-none focus:ring-2 focus:ring-orange-300" /></label>
                </div>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <label className="text-sm font-medium text-gray-700">Size<select value={order.size_preference} onChange={e => setOrder(current => ({ ...current, size_preference: e.target.value }))} className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 font-normal outline-none focus:ring-2 focus:ring-orange-300">{shade.sizes?.map(size => <option key={size.sku_code} value={size.size}>{size.size} — ₹{size.mrp?.toLocaleString('en-IN')}</option>)}</select></label>
                  <label className="text-sm font-medium text-gray-700">Quantity<input required type="number" min="1" max="100" value={order.quantity} onChange={e => setOrder(current => ({ ...current, quantity: e.target.value }))} className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 font-normal outline-none focus:ring-2 focus:ring-orange-300" /></label>
                </div>
                <label className="block text-sm font-medium text-gray-700">Dealer<select required value={order.dealer_id} onChange={e => setOrder(current => ({ ...current, dealer_id: e.target.value }))} className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 font-normal outline-none focus:ring-2 focus:ring-orange-300"><option value="">Select a dealer</option>{orderableDealers.map(dealer => <option key={dealer.dealer_id} value={dealer.dealer_id}>{dealer.dealer_name} · {dealer.city} ({dealer.distance_km} km, {dealer.stock_status})</option>)}</select></label>
                <label className="block text-sm font-medium text-gray-700">Delivery address<textarea required maxLength="300" rows="2" value={order.delivery_address} onChange={e => setOrder(current => ({ ...current, delivery_address: e.target.value }))} className="mt-1 w-full resize-none rounded-lg border border-gray-300 px-3 py-2 font-normal outline-none focus:ring-2 focus:ring-orange-300" /></label>
                <label className="block text-sm font-medium text-gray-700">Notes <span className="font-normal text-gray-400">(optional)</span><textarea maxLength="500" rows="2" value={order.notes} onChange={e => setOrder(current => ({ ...current, notes: e.target.value }))} className="mt-1 w-full resize-none rounded-lg border border-gray-300 px-3 py-2 font-normal outline-none focus:ring-2 focus:ring-orange-300" /></label>
                {selectedDealer && <div className="rounded-lg bg-gray-50 p-3 text-sm text-gray-600">Estimated total: <strong className="text-gray-900">₹{estimatedTotal.toLocaleString('en-IN')}</strong> · Fulfilled by {selectedDealer.dealer_name}</div>}
                {orderError && <p className="text-sm text-red-600">{orderError}</p>}
                <button disabled={submitting} className="w-full rounded-lg bg-orange-500 px-4 py-3 text-sm font-semibold text-white hover:bg-orange-400 disabled:opacity-60">{submitting ? 'Sending order request…' : 'Place order request'}</button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
