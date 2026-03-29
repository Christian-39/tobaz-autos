import { NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  Truck,
  Receipt,
  Users,
  Settings,
  X,
  ChevronRight,
  Warehouse,
  Tags,
  AlertTriangle,
  UserCircle,
  Wallet,
  BarChart3,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/contexts/AuthContext'

interface SidebarProps {
  open: boolean
  onClose: () => void
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  {
    name: 'Products',
    href: '/products',
    icon: Package,
    children: [
      { name: 'All Products', href: '/products' },
      { name: 'Categories', href: '/categories' },
    ],
  },
  {
    name: 'Inventory',
    href: '/inventory',
    icon: Warehouse,
    children: [
      { name: 'Stock Overview', href: '/inventory' },
      { name: 'Stock Alerts', href: '/inventory/alerts' },
      { name: 'Suppliers', href: '/suppliers' },
    ],
  },
  {
    name: 'Sales',
    href: '/sales',
    icon: ShoppingCart,
    children: [
      { name: 'All Sales', href: '/sales' },
      { name: 'Customers', href: '/customers' },
    ],
  },
  {
    name: 'Shipments',
    href: '/shipments',
    icon: Truck,
  },
  {
    name: 'Expenses',
    href: '/expenses',
    icon: Receipt,
    children: [
      { name: 'All Expenses', href: '/expenses' },
      { name: 'Categories', href: '/expenses/categories' },
      { name: 'Budgets', href: '/expenses/budgets' },
    ],
  },
  {
    name: 'Users',
    href: '/users',
    icon: Users,
    adminOnly: true,
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
  },
]

export default function Sidebar({ open, onClose }: SidebarProps) {
  const location = useLocation()
  const { hasPermission } = useAuth()

  const filteredNavigation = navigation.filter((item) => {
    if (item.adminOnly) {
      return hasPermission('admin')
    }
    return true
  })

  return (
    <>
      {/* Mobile overlay */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={onClose}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        className={cn(
          'fixed top-0 left-0 z-50 h-full w-64 bg-card border-r',
          'lg:translate-x-0 lg:static',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
        initial={false}
        animate={{ x: open ? 0 : '-100%' }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-6 border-b">
          <NavLink to="/" className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary flex items-center justify-center">
              <BarChart3 className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="font-bold text-lg">Tobaz Autos</h1>
            </div>
          </NavLink>
          <button
            onClick={onClose}
            className="lg:hidden p-2 rounded-lg hover:bg-muted"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1 overflow-y-auto h-[calc(100vh-4rem)]">
          {filteredNavigation.map((item) => (
            <NavItem
              key={item.name}
              item={item}
              isActive={location.pathname === item.href || location.pathname.startsWith(item.href + '/')}
            />
          ))}
        </nav>
      </motion.aside>
    </>
  )
}

interface NavItemProps {
  item: {
    name: string
    href: string
    icon: React.ElementType
    children?: { name: string; href: string }[]
  }
  isActive: boolean
}

function NavItem({ item, isActive }: NavItemProps) {
  const Icon = item.icon
  const location = useLocation()

  if (item.children) {
    const isChildActive = item.children.some((child) =>
      location.pathname === child.href
    )

    return (
      <div className="space-y-1">
        <div
          className={cn(
            'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium',
            isActive || isChildActive
              ? 'bg-primary/10 text-primary'
              : 'text-muted-foreground hover:bg-muted hover:text-foreground'
          )}
        >
          <Icon className="h-5 w-5" />
          <span>{item.name}</span>
        </div>
        <div className="ml-4 pl-4 border-l space-y-1">
          {item.children.map((child) => (
            <NavLink
              key={child.name}
              to={child.href}
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm',
                location.pathname === child.href
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              )}
            >
              <ChevronRight className="h-4 w-4" />
              {child.name}
            </NavLink>
          ))}
        </div>
      </div>
    )
  }

  return (
    <NavLink
      to={item.href}
      className={cn(
        'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
        isActive
          ? 'bg-primary/10 text-primary'
          : 'text-muted-foreground hover:bg-muted hover:text-foreground'
      )}
    >
      <Icon className="h-5 w-5" />
      <span>{item.name}</span>
    </NavLink>
  )
}
