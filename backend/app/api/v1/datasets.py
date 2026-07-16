from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.api import deps
from app.schemas.dataset import VoiceDatasetCreate, VoiceDatasetRead, VoiceDatasetItemCreate, VoiceDatasetItemRead
from app.models.voice import VoiceDataset, VoiceDatasetItem
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=VoiceDatasetRead, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    *,
    db: AsyncSession = Depends(deps.get_db),
    dataset_in: VoiceDatasetCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    dataset = VoiceDataset(
        user_id=current_user.id,
        name=dataset_in.name,
        description=dataset_in.description
    )
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    return dataset

@router.get("/{dataset_id}", response_model=VoiceDatasetRead)
async def read_dataset(
    *,
    db: AsyncSession = Depends(deps.get_db),
    dataset_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    query = select(VoiceDataset).options(selectinload(VoiceDataset.items)).where(VoiceDataset.id == dataset_id)
    result = await db.execute(query)
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return dataset

@router.post("/{dataset_id}/items", response_model=VoiceDatasetItemRead, status_code=status.HTTP_201_CREATED)
async def add_dataset_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    dataset_id: UUID,
    item_in: VoiceDatasetItemCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    # Verify dataset ownership
    dataset = await db.get(VoiceDataset, dataset_id)
    if not dataset or dataset.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    item = VoiceDatasetItem(
        dataset_id=dataset_id,
        file_asset_id=item_in.file_asset_id,
        category=item_in.category,
        emotion_tag=item_in.emotion_tag,
        quality_score=item_in.quality_score
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
