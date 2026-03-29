import { useEffect, useState } from 'react'
import { AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { productsApi } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'
import type { Product } from '@/types'

export default function StockAlerts() {
  const [lowStock, setLowStock] = useState<Product[]>([])
  const [outOfStock, setOutOfStock] = useState<Product[]>([])

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      const [low, out] = await Promise.all([
        productsApi.getLowStockProducts(),
        productsApi.getOutOfStockProducts(),
      ])
      setLowStock((low as any).results || [])
      setOutOfStock((out as any).results || [])
    } catch (error) {
      console.error('Error fetching alerts:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Stock Alerts</h1>
        <p className="text-muted-foreground mt-1">
          Products that need attention
        </p>
      </div>

      <Card className="border-yellow-500/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-yellow-500" />
            Low Stock ({lowStock.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {lowStock.length === 0 ? (
            <p className="text-muted-foreground">No low stock items</p>
          ) : (
            <div className="space-y-2">
              {lowStock.map((product) => (
                <div
                  key={product.id}
                  className="flex items-center justify-between p-3 bg-yellow-500/10 rounded-lg"
                >
                  <div>
                    <p className="font-medium">{product.name}</p>
                    <p className="text-sm text-muted-foreground">{product.sku}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{product.quantity} left</p>
                    <p className="text-sm text-muted-foreground">
                      Reorder at {product.reorder_level}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="border-red-500/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600">
            <AlertTriangle className="h-5 w-5" />
            Out of Stock ({outOfStock.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {outOfStock.length === 0 ? (
            <p className="text-muted-foreground">No out of stock items</p>
          ) : (
            <div className="space-y-2">
              {outOfStock.map((product) => (
                <div
                  key={product.id}
                  className="flex items-center justify-between p-3 bg-red-500/10 rounded-lg"
                >
                  <div>
                    <p className="font-medium">{product.name}</p>
                    <p className="text-sm text-muted-foreground">{product.sku}</p>
                  </div>
                  <Button size="sm">Restock</Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
