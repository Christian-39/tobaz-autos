import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Eye, Truck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { shipmentsApi } from '@/lib/api'
import { formatCurrency, formatDate } from '@/lib/utils'
import type { Shipment } from '@/types'

export default function Shipments() {
  const [shipments, setShipments] = useState<Shipment[]>([])

  useEffect(() => {
    fetchShipments()
  }, [])

  const fetchShipments = async () => {
    try {
      const response = await shipmentsApi.getShipments()
      setShipments((response as any).results || [])
    } catch (error) {
      console.error('Error fetching shipments:', error)
    }
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-500',
      in_transit: 'bg-blue-500',
      customs: 'bg-purple-500',
      received: 'bg-green-500',
      cancelled: 'bg-red-500',
    }
    return <Badge className={colors[status] || 'bg-gray-500'}>{status.replace('_', ' ')}</Badge>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Shipments</h1>
          <p className="text-muted-foreground mt-1">
            Track shipments and deliveries
          </p>
        </div>
        <Button asChild>
          <Link to="/shipments/new">
            <Plus className="mr-2 h-4 w-4" />
            New Shipment
          </Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Shipments</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Tracking #</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Route</TableHead>
                <TableHead>Est. Arrival</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {shipments.map((shipment) => (
                <TableRow key={shipment.id}>
                  <TableCell className="font-mono">{shipment.tracking_number}</TableCell>
                  <TableCell className="capitalize">{shipment.shipment_type}</TableCell>
                  <TableCell>
                    {shipment.origin_country} → {shipment.destination_country}
                  </TableCell>
                  <TableCell>
                    {shipment.estimated_arrival ? formatDate(shipment.estimated_arrival) : '-'}
                  </TableCell>
                  <TableCell>{getStatusBadge(shipment.status)}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon" asChild>
                      <Link to={`/shipments/${shipment.id}`}>
                        <Eye className="h-4 w-4" />
                      </Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
