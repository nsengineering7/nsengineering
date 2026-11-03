"""
main.py
FastAPI application entry point for the Kharat precision engineering e-commerce backend.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import auth
import models
import schemas
from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_admin_user,
    get_current_user,
    get_password_hash,
    verify_password,
)
from database import Base, SessionLocal, engine, get_db

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Kharat Precision Engineering API",
    description="Backend API for the Kharat e-commerce platform",
    version="1.0.0",
)

# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Startup: create tables + seed default data
# ---------------------------------------------------------------------------

DEFAULT_SETTINGS = {
    "business_name": "Kharat",
    "tagline": "Precision Engineered. Delivered.",
    "description": (
        "Kharat is a premier lathe and precision engineering workshop delivering "
        "high-tolerance machined components, custom tooling, and industrial hardware. "
        "Built for engineers, by engineers."
    ),
    "phone": "+92-300-0000000",
    "email": "info@kharat.pk",
    "location": "Industrial Area, Lahore, Pakistan",
    "working_hours": "Mon-Sat: 8:00 AM - 6:00 PM",
    "established": "2010",
}

SAMPLE_PRODUCTS = [
    {
        "name": "4-Jaw Independent Lathe Chuck – 250mm",
        "description": (
            "Heavy-duty 4-jaw independent chuck with precision-ground jaws for gripping "
            "irregular and asymmetric workpieces. Suitable for manual lathes up to 500mm swing. "
            "Hardened steel body with anti-rust coating."
        ),
        "price": 18500.00,
        "stock_quantity": 12,
        "image_url": "/images/products/lathe-chuck-4jaw.jpg",
        "category": "Lathe Chucks & Accessories",
    },
    {
        "name": "3-Jaw Self-Centering Chuck – 200mm",
        "description": (
            "High-accuracy self-centering 3-jaw chuck with scroll plate mechanism. "
            "Ideal for round and hexagonal bar stock. Includes both standard and reverse jaws. "
            "Runout: ≤ 0.05 mm."
        ),
        "price": 12800.00,
        "stock_quantity": 20,
        "image_url": "/images/products/lathe-chuck-3jaw.jpg",
        "category": "Lathe Chucks & Accessories",
    },
    {
        "name": "Carbide Inserts – CNMG 120408 (Pack of 10)",
        "description": (
            "CNMG 120408 grade P25 carbide turning inserts with TiAlN PVD coating. "
            "Designed for medium to heavy-duty turning of steel and cast iron. "
            "ISO geometry with 80° diamond shape."
        ),
        "price": 3200.00,
        "stock_quantity": 80,
        "image_url": "/images/products/carbide-inserts-cnmg.jpg",
        "category": "Carbide Inserts & Tooling",
    },
    {
        "name": "Adjustable Boring Bar Set – 8pcs",
        "description": (
            "Eight-piece boring bar set with carbide tips, ranging from 6mm to 32mm bore diameter. "
            "Precision-ground shanks with CNC-milled pockets. "
            "Suitable for internal turning, facing, and profiling operations."
        ),
        "price": 8750.00,
        "stock_quantity": 15,
        "image_url": "/images/products/boring-bar-set.jpg",
        "category": "Boring Bars & Holders",
    },
    {
        "name": "ER32 Collet Set – 21pcs (1–20mm)",
        "description": (
            "Complete ER32 spring collet set covering 1mm to 20mm in 1mm increments. "
            "DIN 6499 compliant. Precision ground for concentricity within 0.008 mm. "
            "Suitable for CNC machining centres and manual milling machines."
        ),
        "price": 6400.00,
        "stock_quantity": 25,
        "image_url": "/images/products/er32-collet-set.jpg",
        "category": "Collets & Clamping",
    },
    {
        "name": "Digital Vernier Caliper – 0-300mm",
        "description": (
            "Stainless steel digital vernier caliper with LCD display and zero-setting function. "
            "Resolution: 0.01 mm. Measures outside, inside, depth, and step dimensions. "
            "IP54 dust and splash resistance. Includes carry case."
        ),
        "price": 4200.00,
        "stock_quantity": 30,
        "image_url": "/images/products/digital-caliper.jpg",
        "category": "Measuring Instruments",
    },
    {
        "name": "Water-Soluble Cutting Coolant – 5 Litres",
        "description": (
            "High-performance semi-synthetic metalworking coolant concentrate. "
            "Mix ratio 1:20 with water for general machining. "
            "Anti-rust, anti-corrosion, low-foam formula. "
            "Compatible with aluminium, steel, and cast iron."
        ),
        "price": 2200.00,
        "stock_quantity": 50,
        "image_url": "/images/products/cutting-coolant.jpg",
        "category": "Coolants & Lubricants",
    },
    {
        "name": "HSS Twist Drill Bit Set – 19pcs (1–10mm)",
        "description": (
            "Professional high-speed steel (HSS-Co 5%) fully ground drill bit set. "
            "Sizes 1mm to 10mm in 0.5mm increments. "
            "135° split-point tip for accurate start. "
            "Suitable for steel, stainless steel, and non-ferrous metals. "
            "Stored in indexed metal case."
        ),
        "price": 3900.00,
        "stock_quantity": 40,
        "image_url": "/images/products/hss-drill-set.jpg",
        "category": "Cutting Tools",
    },
]


@app.on_event("startup")
def startup_event() -> None:
    """Create database tables and seed initial data on application startup."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # ── Seed store settings ──────────────────────────────────────────────
        if db.query(models.StoreSettings).count() == 0:
            for key, value in DEFAULT_SETTINGS.items():
                db.add(models.StoreSettings(key=key, value=value))
            db.commit()

        # ── Seed default admin user ──────────────────────────────────────────
        admin_email = "admin@kharat.pk"
        if not db.query(models.User).filter(models.User.email == admin_email).first():
            admin_user = models.User(
                email=admin_email,
                full_name="Kharat Admin",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
            )
            db.add(admin_user)
            db.commit()

        # ── Seed sample products ─────────────────────────────────────────────
        if db.query(models.Product).count() == 0:
            for product_data in SAMPLE_PRODUCTS:
                db.add(models.Product(**product_data))
            db.commit()

    finally:
        db.close()


# ===========================================================================
# Auth routes  /api/auth
# ===========================================================================

auth_router_prefix = "/api/auth"


@app.post(f"{auth_router_prefix}/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists",
        )
    new_user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_admin=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post(f"{auth_router_prefix}/token", response_model=schemas.Token)
def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2-compatible token endpoint. Accepts form data (username/password)."""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserOut.model_validate(user),
    )


@app.post(f"{auth_router_prefix}/login", response_model=schemas.Token)
def login_json(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    """JSON body login endpoint. Accepts {email, password}."""
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        user=schemas.UserOut.model_validate(user),
    )


@app.get(f"{auth_router_prefix}/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user


# ===========================================================================
# Products routes  /api/products
# ===========================================================================

products_prefix = "/api/products"


@app.get(f"{products_prefix}/", response_model=List[schemas.ProductOut])
def list_products(
    search: Optional[str] = Query(None, description="Search in product name and description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    db: Session = Depends(get_db),
):
    """List all active products with optional filtering."""
    query = db.query(models.Product).filter(models.Product.is_active == True)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            models.Product.name.ilike(pattern) | models.Product.description.ilike(pattern)
        )
    if category:
        query = query.filter(models.Product.category == category)
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)

    return query.order_by(models.Product.created_at.desc()).all()


@app.get(f"{products_prefix}/{{product_id}}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Retrieve a single product by ID."""
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.is_active == True,
    ).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@app.post(f"{products_prefix}/", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(get_current_admin_user),
):
    """Create a new product (admin only)."""
    new_product = models.Product(**product_in.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.put(f"{products_prefix}/{{product_id}}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    product_in: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(get_current_admin_user),
):
    """Update an existing product (admin only)."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    product.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(product)
    return product


@app.delete(f"{products_prefix}/{{product_id}}", status_code=status.HTTP_200_OK)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(get_current_admin_user),
):
    """Soft-delete a product by setting is_active=False (admin only)."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    product.is_active = False
    product.updated_at = datetime.utcnow()
    db.commit()
    return {"detail": "Product deactivated successfully", "id": product_id}


# ===========================================================================
# Orders routes  /api/orders
# ===========================================================================

orders_prefix = "/api/orders"


@app.post(f"{orders_prefix}/", response_model=schemas.OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new order from a list of cart items (requires login)."""
    total_amount = 0.0
    order_items: List[models.OrderItem] = []

    for item_in in order_in.items:
        product = db.query(models.Product).filter(
            models.Product.id == item_in.product_id,
            models.Product.is_active == True,
        ).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {item_in.product_id} not found or unavailable",
            )
        if product.stock_quantity < item_in.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product '{product.name}'. Available: {product.stock_quantity}",
            )
        total_amount += product.price * item_in.quantity
        order_items.append(
            models.OrderItem(
                product_id=product.id,
                quantity=item_in.quantity,
                unit_price=product.price,
            )
        )

    # Create order
    new_order = models.Order(
        user_id=current_user.id,
        status=models.OrderStatus.pending,
        total_amount=round(total_amount, 2),
        shipping_address=order_in.shipping_address,
    )
    db.add(new_order)
    db.flush()  # Get new_order.id without committing

    # Attach items and decrement stock
    for item in order_items:
        item.order_id = new_order.id
        db.add(item)
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if product:
            product.stock_quantity -= item.quantity

    db.commit()
    db.refresh(new_order)
    return new_order


@app.get(f"{orders_prefix}/my", response_model=List[schemas.OrderOut])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Return all orders belonging to the authenticated user."""
    return (
        db.query(models.Order)
        .filter(models.Order.user_id == current_user.id)
        .order_by(models.Order.created_at.desc())
        .all()
    )


@app.get(f"{orders_prefix}/", response_model=List[schemas.OrderOut])
def list_all_orders(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(get_current_admin_user),
):
    """List all orders in the system (admin only)."""
    return db.query(models.Order).order_by(models.Order.created_at.desc()).all()


@app.get(f"{orders_prefix}/{{order_id}}", response_model=schemas.OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Retrieve a single order. The order owner or an admin may access it."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this order",
        )
    return order


@app.put(f"{orders_prefix}/{{order_id}}/status", response_model=schemas.OrderOut)
def update_order_status(
    order_id: int,
    status_in: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(get_current_admin_user),
):
    """Update the status of an order (admin only)."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.status = status_in.status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order


# ===========================================================================
# Store Settings routes  /api/settings
# ===========================================================================

settings_prefix = "/api/settings"


@app.get(f"{settings_prefix}/", response_model=Dict[str, Any])
def get_settings(db: Session = Depends(get_db)):
    """Return all store settings as a flat key-value dictionary."""
    settings = db.query(models.StoreSettings).all()
    return {s.key: s.value for s in settings}


@app.put(f"{settings_prefix}/", response_model=Dict[str, Any])
def update_settings(
    updates: Dict[str, Any],
    db: Session = Depends(get_db),
    _admin: models.User = Depends(get_current_admin_user),
):
    """
    Update one or more store settings (admin only).
    Body: {key: value, ...}
    New keys are created automatically.
    """
    for key, value in updates.items():
        setting = db.query(models.StoreSettings).filter(models.StoreSettings.key == key).first()
        if setting:
            setting.value = str(value)
            setting.updated_at = datetime.utcnow()
        else:
            db.add(models.StoreSettings(key=key, value=str(value)))

    db.commit()
    # Return updated full settings dict
    all_settings = db.query(models.StoreSettings).all()
    return {s.key: s.value for s in all_settings}


# ===========================================================================
# Admin Dashboard routes  /api/admin
# ===========================================================================

admin_prefix = "/api/admin"


@app.get(f"{admin_prefix}/stats", response_model=schemas.AdminStats)
def get_admin_stats(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(get_current_admin_user),
):
    """Return high-level dashboard statistics (admin only)."""
    total_products = db.query(models.Product).filter(models.Product.is_active == True).count()
    total_users = db.query(models.User).count()
    total_orders = db.query(models.Order).count()

    revenue_result = db.query(models.Order).filter(
        models.Order.status != models.OrderStatus.cancelled
    ).all()
    total_revenue = sum(o.total_amount for o in revenue_result)

    pending_orders = db.query(models.Order).filter(
        models.Order.status == models.OrderStatus.pending
    ).count()

    recent_orders = (
        db.query(models.Order)
        .order_by(models.Order.created_at.desc())
        .limit(5)
        .all()
    )

    return schemas.AdminStats(
        total_products=total_products,
        total_users=total_users,
        total_orders=total_orders,
        total_revenue=round(total_revenue, 2),
        pending_orders=pending_orders,
        recent_orders=[schemas.OrderOut.model_validate(o) for o in recent_orders],
    )


@app.get(f"{admin_prefix}/users", response_model=List[schemas.UserOut])
def list_all_users(
    db: Session = Depends(get_db),
    _admin: models.User = Depends(get_current_admin_user),
):
    """List all registered users (admin only)."""
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


@app.put(f"{admin_prefix}/users/{{user_id}}/toggle-admin", response_model=schemas.UserOut)
def toggle_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin_user),
):
    """Toggle the admin status of a user (admin only). Cannot demote yourself."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own admin status",
        )
    user.is_admin = not user.is_admin
    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Health-check endpoint
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok", "service": "Kharat API"}
