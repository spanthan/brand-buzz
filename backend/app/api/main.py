from fastapi import FastAPI
from app.api.v1 import brand, product, video, comment, keyword, user

app = FastAPI(title="BrandBuzz API", version="1.0.0")

# Register routers
app.include_router(brand.router)
app.include_router(product.router)
app.include_router(video.router)
app.include_router(comment.router)
app.include_router(keyword.router)
app.include_router(user.router)


# import os
# from sqlalchemy import create_engine, text

# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql://brandbuzz_user:brandbuzz_pass@localhost:5432/brandbuzz"
# )
# engine = create_engine(DATABASE_URL)

# with engine.connect() as conn:
#     result = conn.execute(text("SELECT 1;"))
#     print(result.fetchone())