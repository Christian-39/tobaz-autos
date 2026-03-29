import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Edit, Trash2, Package } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { productsApi } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'
import type { Product } from '@/types'

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProduct()
  }, [id])

  const fetchProduct = async () => {
    try {
      const data = await productsApi.getProduct(id!)
      setProduct(data as Product)
    } catch (error) {
      toast.error('Failed to fetch product')
      navigate('/products')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this product?')) return
    try {
      await productsApi.deleteProduct(id!)
      toast.success('Product deleted')
      navigate('/products')
    } catch (error) {
      toast.error('Failed to delete product')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!product) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" asChild>
            <Link to="/products">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{product.name}</h1>
            <p className="text-muted-foreground">{product.sku}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link to={`/products/${id}/edit`}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Link>
          </Button>
          <Button variant="destructive" onClick={handleDelete}>
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Product Image */}
        <Card>
          <CardContent className="p-6">
            {product.featured_image ? (
              <img
                src={product.featured_image}
                alt={product.name}
                className="w-full rounded-lg object-cover"
              />
            ) : (
              <div className="aspect-square rounded-lg bg-muted flex items-center justify-center">
                <Package className="h-16 w-16 text-muted-foreground" />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Product Info */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Product Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Category</p>
                <p className="font-medium">{product.category_name || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Condition</p>
                <p className="font-medium capitalize">{product.condition}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Brand</p>
                <p className="font-medium">{product.brand || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Model</p>
                <p className="font-medium">{product.model || '-'}</p>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Cost Price</p>
                  <p className="text-xl font-bold">
                    {formatCurrency(product.cost_price)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Selling Price</p>
                  <p className="text-xl font-bold text-green-600">
                    {formatCurrency(product.selling_price)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Profit Margin</p>
                  <p className="text-xl font-bold text-blue-600">
                    {product.profit_margin.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Quantity</p>
                  <p className="text-xl font-bold">{product.quantity}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <Badge
                    className={
                      product.status === 'active'
                        ? 'bg-green-500'
                        : product.status === 'inactive'
                        ? 'bg-gray-500'
                        : 'bg-red-500'
                    }
                  >
                    {product.status}
                  </Badge>
                </div>
              </div>
            </div>

            {product.description && (
              <div className="border-t pt-4">
                <p className="text-sm text-muted-foreground">Description</p>
                <p className="mt-1">{product.description}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
