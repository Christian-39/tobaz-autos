import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft, Loader2, Save } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { productsApi } from '@/lib/api'
import type { Category } from '@/types'

const productSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  category: z.string().optional(),
  cost_price: z.number().min(0, 'Cost price must be positive'),
  selling_price: z.number().min(0, 'Selling price must be positive'),
  quantity: z.number().min(0, 'Quantity must be positive'),
  reorder_level: z.number().min(0),
  brand: z.string().optional(),
  model: z.string().optional(),
  condition: z.enum(['new', 'used', 'refurbished']),
  status: z.enum(['active', 'inactive', 'discontinued']),
})

type ProductFormData = z.infer<typeof productSchema>

export default function ProductForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const isEditing = !!id

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ProductFormData>({
    resolver: zodResolver(productSchema),
    defaultValues: {
      condition: 'new',
      status: 'active',
      cost_price: 0,
      selling_price: 0,
      quantity: 0,
      reorder_level: 10,
    },
  })

  useEffect(() => {
    fetchCategories()
    if (isEditing) {
      fetchProduct()
    }
  }, [id])

  const fetchCategories = async () => {
    try {
      const response = await productsApi.getCategories()
      setCategories((response as any).results || [])
    } catch (error) {
      toast.error('Failed to fetch categories')
    }
  }

  const fetchProduct = async () => {
    try {
      setLoading(true)
      const product = await productsApi.getProduct(id!)
      const p = product as any
      Object.keys(p).forEach((key) => {
        if (key in productSchema.shape) {
          setValue(key as keyof ProductFormData, p[key])
        }
      })
    } catch (error) {
      toast.error('Failed to fetch product')
      navigate('/products')
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (data: ProductFormData) => {
    try {
      setSaving(true)
      if (isEditing) {
        await productsApi.updateProduct(id!, data)
        toast.success('Product updated successfully')
      } else {
        await productsApi.createProduct(data)
        toast.success('Product created successfully')
      }
      navigate('/products')
    } catch (error) {
      toast.error(isEditing ? 'Failed to update product' : 'Failed to create product')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">
            {isEditing ? 'Edit Product' : 'Add Product'}
          </h1>
          <p className="text-muted-foreground mt-1">
            {isEditing
              ? 'Update product information'
              : 'Create a new product'}
          </p>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Product Name *</Label>
                <Input id="name" {...register('name')} />
                {errors.name && (
                  <p className="text-sm text-red-500">{errors.name.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea id="description" {...register('description')} rows={4} />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Select
                  onValueChange={(value) => setValue('category', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((cat) => (
                      <SelectItem key={cat.id} value={cat.id}>
                        {cat.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="brand">Brand</Label>
                  <Input id="brand" {...register('brand')} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="model">Model</Label>
                  <Input id="model" {...register('model')} />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="condition">Condition</Label>
                <Select
                  onValueChange={(value: any) => setValue('condition', value)}
                  defaultValue={watch('condition')}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="new">New</SelectItem>
                    <SelectItem value="used">Used</SelectItem>
                    <SelectItem value="refurbished">Refurbished</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Pricing & Inventory */}
          <Card>
            <CardHeader>
              <CardTitle>Pricing & Inventory</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="cost_price">Cost Price *</Label>
                  <Input
                    id="cost_price"
                    type="number"
                    step="0.01"
                    {...register('cost_price', { valueAsNumber: true })}
                  />
                  {errors.cost_price && (
                    <p className="text-sm text-red-500">
                      {errors.cost_price.message}
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="selling_price">Selling Price *</Label>
                  <Input
                    id="selling_price"
                    type="number"
                    step="0.01"
                    {...register('selling_price', { valueAsNumber: true })}
                  />
                  {errors.selling_price && (
                    <p className="text-sm text-red-500">
                      {errors.selling_price.message}
                    </p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="quantity">Quantity *</Label>
                  <Input
                    id="quantity"
                    type="number"
                    {...register('quantity', { valueAsNumber: true })}
                  />
                  {errors.quantity && (
                    <p className="text-sm text-red-500">
                      {errors.quantity.message}
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reorder_level">Reorder Level</Label>
                  <Input
                    id="reorder_level"
                    type="number"
                    {...register('reorder_level', { valueAsNumber: true })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="status">Status</Label>
                <Select
                  onValueChange={(value: any) => setValue('status', value)}
                  defaultValue={watch('status')}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                    <SelectItem value="discontinued">Discontinued</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-4 mt-6">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate(-1)}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={saving}>
            {saving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                {isEditing ? 'Update Product' : 'Create Product'}
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}
