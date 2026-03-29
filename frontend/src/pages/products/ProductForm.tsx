import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft, Loader2, Save, ImagePlus, Video, X, PlayCircle } from 'lucide-react'
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

// Ensure this matches your backend URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

  // UPDATED: Media states to handle arrays
  const [existingImages, setExistingImages] = useState<string[]>([])
  const [selectedImages, setSelectedImages] = useState<File[]>([])
  const [existingVideo, setExistingVideo] = useState<string | null>(null)
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null)

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
    if (isEditing) fetchProduct()
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

      // UPDATED: Handle potential array of images from backend
      if (p.images && Array.isArray(p.images)) {
          setExistingImages(p.images.map((img: any) => img.image || img))
      } else if (p.featured_image) {
          setExistingImages([p.featured_image])
      }
      
      if (p.video) setExistingVideo(p.video)

    } catch (error) {
      toast.error('Failed to fetch product')
      navigate('/products')
    } finally {
      setLoading(false)
    }
  }

  const getMediaUrl = (path: string) => {
    if (!path) return ''
    return path.startsWith('http') ? path : `${API_BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`
  }

  // UPDATED: Multi-image change handler
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const filesArray = Array.from(e.target.files)
      setSelectedImages((prev) => [...prev, ...filesArray])
    }
  }

  const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setSelectedVideo(e.target.files[0])
    }
  }

  const onSubmit = async (data: ProductFormData) => {
    try {
      setSaving(true)
      const formData = new FormData()

      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          formData.append(key, value.toString())
        }
      })

      // UPDATED: Handle Multi-Images
      selectedImages.forEach((file) => {
        formData.append('images', file) // Using 'images' key for multiple upload
      })

      // Also send existing image paths to keep (helps backend know which to delete)
      formData.append('existing_images', JSON.stringify(existingImages))

      // Handle Video
      if (selectedVideo) {
        formData.append('video', selectedVideo)
      } else if (!existingVideo && isEditing) {
        formData.append('video', '') 
      }

      if (isEditing) {
        await productsApi.updateProduct(id!, formData)
        toast.success('Product updated successfully')
      } else {
        await productsApi.createProduct(formData)
        toast.success('Product created successfully')
      }
      navigate('/products')
    } catch (error) {
      toast.error('Failed to save product')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <div className="flex items-center justify-center h-96"><Loader2 className="h-8 w-8 animate-spin" /></div>

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">{isEditing ? 'Edit Product' : 'Add Product'}</h1>
          <p className="text-muted-foreground mt-1">Manage your inventory details and media.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Basic Information */}
          <Card>
            <CardHeader><CardTitle>Basic Information</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Product Name *</Label>
                <Input id="name" {...register('name')} />
                {errors.name && <p className="text-sm text-red-500">{errors.name.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea id="description" {...register('description')} rows={4} />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Category</Label>
                  <Select onValueChange={(v) => setValue('category', v)} value={watch('category')}>
                    <SelectTrigger><SelectValue placeholder="Select" /></SelectTrigger>
                    <SelectContent>
                      {categories.map((cat) => (
                        <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Condition</Label>
                  <Select onValueChange={(v: any) => setValue('condition', v)} value={watch('condition')}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="new">New</SelectItem>
                      <SelectItem value="used">Used</SelectItem>
                      <SelectItem value="refurbished">Refurbished</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Brand</Label>
                  <Input {...register('brand')} />
                </div>
                <div className="space-y-2">
                  <Label>Model</Label>
                  <Input {...register('model')} />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Pricing & Inventory */}
          <Card>
            <CardHeader><CardTitle>Pricing & Inventory</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Cost Price ($)</Label>
                  <Input type="number" step="0.01" {...register('cost_price', { valueAsNumber: true })} />
                </div>
                <div className="space-y-2">
                  <Label>Selling Price ($)</Label>
                  <Input type="number" step="0.01" {...register('selling_price', { valueAsNumber: true })} />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Quantity</Label>
                  <Input type="number" {...register('quantity', { valueAsNumber: true })} />
                </div>
                <div className="space-y-2">
                  <Label>Reorder Level</Label>
                  <Input type="number" {...register('reorder_level', { valueAsNumber: true })} />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Status</Label>
                <Select onValueChange={(v: any) => setValue('status', v)} value={watch('status')}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
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

        {/* UPDATED: Media Card for Multi-Images */}
        <Card>
          <CardHeader><CardTitle>Product Media</CardTitle></CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              <Label>Product Images</Label>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {/* Existing Server Images */}
                {existingImages.map((url, index) => (
                  <div key={`existing-${index}`} className="relative h-32 border rounded-lg overflow-hidden bg-muted">
                    <img src={getMediaUrl(url)} className="h-full w-full object-cover" alt="Product" />
                    <Button 
                      type="button" variant="destructive" size="icon" className="absolute top-1 right-1 h-6 w-6"
                      onClick={() => setExistingImages(prev => prev.filter((_, i) => i !== index))}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                ))}

                {/* Newly Selected Local Images */}
                {selectedImages.map((file, index) => (
                  <div key={`selected-${index}`} className="relative h-32 border rounded-lg overflow-hidden bg-muted">
                    <img src={URL.createObjectURL(file)} className="h-full w-full object-cover" alt="Preview" />
                    <Button 
                      type="button" variant="destructive" size="icon" className="absolute top-1 right-1 h-6 w-6"
                      onClick={() => setSelectedImages(prev => prev.filter((_, i) => i !== index))}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                ))}

                {/* Upload Button */}
                <label className="flex flex-col items-center justify-center h-32 border-2 border-dashed rounded-lg cursor-pointer hover:bg-muted/50 transition-colors">
                  <ImagePlus className="h-8 w-8 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground mt-2">Add Image</span>
                  <input type="file" accept="image/*" multiple className="hidden" onChange={handleImageChange} />
                </label>
              </div>
            </div>

            <div className="space-y-3">
              <Label>Product Video</Label>
              <div className="relative h-48 w-full border-2 border-dashed rounded-lg flex items-center justify-center bg-muted/30 overflow-hidden">
                {selectedVideo || existingVideo ? (
                  <div className="flex flex-col items-center p-4">
                    <PlayCircle className="h-12 w-12 text-primary mb-2" />
                    <p className="text-xs text-center truncate max-w-[200px]">
                      {selectedVideo ? selectedVideo.name : 'Server-side Video'}
                    </p>
                    <Button 
                      type="button" variant="destructive" size="icon" className="absolute top-2 right-2 rounded-full h-8 w-8"
                      onClick={() => { setSelectedVideo(null); setExistingVideo(null); }}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ) : (
                  <label className="cursor-pointer flex flex-col items-center">
                    <Video className="h-10 w-10 text-muted-foreground mb-2" />
                    <span className="text-sm text-muted-foreground">Upload Video</span>
                    <input type="file" accept="video/*" className="hidden" onChange={handleVideoChange} />
                  </label>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-4 mt-6">
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>Cancel</Button>
          <Button type="submit" disabled={saving}>
            {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
            {isEditing ? 'Update Product' : 'Create Product'}
          </Button>
        </div>
      </form>
    </div>
  )
}