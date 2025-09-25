from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.video import VideoCreate, VideoOut
from app.crud import video as crud_video
from app.api.deps import get_db

router = APIRouter(prefix="/videos", tags=["videos"])

@router.post("/", response_model=VideoOut)
def create_video(video: VideoCreate, db: Session = Depends(get_db)):
    return crud_video.create_video(db, video)

@router.get("/product/{product_id}", response_model=List[VideoOut])
def get_videos_by_product(product_id: int, db: Session = Depends(get_db)):
    return crud_video.get_videos_by_product(db, product_id)
