import { Outlet } from 'react-router-dom'
import { Car } from 'lucide-react'

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/5 via-background to-primary/10 p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-xl bg-primary flex items-center justify-center">
              <Car className="h-7 w-7 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Tobaz Autos</h1>
              <p className="text-sm text-muted-foreground">Management System</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="bg-card rounded-2xl shadow-lg border p-8">
          <Outlet />
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-muted-foreground mt-8">
          © {new Date().getFullYear()} Tobaz Autos. All rights reserved.
        </p>
      </div>
    </div>
  )
}
