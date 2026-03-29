import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { shipmentsApi } from '@/lib/api'

export default function ShipmentForm() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    shipment_type: 'loading',
    origin_country: '',
    destination_country: 'Nigeria',
    shipping_method: 'sea',
    estimated_arrival: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await shipmentsApi.createShipment(formData)
      toast.success('Shipment created')
      navigate('/shipments')
    } catch (error) {
      toast.error('Failed to create shipment')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-3xl font-bold">New Shipment</h1>
      </div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Shipment Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Type</Label>
                <select
                  value={formData.shipment_type}
                  onChange={(e) => setFormData({ ...formData, shipment_type: e.target.value })}
                  className="w-full px-3 py-2 rounded-md border bg-background"
                >
                  <option value="loading">Loading Abroad</option>
                  <option value="receiving">Receiving in Nigeria</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label>Shipping Method</Label>
                <select
                  value={formData.shipping_method}
                  onChange={(e) => setFormData({ ...formData, shipping_method: e.target.value })}
                  className="w-full px-3 py-2 rounded-md border bg-background"
                >
                  <option value="air">Air Freight</option>
                  <option value="sea">Sea Freight</option>
                  <option value="land">Land Transport</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Origin Country</Label>
                <Input
                  value={formData.origin_country}
                  onChange={(e) => setFormData({ ...formData, origin_country: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Destination Country</Label>
                <Input
                  value={formData.destination_country}
                  onChange={(e) => setFormData({ ...formData, destination_country: e.target.value })}
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Estimated Arrival</Label>
              <Input
                type="date"
                value={formData.estimated_arrival}
                onChange={(e) => setFormData({ ...formData, estimated_arrival: e.target.value })}
              />
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4 mt-6">
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>
            Cancel
          </Button>
          <Button type="submit">Create Shipment</Button>
        </div>
      </form>
    </div>
  )
}
