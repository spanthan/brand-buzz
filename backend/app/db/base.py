from sqlalchemy.orm import declarative_base
from app.models.brand import Brand
from app.models.product import Product
from app.models.video import Video
from app.models.comment import Comment
from app.models.keyword import Keyword
from app.models.comment_keyword import CommentKeyword
from app.models.user import User

Base = declarative_base()
