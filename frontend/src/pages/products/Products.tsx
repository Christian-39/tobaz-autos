import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Edit,
  Trash2,
  Eye,
  AlertTriangle,
} from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { productsApi } from '@/lib/api'
import { formatCurrency, getStockStatusColor, truncateText } from '@/lib/utils'
import type { Product } from '@/types'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState({
    category: '',
    status: '',
    stock_status: '',
  })

  useEffect(() => {
    fetchProducts()
  }, [filters])

  const fetchProducts = async () => {
    try {
      const response = await productsApi.getProducts({
        search: searchQuery,
        ...filters,
      })
      setProducts((response as any).results || [])
    } catch (error) {
      toast.error('Failed to fetch products')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    fetchProducts()
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this product?')) return

    try {
      await productsApi.deleteProduct(id)
      toast.success('Product deleted successfully')
      fetchProducts()
    } catch (error) {
      toast.error('Failed to delete product')
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      active: 'bg-green-500',
      inactive: 'bg-gray-500',
      discontinued: 'bg-red-500',
    }
    return (
      <Badge className={variants[status] || 'bg-gray-500'}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    )
  }

  const getStockBadge = (status: string) => {
    const variants: Record<string, string> = {
      in_stock: 'bg-green-500',
      low_stock: 'bg-yellow-500',
      out_of_stock: 'bg-red-500',
    }
    return (
      <Badge className={variants[status] || 'bg-gray-500'}>
        {status.replace('_', ' ').charAt(0).toUpperCase() +
          status.replace('_', ' ').slice(1)}
      </Badge>
    )
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <motion.div
        variants={itemVariants}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div>
          <h1 className="text-3xl font-bold">Products</h1>
          <p className="text-muted-foreground mt-1">
            Manage your products and inventory
          </p>
        </div>
        <Button asChild>
          <Link to="/products/new">
            <Plus className="mr-2 h-4 w-4" />
            Add Product
          </Link>
        </Button>
      </motion.div>

      {/* Filters */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search products..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    className="pl-10"
                  />
                </div>
                <Button variant="outline" onClick={handleSearch}>
                  Search
                </Button>
              </div>
              <div className="flex gap-2">
                <select
                  value={filters.status}
                  onChange={(e) =>
                    setFilters({ ...filters, status: e.target.value })
                  }
                  className="px-3 py-2 rounded-md border bg-background"
                >
                  <option value="">All Status</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="discontinued">Discontinued</option>
                </select>
                <select
                  value={filters.stock_status}
                  onChange={(e) =>
                    setFilters({ ...filters, stock_status: e.target.value })
                  }
                  className="px-3 py-2 rounded-md border bg-background"
                >
                  <option value="">All Stock</option>
                  <option value="in_stock">In Stock</option>
                  <option value="low_stock">Low Stock</option>
                  <option value="out_of_stock">Out of Stock</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Products Table */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle>All Products</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
              </div>
            ) : products.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">No products found</p>
                <Button asChild className="mt-4">
                  <Link to="/products/new">Add your first product</Link>
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Product</TableHead>
                      <TableHead>SKU</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Price</TableHead>
                      <TableHead>Stock</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {products.map((product) => (
                      <TableRow key={product.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            {product.featured_image ? (
                              <img
                                src={product.featured_image}
                                alt={product.name}
                                className="h-10 w-10 rounded-lg object-cover"
                              />
                            ) : (
                              <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center">
                                <span className="text-xs text-muted-foreground">
                                  No img
                                </span>
                              </div>
                            )}
                            <div>
                              <p className="font-medium">{product.name}</p>
                              {product.stock_status === 'low_stock' && (
                                <p className="text-xs text-yellow-600 flex items-center gap-1">
                                  <AlertTriangle className="h-3 w-3" />
                                  Low stock
                                </p>
                              )}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {product.sku}
                        </TableCell>
                        <TableCell>{product.category_name || '-'}</TableCell>
                        <TableCell>
                          <div>
                            <p className="font-medium">
                              {formatCurrency(product.selling_price)}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Cost: {formatCurrency(product.cost_price)}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="font-medium">{product.quantity}</p>
                            {getStockBadge(product.stock_status)}
                          </div>
                        </TableCell>
                        <TableCell>{getStatusBadge(product.status)}</TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem asChild>
                                <Link to={`/products/${product.id}`}>
                                  <Eye className="mr-2 h-4 w-4" />
                                  View
                                </Link>
                              </DropdownMenuItem>
                              <DropdownMenuItem asChild>
                                <Link to={`/products/${product.id}/edit`}>
                                  <Edit className="mr-2 h-4 w-4" />
                                  Edit
                                </Link>
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={() => handleDelete(product.id)}
                                className="text-red-600"
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
