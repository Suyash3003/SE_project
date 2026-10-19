import { useState, useEffect } from 'react'
import {
  SwatchIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XMarkIcon,
  SparklesIcon,
  BuildingStorefrontIcon,
  Squares2X2Icon,
  TableCellsIcon,
} from '@heroicons/react/24/outline'
import {
  fetchCatalogShades,
  createCatalogShade,
  addInventoryStock,
  fetchProducts,
  fetchWarehouses,
} from '../../api/admin'
import { formatCurrency } from '../../utils/formatters'

const FAMILIES = [
  'All',
  'Reds',
  'Blues',
  'Greens',
  'Yellows',
  'Purples',
  'Oranges',
  'Neutrals',
  'Whites',
]

export default function ColorCatalog() {
  const [shades, setShades] = useState([])
  const [products, setProducts] = useState([])
  const [warehouses, setWarehouses] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [search, setSearch] = useState('')
  const [selectedFamily, setSelectedFamily] = useState('All')
  const [viewMode, setViewMode] = useState('table') // 'table' or 'grid'

  // Modals
  const [isAddOpen, setIsAddOpen] = useState(false)
  const [isStockOpen, setIsStockOpen] = useState(false)
  const [stockTarget, setStockTarget] = useState(null) // shade object

  // Feedback alerts
  const [feedback, setFeedback] = useState({ type: '', text: '' })

  // Add Shade Form State
  const [newShade, setNewShade] = useState({
    shade_name: '',
    hex_color: '#8A2BE2',
    shade_family: 'Purples',
    product_id: '',
    is_trending: false,
    initial_stock_per_warehouse: 200,
  })

  // Add Stock Form State
  const [stockForm, setStockForm] = useState({
    warehouse_id: '',
    sku_id: '',
    quantity: 100,
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [shadesRes, prodsRes, whsRes] = await Promise.all([
        fetchCatalogShades(),
        fetchProducts(),
        fetchWarehouses(),
      ])
      setShades(shadesRes.data || [])
      setProducts(prodsRes.data || [])
      setWarehouses(whsRes.data || [])

      if (prodsRes.data?.length > 0 && !newShade.product_id) {
        setNewShade((prev) => ({ ...prev, product_id: prodsRes.data[0].id }))
      }
      if (whsRes.data?.length > 0 && !stockForm.warehouse_id) {
        setStockForm((prev) => ({ ...prev, warehouse_id: whsRes.data[0].id }))
      }
    } catch (err) {
      console.error(err)
      setFeedback({ type: 'error', text: 'Failed to load color catalog data' })
    } finally {
      setLoading(false)
    }
  }

  const handleCreateShade = async (e) => {
    e.preventDefault()
    if (!newShade.shade_name.trim()) return

    setSubmitting(true)
    setFeedback({ type: '', text: '' })
    try {
      const res = await createCatalogShade({
        ...newShade,
        product_id: Number(newShade.product_id),
        initial_stock_per_warehouse: Number(newShade.initial_stock_per_warehouse),
      })
      setFeedback({ type: 'success', text: res.data.message })
      setIsAddOpen(false)
      // Reset form
      setNewShade({
        shade_name: '',
        hex_color: '#4F97A3',
        shade_family: 'Blues',
        product_id: products[0]?.id || '',
        is_trending: false,
        initial_stock_per_warehouse: 200,
      })
      // Reload catalog
      await loadData()
    } catch (err) {
      console.error(err)
      const msg = err.response?.data?.detail || 'Failed to create new shade'
      setFeedback({ type: 'error', text: msg })
    } finally {
      setSubmitting(false)
    }
  }

  const handleOpenStockModal = (shade) => {
    setStockTarget(shade)
    setStockForm({
      warehouse_id: warehouses[0]?.id || '',
      sku_id: shade.skus?.[0]?.id || '',
      quantity: 150,
    })
    setIsStockOpen(true)
  }

  const handleAddStock = async (e) => {
    e.preventDefault()
    if (!stockForm.sku_id || !stockForm.warehouse_id || stockForm.quantity <= 0) return

    setSubmitting(true)
    setFeedback({ type: '', text: '' })
    try {
      const res = await addInventoryStock({
        warehouse_id: Number(stockForm.warehouse_id),
        sku_id: Number(stockForm.sku_id),
        quantity: Number(stockForm.quantity),
      })
      setFeedback({ type: 'success', text: res.data.message })
      setIsStockOpen(false)
      await loadData()
    } catch (err) {
      console.error(err)
      const msg = err.response?.data?.detail || 'Failed to replenish stock'
      setFeedback({ type: 'error', text: msg })
    } finally {
      setSubmitting(false)
    }
  }

  // Filtered shades
  const filteredShades = shades.filter((s) => {
    const matchesFamily =
      selectedFamily === 'All' || s.shade_family.toLowerCase() === selectedFamily.toLowerCase()
    const matchesSearch =
      !search ||
      s.shade_name.toLowerCase().includes(search.toLowerCase()) ||
      s.shade_code.toLowerCase().includes(search.toLowerCase()) ||
      s.product_name.toLowerCase().includes(search.toLowerCase())
    return matchesFamily && matchesSearch
  })

  // Quick stats
  const totalStockUnits = shades.reduce((acc, s) => acc + (s.total_stock || 0), 0)
  const totalSkus = shades.reduce((acc, s) => acc + (s.sku_count || 0), 0)

  return (
    <div className="space-y-6">
      {/* Top Banner & Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 rounded-2xl p-6 text-white shadow-xl">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="p-1.5 bg-indigo-500/20 text-indigo-400 rounded-lg border border-indigo-500/30">
              <SwatchIcon className="w-5 h-5" />
            </span>
            <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
              Factory Catalog & Inventory
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Paint Colors & Inventory Management</h1>
          <p className="text-sm text-slate-400 mt-1">
            Add custom shades, view multi-pack SKUs, and replenish warehouse inventory across India.
          </p>
        </div>

        <button
          onClick={() => setIsAddOpen(true)}
          className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-medium text-sm shadow-lg shadow-indigo-500/25 transition-all transform hover:-translate-y-0.5"
        >
          <PlusIcon className="w-5 h-5" />
          Add New Color to Catalog
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400">Total Shades Cataloged</p>
            <p className="text-2xl font-bold text-white mt-1">{shades.length}</p>
            <p className="text-xs text-indigo-400 mt-0.5">Across 8 color families</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <SwatchIcon className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400">Active Manufactured SKUs</p>
            <p className="text-2xl font-bold text-white mt-1">{totalSkus}</p>
            <p className="text-xs text-purple-400 mt-0.5">1L, 4L, 10L, 20L can packs</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <BuildingStorefrontIcon className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-400">Total Inventory in Stock</p>
            <p className="text-2xl font-bold text-emerald-400 mt-1">
              {totalStockUnits.toLocaleString()} units
            </p>
            <p className="text-xs text-slate-400 mt-0.5">Distributed in 10+ warehouses</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <CheckCircleIcon className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Feedback Banner */}
      {feedback.text && (
        <div
          className={`flex items-center justify-between p-4 rounded-xl border text-sm font-medium ${
            feedback.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300'
              : 'bg-rose-950/40 border-rose-500/30 text-rose-300'
          }`}
        >
          <span>{feedback.text}</span>
          <button
            onClick={() => setFeedback({ type: '', text: '' })}
            className="text-slate-400 hover:text-white"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <MagnifyingGlassIcon className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search shade name, code (e.g. AP-RD01), product..."
            className="w-full bg-slate-800/80 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Family Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
          {FAMILIES.map((family) => (
            <button
              key={family}
              onClick={() => setSelectedFamily(family)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                selectedFamily === family
                  ? 'bg-indigo-600 text-white shadow'
                  : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {family}
            </button>
          ))}
        </div>

        {/* View Toggle & Refresh */}
        <div className="flex items-center gap-2">
          <div className="flex items-center bg-slate-800/80 rounded-lg p-0.5 border border-slate-700">
            <button
              onClick={() => setViewMode('table')}
              className={`p-1.5 rounded-md ${
                viewMode === 'table' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
              title="Table View"
            >
              <TableCellsIcon className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`p-1.5 rounded-md ${
                viewMode === 'grid' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
              title="Grid Cards"
            >
              <Squares2X2Icon className="w-4 h-4" />
            </button>
          </div>

          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Refresh Catalog"
          >
            <ArrowPathIcon className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Catalog View */}
      {loading ? (
        <div className="py-20 text-center">
          <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-slate-400">Loading color shades and inventory...</p>
        </div>
      ) : filteredShades.length === 0 ? (
        <div className="py-16 text-center bg-slate-900/40 border border-slate-800 rounded-xl">
          <SwatchIcon className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-base font-semibold text-slate-300">No matching color shades</p>
          <p className="text-sm text-slate-500 mt-1">
            Try adjusting your search query or color family filter.
          </p>
        </div>
      ) : viewMode === 'table' ? (
        /* TABLE VIEW */
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/60 border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3.5">Color Swatch</th>
                  <th className="px-5 py-3.5">Shade Code</th>
                  <th className="px-5 py-3.5">Shade Name</th>
                  <th className="px-5 py-3.5">Family</th>
                  <th className="px-5 py-3.5">Product Line</th>
                  <th className="px-5 py-3.5">Available SKUs</th>
                  <th className="px-5 py-3.5">Total Warehouse Stock</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {filteredShades.map((shade) => (
                  <tr key={shade.id} className="hover:bg-slate-800/30 transition-colors">
                    {/* Swatch */}
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-8 h-8 rounded-lg shadow-sm border border-slate-700/60 shrink-0"
                          style={{ backgroundColor: shade.hex_color }}
                        />
                        <span className="font-mono text-xs text-slate-400">{shade.hex_color}</span>
                      </div>
                    </td>

                    {/* Shade Code */}
                    <td className="px-5 py-3.5 font-mono text-xs text-indigo-400 font-semibold">
                      {shade.shade_code}
                    </td>

                    {/* Shade Name */}
                    <td className="px-5 py-3.5 font-medium text-white">
                      <div className="flex items-center gap-1.5">
                        <span>{shade.shade_name}</span>
                        {shade.is_trending && (
                          <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
                            <SparklesIcon className="w-3 h-3" /> Trending
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Family */}
                    <td className="px-5 py-3.5">
                      <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
                        {shade.shade_family}
                      </span>
                    </td>

                    {/* Product */}
                    <td className="px-5 py-3.5">
                      <div>
                        <p className="font-medium text-slate-200">{shade.product_name}</p>
                        <p className="text-xs text-slate-400">{shade.product_category} • {shade.finish}</p>
                      </div>
                    </td>

                    {/* SKUs */}
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        {shade.skus?.map((sku) => (
                          <span
                            key={sku.id}
                            className="px-2 py-0.5 rounded text-[11px] bg-slate-800/80 border border-slate-700/80 text-slate-300"
                            title={`MRP: ${formatCurrency(sku.mrp)}`}
                          >
                            {sku.size}
                          </span>
                        ))}
                      </div>
                    </td>

                    {/* Stock */}
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <span
                        className={`font-semibold text-sm ${
                          shade.total_stock > 1000
                            ? 'text-emerald-400'
                            : shade.total_stock > 300
                            ? 'text-amber-400'
                            : 'text-rose-400'
                        }`}
                      >
                        {shade.total_stock.toLocaleString()} units
                      </span>
                    </td>

                    {/* Action */}
                    <td className="px-5 py-3.5 text-right whitespace-nowrap">
                      <button
                        onClick={() => handleOpenStockModal(shade)}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs font-medium transition-colors"
                      >
                        <PlusIcon className="w-3.5 h-3.5" />
                        Add Stock
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* GRID CARDS VIEW */
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredShades.map((shade) => (
            <div
              key={shade.id}
              className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden hover:border-slate-700 transition-all flex flex-col"
            >
              {/* Color Swatch Header */}
              <div
                className="h-28 w-full relative p-3 flex flex-col justify-between"
                style={{ backgroundColor: shade.hex_color }}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-black/60 text-white backdrop-blur-sm">
                    {shade.shade_code}
                  </span>
                  {shade.is_trending && (
                    <span className="px-2 py-0.5 rounded bg-amber-500 text-black text-[10px] font-bold shadow">
                      Trending
                    </span>
                  )}
                </div>
                <div className="font-mono text-xs px-2 py-0.5 rounded bg-black/60 text-white w-max backdrop-blur-sm">
                  {shade.hex_color}
                </div>
              </div>

              {/* Details */}
              <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
                <div>
                  <h3 className="font-bold text-base text-white">{shade.shade_name}</h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {shade.product_name} • {shade.shade_family}
                  </p>
                </div>

                <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800">
                  <span className="text-slate-400">Total Stock</span>
                  <span className="font-bold text-emerald-400">
                    {shade.total_stock.toLocaleString()} units
                  </span>
                </div>

                <button
                  onClick={() => handleOpenStockModal(shade)}
                  className="w-full py-2 rounded-lg bg-indigo-500/15 hover:bg-indigo-500/25 text-indigo-400 border border-indigo-500/30 text-xs font-semibold transition-colors flex items-center justify-center gap-1.5"
                >
                  <PlusIcon className="w-3.5 h-3.5" />
                  Replenish Stock
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* MODAL 1: ADD NEW COLOR */}
      {isAddOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                  <PlusIcon className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold text-white">Add New Color to Catalog</h3>
              </div>
              <button
                onClick={() => setIsAddOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleCreateShade} className="p-6 space-y-4">
              {/* Swatch & Color Picker Row */}
              <div className="bg-slate-800/40 border border-slate-700/60 rounded-xl p-4 flex items-center gap-5">
                <div
                  className="w-20 h-20 rounded-xl shadow-lg border-2 border-white/20 shrink-0 transition-transform transform hover:scale-105"
                  style={{ backgroundColor: newShade.hex_color }}
                />
                <div className="flex-1 space-y-2">
                  <label className="text-xs font-semibold text-slate-300 block">
                    Pick Shade Color (HEX)
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={newShade.hex_color}
                      onChange={(e) =>
                        setNewShade({ ...newShade, hex_color: e.target.value.toUpperCase() })
                      }
                      className="w-10 h-10 rounded-lg cursor-pointer bg-transparent border-0 p-0"
                    />
                    <input
                      type="text"
                      value={newShade.hex_color}
                      onChange={(e) =>
                        setNewShade({ ...newShade, hex_color: e.target.value.toUpperCase() })
                      }
                      placeholder="#RRGGBB"
                      className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white font-mono w-28 uppercase focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Live swatch will automatically calculate RGB values for Snap & Find matching.
                  </p>
                </div>
              </div>

              {/* Shade Name */}
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Color / Shade Name *
                </label>
                <input
                  type="text"
                  required
                  value={newShade.shade_name}
                  onChange={(e) => setNewShade({ ...newShade, shade_name: e.target.value })}
                  placeholder="e.g. Royal Amethyst, Kashmir Saffron"
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Family & Product Grid */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">
                    Color Family
                  </label>
                  <select
                    value={newShade.shade_family}
                    onChange={(e) => setNewShade({ ...newShade, shade_family: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  >
                    {FAMILIES.filter((f) => f !== 'All').map((fam) => (
                      <option key={fam} value={fam}>
                        {fam}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">
                    Paint Product
                  </label>
                  <select
                    value={newShade.product_id}
                    onChange={(e) => setNewShade({ ...newShade, product_id: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                  >
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.finish})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Initial Warehouse Stock */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs font-semibold text-slate-300">
                    Initial Stock Allocation (per warehouse)
                  </label>
                  <span className="text-xs font-bold text-indigo-400">
                    {newShade.initial_stock_per_warehouse} units / WH
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1000"
                  step="50"
                  value={newShade.initial_stock_per_warehouse}
                  onChange={(e) =>
                    setNewShade({ ...newShade, initial_stock_per_warehouse: e.target.value })
                  }
                  className="w-full accent-indigo-500 cursor-pointer"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  Will seed initial stock into all {warehouses.length} regional warehouses.
                </p>
              </div>

              {/* Trending Toggle */}
              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="trending"
                  checked={newShade.is_trending}
                  onChange={(e) => setNewShade({ ...newShade, is_trending: e.target.checked })}
                  className="w-4 h-4 rounded text-indigo-600 bg-slate-800 border-slate-700 focus:ring-0 cursor-pointer"
                />
                <label htmlFor="trending" className="text-xs text-slate-300 cursor-pointer">
                  Feature as <strong>Trending Shade</strong> in Customer Catalog & Dealer Smart Restock
                </label>
              </div>

              {/* Action Buttons */}
              <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsAddOpen(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-medium shadow-md transition-colors flex items-center gap-2"
                >
                  {submitting ? 'Creating SKUs...' : 'Create Color & Allocate Stock'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: ADD INVENTORY STOCK */}
      {isStockOpen && stockTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl">
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div
                  className="w-6 h-6 rounded-md border border-slate-700 shrink-0"
                  style={{ backgroundColor: stockTarget.hex_color }}
                />
                <h3 className="text-base font-bold text-white">
                  Add Stock: {stockTarget.shade_name}
                </h3>
              </div>
              <button
                onClick={() => setIsStockOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddStock} className="p-6 space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Destination Warehouse *
                </label>
                <select
                  value={stockForm.warehouse_id}
                  onChange={(e) => setStockForm({ ...stockForm, warehouse_id: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  {warehouses.map((wh) => (
                    <option key={wh.id} value={wh.id}>
                      {wh.name} ({wh.city})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Pack Size (SKU) *
                </label>
                <select
                  value={stockForm.sku_id}
                  onChange={(e) => setStockForm({ ...stockForm, sku_id: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  {stockTarget.skus?.map((sku) => (
                    <option key={sku.id} value={sku.id}>
                      {sku.size} pack ({sku.sku_code}) — {formatCurrency(sku.mrp)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Units to Add (Quantity) *
                </label>
                <input
                  type="number"
                  min="1"
                  max="10000"
                  required
                  value={stockForm.quantity}
                  onChange={(e) => setStockForm({ ...stockForm, quantity: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsStockOpen(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-medium shadow-md transition-colors"
                >
                  {submitting ? 'Adding...' : 'Add Stock Units'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
