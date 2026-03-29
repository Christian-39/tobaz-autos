import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'sonner'
import { useAuth } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'

// Layouts
import DashboardLayout from './components/layouts/DashboardLayout'
import AuthLayout from './components/layouts/AuthLayout'

// Auth Pages
import Login from './pages/auth/Login'

// Dashboard Pages
import Dashboard from './pages/dashboard/Dashboard'

// Product Pages
import Products from './pages/products/Products'
import ProductDetail from './pages/products/ProductDetail'
import ProductForm from './pages/products/ProductForm'
import Categories from './pages/products/Categories'

// Inventory Pages
import Inventory from './pages/inventory/Inventory'
import StockAlerts from './pages/inventory/StockAlerts'
import Suppliers from './pages/inventory/Suppliers'

// Sales Pages
import Sales from './pages/sales/Sales'
import SaleDetail from './pages/sales/SaleDetail'
import SaleForm from './pages/sales/SaleForm'
import Customers from './pages/sales/Customers'

// Shipment Pages
import Shipments from './pages/shipments/Shipments'
import ShipmentDetail from './pages/shipments/ShipmentDetail'
import ShipmentForm from './pages/shipments/ShipmentForm'

// Expense Pages
import Expenses from './pages/expenses/Expenses'
import ExpenseCategories from './pages/expenses/ExpenseCategories'
import Budgets from './pages/expenses/Budgets'

// User Pages
import Users from './pages/users/Users'
import Profile from './pages/users/Profile'

// Settings Pages
import Settings from './pages/settings/Settings'

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <ThemeProvider>
      <Toaster
        position="top-right"
        richColors
        closeButton
        toastOptions={{
          duration: 4000,
        }}
      />
      <Routes>
        {/* Auth Routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<Login />} />
        </Route>

        {/* Protected Routes */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          {/* Dashboard */}
          <Route path="/" element={<Dashboard />} />

          {/* Products */}
          <Route path="/products" element={<Products />} />
          <Route path="/products/new" element={<ProductForm />} />
          <Route path="/products/:id" element={<ProductDetail />} />
          <Route path="/products/:id/edit" element={<ProductForm />} />
          <Route path="/categories" element={<Categories />} />

          {/* Inventory */}
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/inventory/alerts" element={<StockAlerts />} />
          <Route path="/suppliers" element={<Suppliers />} />

          {/* Sales */}
          <Route path="/sales" element={<Sales />} />
          <Route path="/sales/new" element={<SaleForm />} />
          <Route path="/sales/:id" element={<SaleDetail />} />
          <Route path="/customers" element={<Customers />} />

          {/* Shipments */}
          <Route path="/shipments" element={<Shipments />} />
          <Route path="/shipments/new" element={<ShipmentForm />} />
          <Route path="/shipments/:id" element={<ShipmentDetail />} />

          {/* Expenses */}
          <Route path="/expenses" element={<Expenses />} />
          <Route path="/expenses/categories" element={<ExpenseCategories />} />
          <Route path="/expenses/budgets" element={<Budgets />} />

          {/* Users */}
          <Route path="/users" element={<Users />} />
          <Route path="/profile" element={<Profile />} />

          {/* Settings */}
          <Route path="/settings" element={<Settings />} />
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ThemeProvider>
  )
}

export default App
