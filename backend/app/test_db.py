from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.brand import Brand
from app.models.product import Product
from app.models.video import Video
from app.models.comment import Comment
from app.models.keyword import Keyword
from app.models.comment_keyword import CommentKeyword
from app.models.user import User
from app.core.security import get_password_hash


def run_test():
    db: Session = SessionLocal()

    # Clear old data for clean run
    db.query(CommentKeyword).delete()
    db.query(Comment).delete()
    db.query(Video).delete()
    db.query(Product).delete()
    db.query(Brand).delete()
    db.query(Keyword).delete()
    db.query(User).delete()
    db.commit()

    # Create Brand
    brand = Brand(name="CeraVe")
    db.add(brand)
    db.commit()
    db.refresh(brand)
    print(f"✅ Brand: {brand.name} (id={brand.id})")

    # Create Product
    product = Product(name="Moisturizing Cream", brand_id=brand.id)
    db.add(product)
    db.commit()
    db.refresh(product)
    print(f"✅ Product: {product.name} (id={product.id})")

    # Create Video
    video = Video(product_id=product.id, platform="YouTube", url="http://youtube.com/video1")
    db.add(video)
    db.commit()
    db.refresh(video)
    print(f"✅ Video: {video.url} (id={video.id})")

    # Create Comments
    comment1 = Comment(video_id=video.id, text="Love this cream, so hydrating!", sentiment="positive")
    comment2 = Comment(video_id=video.id, text="Made my skin break out", sentiment="negative")
    db.add_all([comment1, comment2])
    db.commit()
    db.refresh(comment1)
    db.refresh(comment2)
    print(f"✅ Comments inserted: {comment1.text[:20]}..., {comment2.text[:20]}...")

    # Create Keywords
    kw1 = Keyword(text="hydrating")
    kw2 = Keyword(text="breakout")
    db.add_all([kw1, kw2])
    db.commit()
    db.refresh(kw1)
    db.refresh(kw2)

    # Link Comment → Keyword
    ck1 = CommentKeyword(comment_id=comment1.id, keyword_id=kw1.id, weight=1.0)
    ck2 = CommentKeyword(comment_id=comment2.id, keyword_id=kw2.id, weight=0.9)
    db.add_all([ck1, ck2])
    db.commit()
    print("✅ Linked comments to keywords")

    # Query everything back
    print("\n📋 Final Data Snapshot:")
    for brand in db.query(Brand).all():
        print(f"Brand: {brand.name}")
        for product in brand.products:
            print(f"  Product: {product.name}")
            for video in product.videos:
                print(f"    Video: {video.url}")
                for comment in video.comments:
                    print(f"      Comment: {comment.text} ({comment.sentiment})")
                    for ck in comment.keywords:
                        print(f"        Keyword: {ck.keyword.text} (weight={ck.weight})")

    db.close()


if __name__ == "__main__":
    run_test()
