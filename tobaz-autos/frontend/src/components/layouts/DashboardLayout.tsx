import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from '../common/Sidebar'
import BottomNav from '../common/BottomNav'
import Header from '../common/Header'

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-background">
      {/* Desktop Sidebar */}
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Header */}
      <Header onMenuClick={() => setSidebarOpen(true)} />

      {/* Main Content */}
      <main className="lg:pl-64 pb-20 lg:pb-0">
        <div className="p-4 lg:p-8">
          <Outlet />
        </div>
      </main>

      {/* Mobile Bottom Navigation */}
      <BottomNav />
    </div>
  )
}
