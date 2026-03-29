import { useState } from 'react'
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

      {/* Sidebar Container */}
      <motion.aside
        className={cn(
          'fixed top-0 left-0 z-50 h-full w-64 bg-card border-r transition-transform duration-300 ease-in-out',
          'lg:relative lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
        initial={false}
        animate={{ x: open || window.innerWidth >= 1024 ? 0 : '-100%' }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      >
        {/* Logo Section */}
        <div className="relative z-[60] flex items-center justify-between h-16 px-6 border-b">
          <NavLink to="/" className="flex items-center gap-3" onClick={onClose}> 
            {/* Added onClick to NavLink so it closes sidebar when clicking logo on mobile */}
            <div className="h-10 w-10 rounded-xl bg-primary flex items-center justify-center">
              <BarChart3 className="h-6 w-6 text-primary-foreground" />
            </div>
            <h1 className="font-bold text-lg">Tobaz Autos</h1>
          </NavLink>
          
          <button
            type="button" // Always specify type to prevent accidental form submits
            onClick={(e) => {
              e.stopPropagation(); // Prevent the click from bubbling to the overlay
              onClose();
            }}
            className="lg:hidden p-2 rounded-lg hover:bg-muted transition-colors cursor-pointer"
            aria-label="Close menu"
          >
            <X className="h-6 w-6" /> {/* Increased size slightly for better touch target */}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-4 space-y-1 overflow-y-auto h-[calc(100vh-4rem)] scrollbar-thin">
          {filteredNavigation.map((item) => (
            <NavItem
              key={item.name}
              item={item}
              isActive={
                location.pathname === item.href ||
                (item.href !== '/' && location.pathname.startsWith(item.href))
              }
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

  // Initialize open state if a child route is active
  const [isOpen, setIsOpen] = useState(
    item.children?.some((child) => location.pathname === child.href) || false
  )

  if (item.children) {
    const isChildActive = item.children.some(
      (child) => location.pathname === child.href
    )

    return (
      <div className="space-y-1">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors',
            isActive || isChildActive
              ? 'bg-primary/10 text-primary'
              : 'text-muted-foreground hover:bg-muted hover:text-foreground'
          )}
        >
          <div className="flex items-center gap-3">
            <Icon className="h-5 w-5" />
            <span>{item.name}</span>
          </div>
          <ChevronRight
            className={cn(
              'h-4 w-4 transition-transform duration-200',
              isOpen && 'rotate-90'
            )}
          />
        </button>

        <AnimatePresence initial={false}>
          {isOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.2, ease: 'easeInOut' }}
              className="overflow-hidden"
            >
              <div className="ml-4 pl-4 border-l space-y-1 mt-1">
                {item.children.map((child) => (
                  <NavLink
                    key={child.name}
                    to={child.href}
                    className={cn(
                      'flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors',
                      location.pathname === child.href
                        ? 'bg-primary/10 text-primary font-medium'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    )}
                  >
                    <div
                      className={cn(
                        'h-1.5 w-1.5 rounded-full bg-current opacity-40',
                        location.pathname === child.href && 'opacity-100'
                      )}
                    />
                    {child.name}
                  </NavLink>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
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