import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Package } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { shipmentsApi } from '@/lib/api'
import { formatCurrency, formatDate } from '@/lib/utils'
import type { Shipment } from '@/types'

export default function ShipmentDetail() {
  const { id } = useParams()
  const [shipment, setShipment] = useState<Shipment | null>(null)

  useEffect(() => {
    fetchShipment()
  }, [id])

  const fetchShipment = async () => {
    try {
      const data = await shipmentsApi.getShipment(id!)
      setShipment(data as Shipment)
    } catch (error) {
      console.error('Error fetching shipment:', error)
    }
  }

  if (!shipment) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" asChild>
          <Link to="/shipments">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold">{shipment.tracking_number}</h1>
          <p className="text-muted-foreground capitalize">{shipment.shipment_type}</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Shipment Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status</span>
              <Badge>{shipment.status.replace('_', ' ')}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Origin</span>
              <span className="font-medium">{shipment.origin_country}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Destination</span>
              <span className="font-medium">{shipment.destination_country}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Shipping Method</span>
              <span className="font-medium capitalize">{shipment.shipping_method}</span>
            </div>
            <div className="border-t pt-4">
              <div className="flex justify-between text-lg font-bold">
                <span>Total Cost</span>
                <span>{formatCurrency(shipment.total_cost)}</span>
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
              {shipment.items?.map((item) => (
                <div key={item.id} className="flex justify-between py-2 border-b">
                  <div>
                    <p className="font-medium">{item.product_name}</p>
                    <p className="text-sm text-muted-foreground">Qty: {item.quantity}</p>
                  </div>
                  <span className="font-medium">{formatCurrency(item.total_cost)}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
