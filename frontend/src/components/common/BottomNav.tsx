import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  Truck,
  Receipt,
  MoreHorizontal,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { name: 'Home', href: '/', icon: LayoutDashboard },
  { name: 'Products', href: '/products', icon: Package },
  { name: 'Sales', href: '/sales', icon: ShoppingCart },
  { name: 'Shipments', href: '/shipments', icon: Truck },
  { name: 'Expenses', href: '/expenses', icon: Receipt },
  { name: 'More', href: '/settings', icon: MoreHorizontal },
]

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-card border-t lg:hidden">
      <div className="flex items-center justify-around h-16">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex flex-col items-center justify-center flex-1 h-full gap-1',
                  'text-xs font-medium transition-colors',
                  isActive
                    ? 'text-primary'
                    : 'text-muted-foreground hover:text-foreground'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <div
                    className={cn(
                      'p-1.5 rounded-lg transition-colors',
                      isActive && 'bg-primary/10'
                    )}
                  >
                    <Icon className="h-5 w-5" />
                  </div>
                  <span>{item.name}</span>
                </>
              )}
            </NavLink>
          )
        })}
      </div>
    </nav>
  )
}
