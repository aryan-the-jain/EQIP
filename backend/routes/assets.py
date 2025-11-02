from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..services.database import SessionLocal, engine
from ..services.database import Base
from ..schemas.schemas import AssetCreate, AssetOut
from ..models import models as m

router = APIRouter(tags=["assets"])

Base.metadata.create_all(bind=engine)

def db():
    d = SessionLocal()
    try:
        yield d
    finally:
        d.close()

@router.post("/assets", response_model=AssetOut)
def create_asset(payload: AssetCreate, session: Session = Depends(db)):
    asset = m.Asset(type=payload.type, uri=payload.uri)
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return AssetOut(asset_id=asset.id)
