"""
schemas.py
Pydantic v2 schemas for the Kharat precision engineering e-commerce backend.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, field_validator

from models import OrderStatus


# ---------------------------------------------------------------------------
# User Schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserToggleAdminOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_admin: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Token Schemas
# ---------------------------------------------------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class TokenData(BaseModel):
    email: Optional[str] = None


# ---------------------------------------------------------------------------
# Product Schemas
# ---------------------------------------------------------------------------

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int = 0
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Price must be a non-negative value")
        return v

    @field_validator("stock_quantity")
    @classmethod
    def stock_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Stock quantity must be non-negative")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Price must be a non-negative value")
        return v

    @field_validator("stock_quantity")
    @classmethod
    def stock_must_be_non_negative(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Stock quantity must be non-negative")
        return v


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock_quantity: int
    image_url: Optional[str]
    category: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Order Schemas
# ---------------------------------------------------------------------------

class OrderItemIn(BaseModel):
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v


class OrderCreate(BaseModel):
    items: List[OrderItemIn]
    shipping_address: str

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: List[OrderItemIn]) -> List[OrderItemIn]:
        if not v:
            raise ValueError("Order must contain at least one item")
        return v


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    product: Optional[ProductOut] = None

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    shipping_address: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemOut] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Store Settings Schemas
# ---------------------------------------------------------------------------

class StoreSettingOut(BaseModel):
    id: int
    key: str
    value: Optional[str]
    updated_at: datetime

    model_config = {"from_attributes": True}


class StoreSettingUpdate(BaseModel):
    """
    Accepts an arbitrary dict of {key: value} pairs to update.
    Example body: {"business_name": "Kharat", "phone": "+92-300-1234567"}
    """
    model_config = {"extra": "allow"}

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


# ---------------------------------------------------------------------------
# Admin Stats Schema
# ---------------------------------------------------------------------------

class AdminStats(BaseModel):
    total_products: int
    total_users: int
    total_orders: int
    total_revenue: float
    pending_orders: int
    recent_orders: List[OrderOut]
