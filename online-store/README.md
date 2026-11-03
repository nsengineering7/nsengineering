# ⚙ Kharat — Precision Engineering E-Commerce

A complete full-stack e-commerce web application for **Kharat**, a precision engineering and lathe workshop. Built with **FastAPI** (Python) on the backend and pure **HTML + Tailwind CSS + JavaScript** on the frontend.

---

## 📁 Project Structure

```
kharat_website/
├── start.sh                  # One-click startup script
├── README.md
│
├── backend/                  # FastAPI Python backend
│   ├── main.py               # App entry point, all API routes
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── auth.py               # JWT authentication helpers
│   ├── database.py           # SQLite + SQLAlchemy engine setup
│   ├── requirements.txt      # Python dependencies
│   └── kharat.db             # SQLite database (auto-created on first run)
│
└── frontend/                 # Static HTML/CSS/JS frontend
    ├── index.html            # 🏠 Homepage — hero, product grid, about
    ├── product.html          # 📦 Product detail page
    ├── cart.html             # 🛒 Shopping cart
    ├── login.html            # 🔐 User login
    ├── signup.html           # ✍️  User registration
    ├── checkout.html         # 💳 Checkout (requires login)
    ├── orders.html           # 📋 My orders (requires login)
    ├── admin.html            # 🛠️  Admin dashboard (requires admin role)
    └── js/
        └── utils.js          # Shared JS utilities (auth, cart, API, toast)
```

---

## 🚀 Quick Start

### Option A — Use the Startup Script (Recommended)

```bash
cd /home/noorullah751/Downloads/kharat_website
chmod +x start.sh
./start.sh
```

The script will:
1. Create a Python virtual environment inside `backend/.venv`
2. Install all dependencies from `requirements.txt`
3. Start the FastAPI server on **http://localhost:8000**

Then open `frontend/index.html` in your browser.

---

### Option B — Manual Setup

```bash
# 1. Set up backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Start backend server
uvicorn main:app --reload --port 8000

# 3. Open the frontend
# Just open frontend/index.html in your browser
```

---

## 🔑 Default Credentials

| Role  | Email              | Password   |
|-------|--------------------|------------|
| Admin | admin@kharat.pk    | `admin123` |

> ⚠️ Change the admin password after first login via the Admin → Users panel.

---

## 🌐 Pages & URLs

| Page | File | Access |
|------|------|--------|
| Homepage / Storefront | `frontend/index.html` | Public |
| Product Detail | `frontend/product.html?id=X` | Public |
| Shopping Cart | `frontend/cart.html` | Public |
| Login | `frontend/login.html` | Guest only |
| Sign Up | `frontend/signup.html` | Guest only |
| Checkout | `frontend/checkout.html` | Login required |
| My Orders | `frontend/orders.html` | Login required |
| Admin Dashboard | `frontend/admin.html` | Admin only |

---

## 🔌 API Endpoints

**Base URL:** `http://localhost:8000`  
**Interactive Docs:** `http://localhost:8000/docs`

### Auth `/api/auth`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | — | Create new user |
| POST | `/token` | — | OAuth2 form login → JWT |
| POST | `/login` | — | JSON body login → JWT |
| GET | `/me` | ✅ User | Get current user info |

### Products `/api/products`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | List products (`?search=&category=&min_price=&max_price=`) |
| GET | `/{id}` | — | Get single product |
| POST | `/` | 🔒 Admin | Create product |
| PUT | `/{id}` | 🔒 Admin | Update product |
| DELETE | `/{id}` | 🔒 Admin | Soft-delete product |

### Orders `/api/orders`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/` | ✅ User | Place new order |
| GET | `/my` | ✅ User | My order history |
| GET | `/` | 🔒 Admin | All orders |
| GET | `/{id}` | ✅ User | Single order (owner or admin) |
| PUT | `/{id}/status` | 🔒 Admin | Update order status |

### Store Settings `/api/settings`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | All settings as `{key: value}` |
| PUT | `/` | 🔒 Admin | Update settings |

### Admin `/api/admin`
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/stats` | 🔒 Admin | Dashboard stats |
| GET | `/users` | 🔒 Admin | All users |
| PUT | `/users/{id}/toggle-admin` | 🔒 Admin | Toggle admin status |

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, Uvicorn |
| Database | SQLite, SQLAlchemy 2.x |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Frontend | HTML5, Tailwind CSS (CDN), Vanilla JS |
| Icons | Lucide Icons (CDN) |
| Fonts | Inter (Google Fonts) |

---

## 🛠️ Admin Dashboard Features

Access at `frontend/admin.html` (login with admin credentials first):

- **📊 Overview** — Stats: total products, users, orders, revenue, pending orders + recent orders table
- **📦 Products** — Full CRUD: add, edit, delete products with modal form
- **🚚 Orders** — View all orders, update status (pending → confirmed → processing → shipped → delivered)
- **⚙️ Settings** — Edit all store info: name, tagline, description, contact details, working hours
- **👥 Users** — View all users, toggle admin privileges

---

## 🎨 Design System

- **Background:** Slate 900/800/700 (`#0f172a` / `#1e293b` / `#334155`)
- **Accent:** Amber 500/400 (`#f59e0b` / `#fbbf24`)
- **Style:** Industrial / precision engineering — sharp edges, grid patterns, amber glow effects
- **Font:** Inter (300–800 weights)

---

## 🔧 Customization

### Update Store Info
1. Log in as admin → go to **Admin Dashboard → Settings**
2. Update business name, tagline, contact info, hours, etc.
3. Click **Save Settings** — changes reflect on the homepage immediately

### Add Products
1. Admin Dashboard → **Products** tab → **"+ Add Product"**
2. Fill in name, price, description, stock, image URL, category
3. Products appear in the public storefront immediately

### Change Secret Key
Edit `backend/auth.py` — change `SECRET_KEY` to a strong random string before production deployment.

---

## 📦 Sample Products (Pre-seeded)

1. 4-Jaw Independent Lathe Chuck – 250mm — PKR 18,500
2. 3-Jaw Self-Centering Chuck – 200mm — PKR 12,800
3. Carbide Inserts CNMG 120408 (×10) — PKR 3,200
4. Adjustable Boring Bar Set – 8pcs — PKR 8,750
5. ER32 Collet Set – 21pcs — PKR 6,400
6. Digital Vernier Caliper – 0-300mm — PKR 4,200
7. Water-Soluble Cutting Coolant – 5L — PKR 2,200
8. HSS Twist Drill Bit Set – 19pcs — PKR 3,900
