from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.crud import addon as crud
from src.app.database import get_db
from src.app.schemas.addon import AddonRead, AddonCreate, AddonUpdate

router = APIRouter(tags=["Addons"])


@router.post("/", response_model=AddonRead)
def create_addon(addon: AddonCreate, db: Session = Depends(get_db)):
    return crud.create_addon(db=db, addon=addon)


@router.get("/", response_model=List[AddonRead])
def get_all_addons(db: Session = Depends(get_db)):
    return crud.get_addons(db=db)


@router.put("/{addon_id}", response_model=AddonRead)
def update_addon(addon_id: int, updated_data: AddonUpdate, db: Session = Depends(get_db)):
    result = crud.update_addon(db=db, addon_id=addon_id, updated_data=updated_data)
    if not result:
        raise HTTPException(status_code=404, detail="Addon not found")
    return result


@router.delete("/{addon_id}", status_code=204)
def delete_addon(addon_id: int, db: Session = Depends(get_db)):
    if not crud.delete_addon(db=db, addon_id=addon_id):
        raise HTTPException(status_code=404, detail="Addon not found")

