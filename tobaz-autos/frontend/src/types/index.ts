// User types
export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: 'admin' | 'staff' | 'manager';
  phone?: string;
  profile_image?: string;
  address?: string;
  is_active: boolean;
  date_joined: string;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

// Category types
export interface Category {
  id: string;
  name: string;
  slug: string;
  category_type: 'car' | 'part' | 'tool' | 'oil' | 'accessory' | 'other';
  description?: string;
  icon?: string;
  color: string;
  is_active: boolean;
  product_count: number;
  created_at: string;
}

// Product types
export interface Product {
  id: string;
  sku: string;
  name: string;
  slug: string;
  description?: string;
  category?: string;
  category_name?: string;
  cost_price: number;
  selling_price: number;
  quantity: number;
  reorder_level: number;
  reorder_quantity: number;
  stock_status: 'in_stock' | 'low_stock' | 'out_of_stock';
  profit_margin: number;
  inventory_value?: number;
  brand?: string;
  model?: string;
  year?: number;
  condition: 'new' | 'used' | 'refurbished';
  mileage?: number;
  fuel_type?: string;
  transmission?: string;
  color?: string;
  vin?: string;
  featured_image?: string;
  images: string[];
  meta_title?: string;
  meta_description?: string;
  meta_keywords?: string;
  status: 'active' | 'inactive' | 'discontinued';
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

// Customer types
export interface Customer {
  id: string;
  customer_type: 'individual' | 'business';
  first_name: string;
  last_name: string;
  full_name: string;
  email?: string;
  phone: string;
  alternate_phone?: string;
  address?: string;
  city?: string;
  state?: string;
  company_name?: string;
  tax_id?: string;
  notes?: string;
  is_active: boolean;
  total_purchases: number;
  total_spent: number;
  created_at: string;
}

// Sale types
export interface SaleItem {
  id: string;
  product?: string;
  product_name: string;
  product_image?: string;
  product_sku?: string;
  quantity: number;
  unit_price: number;
  unit_cost: number;
  total_price: number;
  total_cost: number;
  discount: number;
}

export interface Payment {
  id: string;
  amount: number;
  payment_method: string;
  reference_number?: string;
  notes?: string;
  payment_date: string;
  received_by?: string;
  received_by_name?: string;
  created_at: string;
}

export interface Sale {
  id: string;
  order_number: string;
  customer?: Customer;
  status: 'pending' | 'confirmed' | 'processing' | 'shipped' | 'delivered' | 'completed' | 'cancelled' | 'refunded';
  payment_status: 'pending' | 'partial' | 'paid' | 'refunded';
  payment_method: 'cash' | 'transfer' | 'card' | 'check' | 'installment';
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  shipping_cost: number;
  total_amount: number;
  total_cost: number;
  profit: number;
  amount_paid: number;
  amount_due: number;
  order_date: string;
  due_date?: string;
  completed_at?: string;
  delivery_address?: string;
  delivery_notes?: string;
  customer_notes?: string;
  staff_notes?: string;
  items: SaleItem[];
  payments: Payment[];
  created_at: string;
  updated_at: string;
}

// Shipment types
export interface ShipmentItem {
  id: string;
  product?: string;
  product_name: string;
  product_sku?: string;
  quantity: number;
  unit_cost: number;
  total_cost: number;
  description?: string;
}

export interface ShipmentTracking {
  id: string;
  status: string;
  location?: string;
  description: string;
  tracking_date: string;
  created_by?: string;
  created_by_name?: string;
  created_at: string;
}

export interface Shipment {
  id: string;
  tracking_number: string;
  shipment_type: 'loading' | 'receiving';
  origin_country: string;
  origin_city?: string;
  destination_country: string;
  destination_city?: string;
  shipping_method: 'air' | 'sea' | 'land';
  carrier?: string;
  estimated_arrival?: string;
  actual_arrival?: string;
  shipping_cost: number;
  customs_duty: number;
  insurance_cost: number;
  other_costs: number;
  total_cost: number;
  status: 'pending' | 'in_transit' | 'customs' | 'received' | 'cancelled';
  invoice_file?: string;
  bill_of_lading?: string;
  customs_document?: string;
  other_documents: string[];
  notes?: string;
  items: ShipmentItem[];
  tracking_updates: ShipmentTracking[];
  created_by?: string;
  created_by_name?: string;
  received_by?: string;
  received_by_name?: string;
  received_at?: string;
  is_overdue: boolean;
  days_in_transit: number;
  created_at: string;
  updated_at: string;
}

// Expense types
export interface ExpenseCategory {
  id: string;
  name: string;
  description?: string;
  color: string;
  icon?: string;
  is_active: boolean;
  expense_count: number;
  total_spent: number;
  created_at: string;
}

export interface Expense {
  id: string;
  expense_number: string;
  category?: string;
  category_name?: string;
  category_color?: string;
  title: string;
  description?: string;
  amount: number;
  date: string;
  payment_method: 'cash' | 'transfer' | 'card' | 'check';
  reference_number?: string;
  receipt_image?: string;
  receipt_file?: string;
  status: 'pending' | 'approved' | 'paid' | 'rejected';
  approved_by?: string;
  approved_by_name?: string;
  approved_at?: string;
  rejection_reason?: string;
  created_by_name?: string;
  created_at: string;
}

// Dashboard types
export interface DashboardStats {
  products: {
    total: number;
    low_stock: number;
    out_of_stock: number;
  };
  sales: {
    today: { amount: number; count: number };
    month: { amount: number; count: number };
    year: { amount: number; count: number };
  };
  profit: {
    today: number;
    month: number;
  };
  shipments: {
    pending: number;
    received_this_month: number;
  };
  expenses: {
    month: number;
  };
  inventory_value: number;
  categories: Array<{
    name: string;
    product_count: number;
  }>;
}

// Chart data types
export interface ChartData {
  labels: string[];
  data: number[];
}

export interface SalesChartData {
  labels: string[];
  revenue: number[];
  profit: number[];
  count: number[];
}

// Notification types
export interface Notification {
  id: string;
  title: string;
  message: string;
  notification_type: 'info' | 'success' | 'warning' | 'error';
  is_read: boolean;
  link?: string;
  created_at: string;
}

// Activity log types
export interface ActivityLog {
  id: string;
  user?: string;
  user_name?: string;
  action: 'create' | 'update' | 'delete' | 'login' | 'logout' | 'view';
  entity_type: string;
  entity_id?: string;
  description: string;
  ip_address?: string;
  created_at: string;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

// Filter types
export interface ProductFilters {
  search?: string;
  category?: string;
  status?: string;
  condition?: string;
  stock_status?: string;
  min_price?: number;
  max_price?: number;
}

export interface SaleFilters {
  search?: string;
  status?: string;
  payment_status?: string;
  payment_method?: string;
  start_date?: string;
  end_date?: string;
}

export interface ShipmentFilters {
  search?: string;
  shipment_type?: string;
  status?: string;
  shipping_method?: string;
}

export interface ExpenseFilters {
  search?: string;
  category?: string;
  status?: string;
  payment_method?: string;
  start_date?: string;
  end_date?: string;
}
