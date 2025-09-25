from sqlalchemy.orm import Session
from app.models.video import Video
from app.schemas.video import VideoCreate

def create_video(db: Session, video: VideoCreate) -> Video:
    db_video = Video(product_id=video.product_id, platform=video.platform, url=video.url)
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def get_videos_by_product(db: Session, product_id: int):
    return db.query(Video).filter(Video.product_id == product_id).all()

def get_video(db: Session, video_id: int):
    return db.query(Video).filter(Video.id == video_id).first()

def delete_video(db: Session, video_id: int):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        return None
    db.delete(video)
    db.commit()
    return video
