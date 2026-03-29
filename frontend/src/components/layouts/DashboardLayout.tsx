import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from '../common/Sidebar'
import BottomNav from '../common/BottomNav'
import Header from '../common/Header'

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    // h-screen locks the whole app to the window height
    // overflow-hidden prevents the whole page from scrolling
    <div className="flex h-screen overflow-hidden bg-background">
      
      {/* Sidebar - should stay fixed/relative as we discussed */}
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Content Wrapper */}
      <div className="flex flex-col flex-1 min-w-0 relative">
        
        {/* Header - usually h-16 */}
        <Header onMenuClick={() => setSidebarOpen(true)} />

        {/* Main Content Area */}
        {/* overflow-y-auto makes ONLY this section scrollable */}
        <main className="flex-1 overflow-y-auto pt-16 pb-20 lg:pb-0">
          <div className="p-4 lg:p-8">
            <Outlet />
          </div>
        </main>
      </div>

      <BottomNav />
    </div>
  )
}