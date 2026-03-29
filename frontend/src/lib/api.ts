import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios'
import { toast } from 'sonner'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
      toast.error('Session expired. Please login again.')
    } else if (error.response?.status === 403) {
      toast.error('You do not have permission to perform this action.')
    } else if (error.response?.status === 404) {
      toast.error('Resource not found.')
    } else if (error.response?.status === 500) {
      toast.error('Server error. Please try again later.')
    } else if (error.message === 'Network Error') {
      toast.error('Network error. Please check your connection.')
    }
    return Promise.reject(error)
  }
)

// Generic API methods
export const apiService = {
  get: <T>(url: string, config?: AxiosRequestConfig) =>
    api.get<T>(url, config).then((res) => res.data),

  post: <T>(url: string, data?: any, config?: AxiosRequestConfig) => {
    const isFormData = data instanceof FormData;
    return api.post<T>(url, data, {
      ...config,
      headers: {
        ...config?.headers,
        ...(isFormData ? { 'Content-Type': 'multipart/form-data' } : { 'Content-Type': 'application/json' }),
      },
    }).then((res) => res.data);
  },

  // Smart PUT: Automatically detects FormData and sets the correct header
  put: <T>(url: string, data?: any, config?: AxiosRequestConfig) => {
    const isFormData = data instanceof FormData;
    return api.put<T>(url, data, {
      ...config,
      headers: {
        ...config?.headers,
        ...(isFormData ? { 'Content-Type': 'multipart/form-data' } : {}),
      },
    }).then((res) => res.data);
  },

  // Smart PATCH: Handles partial updates and file buffers reliably
  patch: <T>(url: string, data?: any, config?: AxiosRequestConfig) => {
    const isFormData = data instanceof FormData;
    return api.patch<T>(url, data, {
      ...config,
      headers: {
        ...config?.headers,
        ...(isFormData ? { 'Content-Type': 'multipart/form-data' } : {}),
      },
    }).then((res) => res.data);
  },

  delete: <T>(url: string, config?: AxiosRequestConfig) =>
    api.delete<T>(url, config).then((res) => res.data),

    upload: <T>(url: string, file: File, fieldName = 'image', method: 'post' | 'patch' = 'post') => {
    const formData = new FormData()
    formData.append(fieldName, file)
    return api[method]<T>(url, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((res) => res.data)
  },
}

// Auth API
export const authApi = {
  login: (credentials: { username: string; password: string }) =>
    apiService.post<{ token: string; user: unknown }>('/auth/login/', credentials),

  getProfile: () =>
    apiService.get<unknown>('/auth/profile/'),

  updateProfile: (data: unknown) =>
    apiService.patch<unknown>('/auth/profile/', data),

  changePassword: (data: { old_password: string; new_password: string }) =>
    apiService.post('/auth/profile/change-password/', data),

  uploadProfileImage: (file: File) =>
    apiService.upload('/auth/profile/upload-image/', file, 'image'),

  getUsers: (params?: unknown) =>
    apiService.get<unknown>('/auth/users/', { params }),

  createUser: (data: unknown) =>
    apiService.post('/auth/register/', data),

  updateUser: (id: string, data: unknown) =>
    apiService.patch(`/auth/users/${id}/`, data),

  deleteUser: (id: string) =>
    apiService.delete(`/auth/users/${id}/`),
}

// Dashboard API
export const dashboardApi = {
  getStats: () =>
    apiService.get<unknown>('/dashboard/stats/'),

  getSalesChart: (period = 'month') =>
    apiService.get<unknown>('/dashboard/charts/sales/', { params: { period } }),

  getInventoryChart: () =>
    apiService.get<unknown>('/dashboard/charts/inventory/'),
}

// Products API
export const productsApi = {
  getCategories: (params?: unknown) =>
    apiService.get<unknown>('/inventory/categories/', { params }),

  createCategory: (data: unknown) =>
    apiService.post('/inventory/categories/', data),

  updateCategory: (id: string, data: unknown) =>
    apiService.patch(`/inventory/categories/${id}/`, data),

  deleteCategory: (id: string) =>
    apiService.delete(`/inventory/categories/${id}/`),

  getProducts: (params?: unknown) =>
    apiService.get<unknown>('/inventory/products/', { params }),

  getProduct: (id: string) =>
    apiService.get<unknown>(`/inventory/products/${id}/`),

  getProductBySlug: (slug: string) =>
    apiService.get<unknown>(`/inventory/products/slug/${slug}/`),

  createProduct: (data: unknown) =>
    apiService.post('/inventory/products/', data),

  updateProduct: (id: string, data: unknown) =>
    apiService.patch(`/inventory/products/${id}/`, data),

  deleteProduct: (id: string) =>
    apiService.delete(`/inventory/products/${id}/`),

  uploadImage: (id: string, file: File) =>
    apiService.upload(`/inventory/products/${id}/upload-image/`, file, 'featured_image'),

  adjustStock: (id: string, data: { quantity: number; reason: string; reference?: string }) =>
    apiService.post(`/inventory/products/${id}/adjust-stock/`, data),

  getLowStockProducts: () =>
    apiService.get<unknown>('/inventory/products/low-stock/'),

  getOutOfStockProducts: () =>
    apiService.get<unknown>('/inventory/products/out-of-stock/'),

  getTransactions: (params?: unknown) =>
    apiService.get<unknown>('/inventory/transactions/', { params }),

  getSuppliers: (params?: unknown) =>
    apiService.get<unknown>('/inventory/suppliers/', { params }),

  createSupplier: (data: unknown) =>
    apiService.post('/inventory/suppliers/', data),

  updateSupplier: (id: string, data: unknown) =>
    apiService.patch(`/inventory/suppliers/${id}/`, data),

  deleteSupplier: (id: string) =>
    apiService.delete(`/inventory/suppliers/${id}/`),
}

// Sales API
export const salesApi = {
  getCustomers: (params?: unknown) =>
    apiService.get<unknown>('/sales/customers/', { params }),

  getCustomer: (id: string) =>
    apiService.get<unknown>(`/sales/customers/${id}/`),

  createCustomer: (data: unknown) =>
    apiService.post('/sales/customers/', data),

  updateCustomer: (id: string, data: unknown) =>
    apiService.patch(`/sales/customers/${id}/`, data),

  deleteCustomer: (id: string) =>
    apiService.delete(`/sales/customers/${id}/`),

  getSales: (params?: unknown) =>
    apiService.get<unknown>('/sales/', { params }),

  getSale: (id: string) =>
    apiService.get<unknown>(`/sales/${id}/`),

  createSale: (data: unknown) =>
    apiService.post('/sales/', data),

  updateSale: (id: string, data: unknown) =>
    apiService.patch(`/sales/${id}/`, data),

  deleteSale: (id: string) =>
    apiService.delete(`/sales/${id}/`),

  updateStatus: (id: string, data: { status: string; notes?: string }) =>
    apiService.post(`/sales/${id}/status/`, data),

  addPayment: (id: string, data: unknown) =>
    apiService.post(`/sales/${id}/payments/`, data),

  createInvoice: (id: string, data?: unknown) =>
    apiService.post(`/sales/${id}/invoice/`, data),

  getStats: () =>
    apiService.get<unknown>('/sales/stats/overview/'),

  getChart: (period = 'month') =>
    apiService.get<unknown>('/sales/stats/chart/', { params: { period } }),

  getTopCustomers: (limit = 10) =>
    apiService.get<unknown>('/sales/stats/top-customers/', { params: { limit } }),

  getTopProducts: (limit = 10) =>
    apiService.get<unknown>('/sales/stats/top-products/', { params: { limit } }),
}

// Shipments API
export const shipmentsApi = {
  getShipments: (params?: unknown) =>
    apiService.get<unknown>('/shipments/', { params }),

  getShipment: (id: string) =>
    apiService.get<unknown>(`/shipments/${id}/`),

  createShipment: (data: unknown) =>
    apiService.post('/shipments/', data),

  updateShipment: (id: string, data: unknown) =>
    apiService.patch(`/shipments/${id}/`, data),

  deleteShipment: (id: string) =>
    apiService.delete(`/shipments/${id}/`),

  updateStatus: (id: string, data: { status: string; notes?: string }) =>
    apiService.post(`/shipments/${id}/status/`, data),

  receiveShipment: (id: string, data?: unknown) =>
    apiService.post(`/shipments/${id}/receive/`, data),

  addTracking: (id: string, data: unknown) =>
    apiService.post(`/shipments/${id}/tracking/`, data),

  addItem: (id: string, data: unknown) =>
    apiService.post(`/shipments/${id}/items/`, data),

  removeItem: (id: string, itemId: string) =>
    apiService.delete(`/shipments/${id}/items/${itemId}/`),

  uploadDocument: (id: string, file: File, documentType: string) => {
    const formData = new FormData()
    formData.append('document', file)
    formData.append('document_type', documentType)
    return api.post(`/shipments/${id}/documents/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }).then((res) => res.data)
  },

  getPending: () =>
    apiService.get<unknown>('/shipments/pending/'),

  getOverdue: () =>
    apiService.get<unknown>('/shipments/overdue/'),

  getStats: () =>
    apiService.get<unknown>('/shipments/stats/overview/'),
}

// Expenses API
export const expensesApi = {
  getCategories: (params?: unknown) =>
    apiService.get<unknown>('/expenses/categories/', { params }),

  createCategory: (data: unknown) =>
    apiService.post('/expenses/categories/', data),

  updateCategory: (id: string, data: unknown) =>
    apiService.patch(`/expenses/categories/${id}/`, data),

  deleteCategory: (id: string) =>
    apiService.delete(`/expenses/categories/${id}/`),

  getExpenses: (params?: unknown) =>
    apiService.get<unknown>('/expenses/', { params }),

  getExpense: (id: string) =>
    apiService.get<unknown>(`/expenses/${id}/`),

  createExpense: (data: unknown) =>
    apiService.post('/expenses/', data),

  updateExpense: (id: string, data: unknown) =>
    apiService.patch(`/expenses/${id}/`, data),

  deleteExpense: (id: string) =>
    apiService.delete(`/expenses/${id}/`),

  approveExpense: (id: string, action: string, reason?: string) =>
    apiService.post(`/expenses/${id}/approval/`, { action, reason }),

  uploadReceipt: (id: string, file: File, receiptType = 'image') => {
    const formData = new FormData()
    formData.append('receipt', file)
    formData.append('receipt_type', receiptType)
    return api.post(`/expenses/${id}/receipt/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }).then((res) => res.data)
  },

  getRecurring: (params?: unknown) =>
    apiService.get<unknown>('/expenses/recurring/', { params }),

  createRecurring: (data: unknown) =>
    apiService.post('/expenses/recurring/', data),

  updateRecurring: (id: string, data: unknown) =>
    apiService.patch(`/expenses/recurring/${id}/`, data),

  deleteRecurring: (id: string) =>
    apiService.delete(`/expenses/recurring/${id}/`),

  generateFromRecurring: (id: string) =>
    apiService.post(`/expenses/recurring/${id}/generate/`),

  getBudgets: (params?: unknown) =>
    apiService.get<unknown>('/expenses/budgets/', { params }),

  createBudget: (data: unknown) =>
    apiService.post('/expenses/budgets/', data),

  updateBudget: (id: string, data: unknown) =>
    apiService.patch(`/expenses/budgets/${id}/`, data),

  deleteBudget: (id: string) =>
    apiService.delete(`/expenses/budgets/${id}/`),

  getStats: () =>
    apiService.get<unknown>('/expenses/stats/overview/'),

  getChart: (period = 'month') =>
    apiService.get<unknown>('/expenses/stats/chart/', { params: { period } }),
}

// Activity logs API
export const activityApi = {
  getLogs: (params?: unknown) =>
    apiService.get<unknown>('/auth/activity-logs/', { params }),
}

// Notifications API
export const notificationsApi = {
  getNotifications: () =>
    apiService.get<unknown>('/auth/notifications/'),

  markAsRead: (id: string) =>
    apiService.post(`/auth/notifications/${id}/read/`),
}

// Settings API
export const settingsApi = {
  getSettings: () =>
    apiService.get<unknown>('/auth/settings/'),

  updateSetting: (key: string, value: string) =>
    apiService.patch(`/auth/settings/${key}/`, { value }),
}

export default api;