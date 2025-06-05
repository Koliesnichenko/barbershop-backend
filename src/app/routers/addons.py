from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.auth.dependencies import admin_required, get_current_user
from src.app.crud import addon as crud
from src.app.database import get_db
from src.app.models.user import User
from src.app.schemas.addon import AddonRead, AddonCreate, AddonUpdate

router = APIRouter(tags=["Addons"])


@router.post("/", response_model=AddonRead)
def create_addon(
        addon: AddonCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)):
    return crud.create_addon(db=db, addon=addon)


@router.get("/", response_model=List[AddonRead])
def get_all_addons(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud.get_addons(db=db)


@router.put("/{addon_id}", response_model=AddonRead)
def update_addon(
        addon_id: int,
        updated_data: AddonUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    result = crud.update_addon(db=db, addon_id=addon_id, updated_data=updated_data)
    if not result:
        raise HTTPException(status_code=404, detail="Addon not found")
    return result


@router.delete("/{addon_id}", status_code=204)
def delete_addon(
        addon_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    if not crud.delete_addon(db=db, addon_id=addon_id):
        raise HTTPException(status_code=404, detail="Addon not found")

