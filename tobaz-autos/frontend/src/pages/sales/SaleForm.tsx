import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { salesApi } from '@/lib/api'

export default function SaleForm() {
  const navigate = useNavigate()
  const [items, setItems] = useState([{ product: '', quantity: 1, unit_price: 0 }])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await salesApi.createSale({ items })
      toast.success('Sale created')
      navigate('/sales')
    } catch (error) {
      toast.error('Failed to create sale')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-3xl font-bold">New Sale</h1>
      </div>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Sale Items</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {items.map((item, index) => (
              <div key={index} className="grid grid-cols-3 gap-4">
                <div>
                  <Label>Product</Label>
                  <Input placeholder="Product name" />
                </div>
                <div>
                  <Label>Quantity</Label>
                  <Input type="number" min="1" defaultValue="1" />
                </div>
                <div>
                  <Label>Price</Label>
                  <Input type="number" min="0" step="0.01" />
                </div>
              </div>
            ))}
            <Button
              type="button"
              variant="outline"
              onClick={() => setItems([...items, { product: '', quantity: 1, unit_price: 0 }])}
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Item
            </Button>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4 mt-6">
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>
            Cancel
          </Button>
          <Button type="submit">Create Sale</Button>
        </div>
      </form>
    </div>
  )
}
