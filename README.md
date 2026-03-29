# Tobaz Autos Management System

A comprehensive, production-ready auto parts and vehicle management system built with Django and React.

## Features

### Admin Dashboard
- **Real-time Statistics**: View sales, inventory, shipments, and expenses at a glance
- **Interactive Charts**: Visualize sales trends and inventory distribution
- **Stock Alerts**: Get notified about low stock and out-of-stock products

### Product Management
- **CRUD Operations**: Create, read, update, and delete products
- **Categories**: Organize products by categories (Cars, Parts, Tools, Oil, Accessories)
- **Inventory Tracking**: Track stock levels, reorder points, and costs
- **SEO-Friendly**: Products have meta tags, slugs, and structured data
- **Image Upload**: Upload product images to Backblaze B2

### Inventory Management
- **Stock Tracking**: Real-time inventory levels
- **Stock Alerts**: Automatic alerts for low stock and out-of-stock items
- **Transactions**: Track all inventory movements
- **Suppliers**: Manage supplier information

### Shipment System
- **Loading Abroad**: Track shipments from international suppliers
- **Receiving in Nigeria**: Manage local deliveries
- **Status Tracking**: Track shipments through the entire process
- **Document Management**: Upload invoices, bills of lading, and customs documents
- **Automatic Inventory Update**: Update inventory when shipments are received

### Sales Tracking
- **Order Management**: Create and manage sales orders
- **Customer Management**: Store customer information and purchase history
- **Payment Tracking**: Track payments and outstanding balances
- **Profit Calculation**: Automatic profit calculation per sale
- **Invoices**: Generate and manage invoices

### Expense Tracking
- **Expense Categories**: Organize expenses by category
- **Receipt Upload**: Upload receipt images
- **Approval Workflow**: Expense approval system
- **Recurring Expenses**: Set up recurring expenses
- **Budgets**: Create and track budgets

### User Management
- **Role-Based Access**: Admin, Manager, and Staff roles
- **Profile Management**: Users can update their profiles and upload avatars
- **Activity Logging**: Track all user activities

### UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Mode**: Toggle between themes
- **Smooth Animations**: Page transitions, hover effects, and loading states
- **Modern UI**: Clean, premium interface with Tailwind CSS

## Tech Stack

### Backend
- **Django 4.2**: Python web framework
- **Django REST Framework**: API development
- **MySQL**: Database
- **JWT Authentication**: Secure token-based authentication
- **Backblaze B2**: Cloud storage for images and documents

### Frontend
- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **shadcn/ui**: UI components
- **Framer Motion**: Animations
- **Recharts**: Charts and graphs

## Project Structure

```
tobaz-autos/
├── backend/                    # Django backend
│   ├── tobaz_autos/           # Project settings
│   ├── core/                  # User authentication, activity logs
│   ├── inventory/             # Products, categories, suppliers
│   ├── sales/                 # Sales, customers, payments
│   ├── shipments/             # Shipments, tracking
│   ├── expenses/              # Expenses, budgets
│   ├── manage.py
│   ├── requirements.txt
│   └── build.sh               # Render build script
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── contexts/          # React contexts
│   │   ├── lib/               # Utilities and API
│   │   ├── types/             # TypeScript types
│   │   └── App.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── render.yaml                 # Render deployment config
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 20+
- MySQL 8.0+

### Backend Setup

1. **Create a virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create environment variables:**
```bash
cp .env.example .env
# Edit .env with your database credentials and other settings
```

4. **Set up the database:**
```bash
python manage.py migrate
```

5. **Create a superuser:**
```bash
python manage.py createsuperuser
```

6. **Run the development server:**
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Run the development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Environment Variables

Create a `.env` file in the backend directory with the following:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=tobaz_autos
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

# JWT
JWT_SECRET_KEY=your-jwt-secret

# Backblaze B2 (optional)
BACKBLAZE_B2_ENABLED=False
BACKBLAZE_B2_KEY_ID=your-key-id
BACKBLAZE_B2_APPLICATION_KEY=your-app-key
BACKBLAZE_B2_BUCKET_NAME=your-bucket
BACKBLAZE_B2_BUCKET_ENDPOINT=https://your-endpoint
```

## Database Schema

### Core Tables
- **users**: Custom user model with roles (admin, manager, staff)
- **activity_logs**: Track user activities
- **notifications**: User notifications
- **settings**: System settings

### Inventory Tables
- **categories**: Product categories
- **products**: Product information with SEO fields
- **inventory_transactions**: Stock movement history
- **suppliers**: Supplier information

### Sales Tables
- **customers**: Customer information
- **sales**: Sales orders
- **sale_items**: Items in each sale
- **payments**: Payment records
- **invoices**: Invoice records

### Shipment Tables
- **shipments**: Shipment information
- **shipment_items**: Items in each shipment
- **shipment_tracking**: Tracking updates

### Expense Tables
- **expense_categories**: Expense categories
- **expenses**: Expense records
- **recurring_expenses**: Recurring expense templates
- **budgets**: Budget records

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login
- `GET /api/auth/profile/` - Get profile
- `PUT /api/auth/profile/` - Update profile
- `POST /api/auth/profile/change-password/` - Change password
- `POST /api/auth/profile/upload-image/` - Upload profile image

### Products
- `GET /api/inventory/products/` - List products
- `POST /api/inventory/products/` - Create product
- `GET /api/inventory/products/{id}/` - Get product
- `PUT /api/inventory/products/{id}/` - Update product
- `DELETE /api/inventory/products/{id}/` - Delete product

### Sales
- `GET /api/sales/` - List sales
- `POST /api/sales/` - Create sale
- `GET /api/sales/{id}/` - Get sale
- `POST /api/sales/{id}/payments/` - Add payment

### Shipments
- `GET /api/shipments/` - List shipments
- `POST /api/shipments/` - Create shipment
- `POST /api/shipments/{id}/receive/` - Receive shipment

### Expenses
- `GET /api/expenses/` - List expenses
- `POST /api/expenses/` - Create expense
- `POST /api/expenses/{id}/approval/` - Approve/reject expense

### Dashboard
- `GET /api/dashboard/stats/` - Get dashboard statistics
- `GET /api/dashboard/charts/sales/` - Get sales chart data
- `GET /api/dashboard/charts/inventory/` - Get inventory chart data

## Deployment

### Render Deployment

1. **Create a new Web Service on Render:**
   - Connect your GitHub repository
   - Select the branch to deploy

2. **Configure the service:**
   - Build Command: `cd backend && chmod +x build.sh && ./build.sh`
   - Start Command: `cd backend && gunicorn tobaz_autos.wsgi:application --bind 0.0.0.0:$PORT`

3. **Add environment variables:**
   - Add all variables from your `.env` file
   - Render will automatically set `DATABASE_URL` if you create a managed database

4. **Create a MySQL database:**
   - You can use Render's managed MySQL or an external provider

The `render.yaml` file in the repository includes the configuration for automatic deployment.

### Manual Deployment

1. **Build the frontend:**
```bash
cd frontend
npm run build
```

2. **Collect static files:**
```bash
cd backend
python manage.py collectstatic --no-input
```

3. **Run migrations:**
```bash
python manage.py migrate
```

4. **Start the server:**
```bash
gunicorn tobaz_autos.wsgi:application --bind 0.0.0.0:8000
```

## Default Credentials

After setting up the backend, you can log in with:
- **Username**: admin
- **Password**: admin123

Make sure to change the default password after the first login.

## User Roles

- **Admin**: Full access to all features
- **Manager**: Can manage products, sales, shipments, and expenses
- **Staff**: Can view data and create sales

## Features in Detail

### SEO-Friendly Products
Products include:
- Meta title and description
- Meta keywords
- SEO-friendly URLs (slugs)
- Structured data for search engines

### Image Upload
- Upload product images, profile pictures, and documents
- Images are stored in Backblaze B2 (or locally in development)
- Automatic image optimization

### Notifications
- Real-time notifications for important events
- Stock alerts
- Shipment updates
- Expense approvals

### Activity Logging
- Track all user actions
- View activity history
- Audit trail for compliance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is proprietary software for Tobaz Autos.

## Support

For support, contact the development team or create an issue in the repository.

---

Built with ❤️ for Tobaz Autos
