from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate

def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(name=product.name, brand_id=product.brand_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products_by_brand(db: Session, brand_id: int):
    return db.query(Product).filter(Product.brand_id == brand_id).all()

def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    db.delete(product)
    db.commit()
    return product
