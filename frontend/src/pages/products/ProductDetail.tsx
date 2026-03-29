import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Edit, Trash2, Package, Film, PlayCircle } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog'
import { productsApi } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  
  // State for the preview modal
  const [previewItem, setPreviewItem] = useState<{ type: 'image' | 'video', url: string } | null>(null)

  const getMediaUrl = (path: string | null | undefined) => {
    if (!path) return '';
    if (path.startsWith('http')) return path;
    return `http://127.0.0.1:8000${path.startsWith('/') ? '' : '/'}${path}`;
  };

  useEffect(() => {
    fetchProduct()
  }, [id])

  const fetchProduct = async () => {
    try {
      const data = await productsApi.getProduct(id!)
      setProduct(data)
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

  if (loading) return (
    <div className="flex items-center justify-center h-96">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
    </div>
  )

  if (!product) return null

  // Robust check for the images JSONField
  const galleryImages = Array.isArray(product.images) ? product.images : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" asChild>
            <Link to="/products"><ArrowLeft className="h-4 w-4" /></Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{product.name}</h1>
            <p className="text-muted-foreground">{product.sku || 'No SKU'}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link to={`/products/${id}/edit`}><Edit className="mr-2 h-4 w-4" /> Edit</Link>
          </Button>
          <Button variant="destructive" onClick={handleDelete}>
            <Trash2 className="mr-2 h-4 w-4" /> Delete
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column: Media Gallery */}
        <div className="space-y-6">
          {/* Compact Image Gallery */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-xs font-semibold uppercase tracking-wider flex items-center gap-2 text-muted-foreground">
                <Package className="h-3.5 w-3.5" /> Photos
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-4 gap-2">
                {/* 1. Show Gallery Images if they exist */}
                {galleryImages.length > 0 ? (
                  galleryImages.map((img: any, idx: number) => {
                    const path = typeof img === 'string' ? img : (img?.image || img?.url);
                    const url = getMediaUrl(path);
                    return (
                      <div 
                        key={idx} 
                        className="relative aspect-square cursor-zoom-in overflow-hidden rounded-md border bg-muted"
                        onClick={() => setPreviewItem({ type: 'image', url })}
                      >
                        <img src={url} className="h-full w-full object-cover hover:scale-110 transition-transform duration-300" alt="Product" />
                      </div>
                    )
                  })
                ) : product.featured_image ? (
                  /* 2. If gallery empty, show featured image as the thumbnail */
                  <div 
                    className="relative aspect-square cursor-zoom-in overflow-hidden rounded-md border bg-muted"
                    onClick={() => setPreviewItem({ type: 'image', url: getMediaUrl(product.featured_image) })}
                  >
                    <img src={getMediaUrl(product.featured_image)} className="h-full w-full object-cover" alt="Featured" />
                  </div>
                ) : (
                  <div className="col-span-4 py-4 text-center text-xs text-muted-foreground border border-dashed rounded-md">
                    No images available
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Compact Video Card */}
          {product.video && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-semibold uppercase tracking-wider flex items-center gap-2 text-muted-foreground">
                  <Film className="h-3.5 w-3.5" /> Video Preview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div 
                  className="group relative aspect-video cursor-pointer overflow-hidden rounded-md bg-black shadow-lg"
                  onClick={() => setPreviewItem({ type: 'video', url: getMediaUrl(product.video) })}
                >
                  <div className="absolute inset-0 z-10 flex items-center justify-center bg-black/30 transition-colors group-hover:bg-black/50">
                    <PlayCircle className="h-10 w-10 text-white/90" />
                  </div>
                  <video className="h-full w-full object-cover opacity-60">
                    <source src={getMediaUrl(product.video)} />
                  </video>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column: Details */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Product Information</CardTitle>
              <Badge className={product.status === 'active' ? 'bg-green-500' : 'bg-slate-500'}>
                {product.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-8">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-muted-foreground">Category</p>
                <p className="font-semibold">{product.category_name || 'Uncategorized'}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Condition</p>
                <p className="font-semibold capitalize">{product.condition}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Stock</p>
                <p className="font-semibold">{product.quantity} units</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-xl bg-muted/30 border">
              <div>
                <p className="text-sm text-muted-foreground">Selling Price</p>
                <p className="text-2xl font-bold text-green-600">{formatCurrency(product.selling_price)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Profit Margin</p>
                <p className="text-2xl font-bold text-blue-600">
                  {Number(product.profit_margin || 0).toFixed(1)}%
                </p>
              </div>
            </div>

            {product.description && (
              <div className="space-y-2">
                <p className="text-xs font-bold text-muted-foreground uppercase">Description</p>
                <div className="p-4 rounded-lg border bg-card text-sm leading-relaxed whitespace-pre-wrap">
                  {product.description}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Media Preview Modal */}
      <Dialog open={!!previewItem} onOpenChange={() => setPreviewItem(null)}>
        <DialogContent className="max-w-4xl border-none bg-transparent p-0 shadow-none outline-none overflow-hidden">
          <DialogTitle className="sr-only">Media Preview</DialogTitle>
          <div className="relative flex items-center justify-center bg-transparent">
            {previewItem?.type === 'image' ? (
              <img src={previewItem.url} className="max-h-[85vh] w-auto rounded-lg object-contain shadow-2xl" alt="Preview" />
            ) : (
              <video controls autoPlay className="max-h-[85vh] w-full rounded-lg shadow-2xl bg-black">
                <source src={previewItem?.url} type="video/mp4" />
              </video>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}