from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import User, Collection, Item, Connection
from app.schemas import ItemCreate, ItemResponse, ItemUpdate
from app.utils.metadata import extract_metadata, detect_platform
import uuid
import asyncio

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/collection/{collection_id}", response_model=list[ItemResponse])
def get_items_by_collection(
    collection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todos los items de una carpeta"""
    
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carpeta no encontrada"
        )
    
    # Verificar acceso
    connection = db.query(Connection).filter(Connection.id == collection.connection_id).first()
    if connection.user_id_1 != current_user.id and connection.user_id_2 != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso"
        )
    
    items = db.query(Item).filter(
        Item.collection_id == collection_id,
        Item.deleted_at == None
    ).all()
    
    return items

@router.post("/collection/{collection_id}", response_model=ItemResponse)
async def create_item(
    collection_id: uuid.UUID,
    item_data: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo item en una carpeta"""
    
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carpeta no encontrada"
        )
    
    # Verificar acceso
    connection = db.query(Connection).filter(Connection.id == collection.connection_id).first()
    if connection.user_id_1 != current_user.id and connection.user_id_2 != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso"
        )
    
    # Extraer metadata
    metadata = await extract_metadata(item_data.url)
    
    new_item = Item(
        collection_id=collection_id,
        url=item_data.url,
        title=item_data.title or metadata.get("title"),
        description=item_data.description or metadata.get("description"),
        thumbnail_url=metadata.get("thumbnail_url"),
        platform=metadata.get("platform"),
        created_by=current_user.id,
        metadata=metadata
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return new_item

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: uuid.UUID,
    item_data: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar item"""
    
    item = db.query(Item).filter(Item.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado"
        )
    
    # Verificar acceso
    collection = db.query(Collection).filter(Collection.id == item.collection_id).first()
    connection = db.query(Connection).filter(Connection.id == collection.connection_id).first()
    if connection.user_id_1 != current_user.id and connection.user_id_2 != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso"
        )
    
    if item_data.title:
        item.title = item_data.title
    if item_data.description:
        item.description = item_data.description
    
    item.version += 1
    db.commit()
    db.refresh(item)
    
    return item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar item (soft delete)"""
    
    item = db.query(Item).filter(Item.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado"
        )
    
    # Verificar acceso
    collection = db.query(Collection).filter(Collection.id == item.collection_id).first()
    connection = db.query(Connection).filter(Connection.id == collection.connection_id).first()
    if connection.user_id_1 != current_user.id and connection.user_id_2 != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso"
        )
    
    from datetime import datetime
    item.deleted_at = datetime.utcnow()
    item.version += 1
    db.commit()