import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Eye } from 'lucide-react'
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
import { salesApi } from '@/lib/api'
import { formatCurrency, formatDate } from '@/lib/utils'
import type { Sale } from '@/types'

export default function Sales() {
  const [sales, setSales] = useState<Sale[]>([])

  useEffect(() => {
    fetchSales()
  }, [])

  const fetchSales = async () => {
    try {
      const response = await salesApi.getSales()
      setSales((response as any).results || [])
    } catch (error) {
      console.error('Error fetching sales:', error)
    }
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-500',
      confirmed: 'bg-blue-500',
      processing: 'bg-purple-500',
      shipped: 'bg-indigo-500',
      delivered: 'bg-green-500',
      completed: 'bg-green-600',
      cancelled: 'bg-red-500',
      refunded: 'bg-gray-500',
    }
    return <Badge className={colors[status] || 'bg-gray-500'}>{status}</Badge>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Sales</h1>
          <p className="text-muted-foreground mt-1">
            Manage sales and orders
          </p>
        </div>
        <Button asChild>
          <Link to="/sales/new">
            <Plus className="mr-2 h-4 w-4" />
            New Sale
          </Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Sales</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order #</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Total</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sales.map((sale) => (
                <TableRow key={sale.id}>
                  <TableCell className="font-mono">{sale.order_number}</TableCell>
                  <TableCell>{sale.customer?.full_name || 'Walk-in'}</TableCell>
                  <TableCell>{formatDate(sale.order_date)}</TableCell>
                  <TableCell>{formatCurrency(sale.total_amount)}</TableCell>
                  <TableCell>{getStatusBadge(sale.status)}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon" asChild>
                      <Link to={`/sales/${sale.id}`}>
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
