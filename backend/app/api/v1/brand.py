from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.brand import BrandCreate, BrandOut
from app.crud import brand as crud_brand
from app.api.deps import get_db

router = APIRouter(prefix="/brands", tags=["brands"])

@router.post("/", response_model=BrandOut)
def create_brand(brand: BrandCreate, db: Session = Depends(get_db)):
    return crud_brand.create_brand(db, brand)

@router.get("/", response_model=List[BrandOut])
def read_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_brand.get_brands(db, skip=skip, limit=limit)

@router.get("/{brand_id}", response_model=BrandOut)
def read_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = crud_brand.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand
