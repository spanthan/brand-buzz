from sqlalchemy.orm import Session
from app.models.brand import Brand
from app.schemas.brand import BrandCreate

# CREATE
def create_brand(db: Session, brand: BrandCreate) -> Brand:
    db_brand = Brand(name=brand.name)
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

# READ (get all brands)
def get_brands(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Brand).offset(skip).limit(limit).all()

# READ (get by id)
def get_brand(db: Session, brand_id: int):
    return db.query(Brand).filter(Brand.id == brand_id).first()

# READ (get by name)
def get_brand_by_name(db: Session, name: str):
    return db.query(Brand).filter(Brand.name == name).first()

# UPDATE
def update_brand(db: Session, brand_id: int, new_name: str):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        return None
    brand.name = new_name
    db.commit()
    db.refresh(brand)
    return brand

# DELETE
def delete_brand(db: Session, brand_id: int):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        return None
    db.delete(brand)
    db.commit()
    return brand
