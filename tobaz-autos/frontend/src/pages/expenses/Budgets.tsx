import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { expensesApi } from '@/lib/api'
import { formatCurrency } from '@/lib/utils'

interface Budget {
  id: string
  title: string
  amount: number
  spent: number
  remaining: number
  percentage_used: number
  is_alert: boolean
}

export default function Budgets() {
  const [budgets, setBudgets] = useState<Budget[]>([])
  const [dialogOpen, setDialogOpen] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    amount: '',
    category: '',
    start_date: '',
    end_date: '',
  })

  useEffect(() => {
    fetchBudgets()
  }, [])

  const fetchBudgets = async () => {
    try {
      const response = await expensesApi.getBudgets()
      setBudgets((response as any).results || [])
    } catch (error) {
      toast.error('Failed to fetch budgets')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await expensesApi.createBudget({
        ...formData,
        amount: parseFloat(formData.amount),
      })
      toast.success('Budget created')
      setDialogOpen(false)
      fetchBudgets()
    } catch (error) {
      toast.error('Failed to create budget')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Budgets</h1>
          <p className="text-muted-foreground mt-1">Manage expense budgets</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Budget
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Budget</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label>Title</Label>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Amount</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  required
                />
              </div>
              <Button type="submit" className="w-full">Create</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {budgets.map((budget) => (
          <Card key={budget.id} className={budget.is_alert ? 'border-red-500' : ''}>
            <CardHeader>
              <CardTitle>{budget.title}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Budget</span>
                <span className="font-medium">{formatCurrency(budget.amount)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Spent</span>
                <span className="font-medium text-red-600">{formatCurrency(budget.spent)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Remaining</span>
                <span className="font-medium text-green-600">{formatCurrency(budget.remaining)}</span>
              </div>
              <Progress value={budget.percentage_used} />
              <p className="text-sm text-muted-foreground text-right">
                {budget.percentage_used.toFixed(1)}% used
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
