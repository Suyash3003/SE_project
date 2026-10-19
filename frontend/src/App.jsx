import { Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import AdminLayout from './layouts/AdminLayout'
import DealerLayout from './layouts/DealerLayout'
import CustomerLayout from './layouts/CustomerLayout'
import AdminDashboard from './pages/admin/Dashboard'
import DemandForecast from './pages/admin/DemandForecast'
import DeadStock from './pages/admin/DeadStock'
import Transfers from './pages/admin/Transfers'
import DealerPerformance from './pages/admin/DealerPerformance'
import DealerDashboard from './pages/dealer/Dashboard'
import SmartOrders from './pages/dealer/SmartOrders'
import OrderTracking from './pages/dealer/OrderTracking'
import CustomerLeads from './pages/dealer/CustomerLeads'
import ShadeCatalog from './pages/customer/ShadeCatalog'
import ShadeDetail from './pages/customer/ShadeDetail'
import FindNearMe from './pages/customer/FindNearMe'
import SnapAndFind from './pages/customer/SnapAndFind'
import CustomerOrders from './pages/customer/CustomerOrders'
import AdminCustomerLeads from './pages/admin/AdminCustomerLeads'
import ColorCatalog from './pages/admin/ColorCatalog'
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage'
import { AuthProvider, ProtectedRoute } from './contexts/AuthContext'
import { SimulationProvider } from './contexts/SimulationContext'

export default function App() {
  return (
    <AuthProvider>
      <SimulationProvider>
        <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register/:role" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/admin" element={<ProtectedRoute role="admin"><AdminLayout /></ProtectedRoute>}>
        <Route index element={<AdminDashboard />} />
        <Route path="catalog" element={<ColorCatalog />} />
        <Route path="forecast" element={<DemandForecast />} />
        <Route path="dead-stock" element={<DeadStock />} />
        <Route path="transfers" element={<Transfers />} />
        <Route path="dealers" element={<DealerPerformance />} />
        <Route path="customer-leads" element={<AdminCustomerLeads />} />
      </Route>
      <Route path="/dealer" element={<ProtectedRoute role="dealer"><DealerLayout /></ProtectedRoute>}>
        <Route index element={<DealerDashboard />} />
        <Route path="smart-orders" element={<SmartOrders />} />
        <Route path="orders" element={<OrderTracking />} />
        <Route path="customer-leads" element={<CustomerLeads />} />
      </Route>
      <Route path="/customer" element={<ProtectedRoute role="customer"><CustomerLayout /></ProtectedRoute>}>
        <Route index element={<ShadeCatalog />} />
        <Route path="shade/:shadeId" element={<ShadeDetail />} />
        <Route path="find-near-me" element={<FindNearMe />} />
        <Route path="snap-find" element={<SnapAndFind />} />
        <Route path="orders" element={<CustomerOrders />} />
      </Route>
      </Routes>
      </SimulationProvider>
    </AuthProvider>
  )
}
