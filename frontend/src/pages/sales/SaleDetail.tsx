import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { salesApi } from '@/lib/api'
import { formatCurrency, formatDateTime } from '@/lib/utils'
import type { Sale } from '@/types'

export default function SaleDetail() {
  const { id } = useParams()
  const [sale, setSale] = useState<Sale | null>(null)

  useEffect(() => {
    fetchSale()
  }, [id])

  const fetchSale = async () => {
    try {
      const data = await salesApi.getSale(id!)
      setSale(data as Sale)
    } catch (error) {
      console.error('Error fetching sale:', error)
    }
  }

  if (!sale) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" asChild>
          <Link to="/sales">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold">{sale.order_number}</h1>
          <p className="text-muted-foreground">{formatDateTime(sale.order_date)}</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Order Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Customer</span>
              <span className="font-medium">{sale.customer?.full_name || 'Walk-in'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status</span>
              <Badge>{sale.status}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Payment Status</span>
              <Badge>{sale.payment_status}</Badge>
            </div>
            <div className="border-t pt-4">
              <div className="flex justify-between text-lg font-bold">
                <span>Total</span>
                <span>{formatCurrency(sale.total_amount)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Items</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {sale.items?.map((item) => (
                <div key={item.id} className="flex justify-between py-2 border-b">
                  <div>
                    <p className="font-medium">{item.product_name}</p>
                    <p className="text-sm text-muted-foreground">
                      {item.quantity} x {formatCurrency(item.unit_price)}
                    </p>
                  </div>
                  <span className="font-medium">{formatCurrency(item.total_price)}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
