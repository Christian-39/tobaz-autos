import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Package,
  ShoppingCart,
  Truck,
  TrendingUp,
  TrendingDown,
  DollarSign,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { dashboardApi } from '@/lib/api'
import { formatCurrency, formatNumber } from '@/lib/utils'
import type { DashboardStats } from '@/types'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
    },
  },
}

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308']

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [salesChartData, setSalesChartData] = useState<any[]>([])
  const [inventoryChartData, setInventoryChartData] = useState<any[]>([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, salesChart, inventoryChart] = await Promise.all([
          dashboardApi.getStats(),
          dashboardApi.getSalesChart('month'),
          dashboardApi.getInventoryChart(),
        ])
        setStats(statsData as DashboardStats)
        setSalesChartData((salesChart as any).data || [])
        setInventoryChartData((inventoryChart as any).categories || [])
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  const statCards = [
    {
      title: 'Total Products',
      value: stats?.products.total || 0,
      icon: Package,
      change: '+12%',
      trend: 'up',
      color: 'bg-blue-500',
    },
    {
      title: 'Today\'s Sales',
      value: formatCurrency(stats?.sales.today.amount || 0),
      subtitle: `${stats?.sales.today.count || 0} orders`,
      icon: ShoppingCart,
      change: '+8%',
      trend: 'up',
      color: 'bg-green-500',
    },
    {
      title: 'Pending Shipments',
      value: stats?.shipments.pending || 0,
      icon: Truck,
      change: '-3%',
      trend: 'down',
      color: 'bg-orange-500',
    },
    {
      title: 'Monthly Profit',
      value: formatCurrency(stats?.profit.month || 0),
      icon: DollarSign,
      change: '+15%',
      trend: 'up',
      color: 'bg-purple-500',
    },
  ]

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Welcome back! Here's what's happening with your business.
          </p>
        </div>
        <Button>Generate Report</Button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, index) => (
          <motion.div key={stat.title} variants={itemVariants}>
            <Card className="card-hover">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <div className={`${stat.color} p-2 rounded-lg`}>
                  <stat.icon className="h-4 w-4 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                {stat.subtitle && (
                  <p className="text-xs text-muted-foreground">{stat.subtitle}</p>
                )}
                <div className="flex items-center gap-1 mt-2">
                  {stat.trend === 'up' ? (
                    <ArrowUpRight className="h-4 w-4 text-green-500" />
                  ) : (
                    <ArrowDownRight className="h-4 w-4 text-red-500" />
                  )}
                  <span
                    className={`text-xs ${
                      stat.trend === 'up' ? 'text-green-500' : 'text-red-500'
                    }`}
                  >
                    {stat.change}
                  </span>
                  <span className="text-xs text-muted-foreground">vs last month</span>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Alerts */}
      {(stats?.products.low_stock || 0) > 0 && (
        <motion.div variants={itemVariants}>
          <Card className="border-yellow-500/50 bg-yellow-500/5">
            <CardContent className="flex items-center gap-4 py-4">
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
              <div className="flex-1">
                <p className="font-medium">Low Stock Alert</p>
                <p className="text-sm text-muted-foreground">
                  {stats?.products.low_stock} products are running low on stock.
                </p>
              </div>
              <Button variant="outline" size="sm" asChild>
                <a href="/inventory/alerts">View Alerts</a>
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Sales Chart */}
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle>Sales Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={salesChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip
                      formatter={(value: number) => formatCurrency(value)}
                    />
                    <Bar dataKey="amount" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Inventory by Category */}
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle>Inventory by Category</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={inventoryChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) =>
                        `${name} ${(percent * 100).toFixed(0)}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="product_count"
                      nameKey="name"
                    >
                      {inventoryChartData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Inventory Value */}
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle>Inventory Value</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {formatCurrency(stats?.inventory_value || 0)}
              </div>
              <Progress value={75} className="mt-4" />
              <p className="text-sm text-muted-foreground mt-2">
                75% of annual budget used
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Monthly Expenses */}
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle>Monthly Expenses</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">
                {formatCurrency(stats?.expenses.month || 0)}
              </div>
              <div className="flex items-center gap-2 mt-4">
                <TrendingDown className="h-4 w-4 text-green-500" />
                <span className="text-sm text-green-500">-5%</span>
                <span className="text-sm text-muted-foreground">vs last month</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Stock Status */}
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle>Stock Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">In Stock</span>
                <span className="font-medium">
                  {formatNumber(
                    (stats?.products.total || 0) -
                      (stats?.products.low_stock || 0) -
                      (stats?.products.out_of_stock || 0)
                  )}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-yellow-600">Low Stock</span>
                <span className="font-medium text-yellow-600">
                  {formatNumber(stats?.products.low_stock || 0)}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-red-600">Out of Stock</span>
                <span className="font-medium text-red-600">
                  {formatNumber(stats?.products.out_of_stock || 0)}
                </span>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  )
}
