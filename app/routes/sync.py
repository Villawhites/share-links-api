from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import User, Item, Collection, SyncLog
from app.schemas import SyncDataRequest, SyncResponse
from datetime import datetime
import uuid

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/apply", response_model=SyncResponse)
def apply_sync(
    sync_data: SyncDataRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aplicar cambios offline al servidor
    Resuelve conflictos si existen
    """
    
    try:
        if sync_data.entity_type == "item":
            return handle_item_sync(sync_data, current_user, db)
        elif sync_data.entity_type == "collection":
            return handle_collection_sync(sync_data, current_user, db)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de entidad no válido"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def handle_item_sync(sync_data: SyncDataRequest, current_user: User, db: Session) -> dict:
    """Manejar sincronización de items"""
    
    existing = db.query(Item).filter(Item.id == sync_data.entity_id).first()
    
    # Detectar conflicto
    conflict = False
    if existing and existing.version > sync_data.data.get("version", 0):
        conflict = True
    
    if sync_data.operation == "create":
        if existing:
            return {
                "status": "conflict",
                "resolved_conflict": True,
                "server_data": serialize_item(existing),
                "message": "Item ya existe en el servidor"
            }
        
        new_item = Item(
            id=sync_data.entity_id,
            url=sync_data.data.get("url"),
            title=sync_data.data.get("title"),
            description=sync_data.data.get("description"),
            collection_id=sync_data.data.get("collection_id"),
            created_by=current_user.id,
            version=0
        )
        db.add(new_item)
    
    elif sync_data.operation == "update":
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item no encontrado"
            )
        
        if conflict:
            return {
                "status": "conflict",
                "resolved_conflict": True,
                "server_data": serialize_item(existing),
                "message": "Conflicto: versión del servidor es más nueva"
            }
        
        existing.title = sync_data.data.get("title", existing.title)
        existing.description = sync_data.data.get("description", existing.description)
        existing.version += 1
    
    elif sync_data.operation == "delete":
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item no encontrado"
            )
        
        existing.deleted_at = datetime.utcnow()
        existing.version += 1
    
    db.commit()
    
    # Registrar en sync log
    sync_log = SyncLog(
        user_id=current_user.id,
        entity_type=sync_data.entity_type,
        entity_id=sync_data.entity_id,
        operation=sync_data.operation,
        data=sync_data.data,
        timestamp=sync_data.timestamp,
        synced=True
    )
    db.add(sync_log)
    db.commit()
    
    if existing:
        db.refresh(existing)
        return {
            "status": "success",
            "resolved_conflict": conflict,
            "server_data": serialize_item(existing)
        }
    else:
        db.refresh(new_item)
        return {
            "status": "success",
            "resolved_conflict": False,
            "server_data": serialize_item(new_item)
        }

def handle_collection_sync(sync_data: SyncDataRequest, current_user: User, db: Session) -> dict:
    """Manejar sincronización de collections"""
    
    existing = db.query(Collection).filter(Collection.id == sync_data.entity_id).first()
    
    conflict = False
    if existing and existing.version > sync_data.data.get("version", 0):
        conflict = True
    
    if sync_data.operation == "create":
        if existing:
            return {
                "status": "conflict",
                "resolved_conflict": True,
                "server_data": serialize_collection(existing),
                "message": "Collection ya existe"
            }
        
        new_collection = Collection(
            id=sync_data.entity_id,
            name=sync_data.data.get("name"),
            icon=sync_data.data.get("icon"),
            connection_id=sync_data.data.get("connection_id"),
            created_by=current_user.id,
            version=0
        )
        db.add(new_collection)
    
    elif sync_data.operation == "update":
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection no encontrada"
            )
        
        if conflict:
            return {
                "status": "conflict",
                "resolved_conflict": True,
                "server_data": serialize_collection(existing),
                "message": "Conflicto: versión del servidor es más nueva"
            }
        
        existing.name = sync_data.data.get("name", existing.name)
        existing.icon = sync_data.data.get("icon", existing.icon)
        existing.version += 1
    
    db.commit()
    
    sync_log = SyncLog(
        user_id=current_user.id,
        entity_type=sync_data.entity_type,
        entity_id=sync_data.entity_id,
        operation=sync_data.operation,
        data=sync_data.data,
        timestamp=sync_data.timestamp,
        synced=True
    )
    db.add(sync_log)
    db.commit()
    
    if existing:
        db.refresh(existing)
        return {
            "status": "success",
            "resolved_conflict": conflict,
            "server_data": serialize_collection(existing)
        }
    else:
        db.refresh(new_collection)
        return {
            "status": "success",
            "resolved_conflict": False,
            "server_data": serialize_collection(new_collection)
        }

def serialize_item(item: Item) -> dict:
    return {
        "id": str(item.id),
        "collection_id": str(item.collection_id),
        "url": item.url,
        "title": item.title,
        "description": item.description,
        "thumbnail_url": item.thumbnail_url,
        "platform": item.platform,
        "created_by": str(item.created_by),
        "version": item.version,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
        "deleted_at": item.deleted_at.isoformat() if item.deleted_at else None
    }

def serialize_collection(collection: Collection) -> dict:
    return {
        "id": str(collection.id),
        "connection_id": str(collection.connection_id),
        "name": collection.name,
        "icon": collection.icon,
        "created_by": str(collection.created_by),
        "version": collection.version,
        "created_at": collection.created_at.isoformat(),
        "updated_at": collection.updated_at.isoformat()
    }