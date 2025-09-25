from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.product import ProductCreate, ProductOut
from app.crud import product as crud_product
from app.api.deps import get_db

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return crud_product.create_product(db, product)

@router.get("/brand/{brand_id}", response_model=List[ProductOut])
def get_products_by_brand(brand_id: int, db: Session = Depends(get_db)):
    return crud_product.get_products_by_brand(db, brand_id)
