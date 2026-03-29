import { useEffect, useState } from 'react'
import { Package, AlertTriangle, TrendingDown } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { productsApi } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'
import type { Product } from '@/types'

export default function Inventory() {
  const [products, setProducts] = useState<Product[]>([])
  const [stats, setStats] = useState({
    total_value: 0,
    low_stock: 0,
    out_of_stock: 0,
  })

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const response = await productsApi.getProducts()
      const data = (response as any).results || []
      setProducts(data)
      setStats({
        total_value: data.reduce((acc: number, p: Product) => acc + (p.inventory_value || 0), 0),
        low_stock: data.filter((p: Product) => p.stock_status === 'low_stock').length,
        out_of_stock: data.filter((p: Product) => p.stock_status === 'out_of_stock').length,
      })
    } catch (error) {
      console.error('Error fetching inventory:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Inventory</h1>
        <p className="text-muted-foreground mt-1">
          Track and manage your inventory
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium">Total Value</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(stats.total_value)}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium">Low Stock</CardTitle>
            <TrendingDown className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.low_stock}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-sm font-medium">Out of Stock</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.out_of_stock}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-8">
            Transaction history will appear here
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
