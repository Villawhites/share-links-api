from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import User, Connection, Collection
from app.schemas import CollectionCreate, CollectionResponse, CollectionUpdate
import uuid

router = APIRouter(prefix="/collections", tags=["collections"])

@router.get("/connection/{connection_id}", response_model=list[CollectionResponse])
def get_collections_by_connection(
    connection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las carpetas de una conexión"""
    
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conexión no encontrada"
        )
    
    # Verificar que el usuario sea parte de la conexión
    if connection.user_id_1 != current_user.id and connection.user_id_2 != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso"
        )
    
    collections = db.query(Collection).filter(
        Collection.connection_id == connection_id
    ).all()
    
    return collections

@router.post("/connection/{connection_id}", response_model=CollectionResponse)
def create_collection(
    connection_id: uuid.UUID,
    collection_data: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nueva carpeta en una conexión"""
    
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conexión no encontrada"
        )
    
    # Verificar que el usuario sea parte de la conexión
    if connection.user_id_1 != current_user.id and connection.user_id_2 != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso"
        )
    
    new_collection = Collection(
        connection_id=connection_id,
        name=collection_data.name,
        icon=collection_data.icon,
        created_by=current_user.id
    )
    
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)
    
    return new_collection

@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: uuid.UUID,
    collection_data: CollectionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualizar carpeta"""
    
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carpeta no encontrada"
        )
    
    # Cualquiera de los dos usuarios puede editar
    connection = db.query(Connection).filter(Connection.id == collection.connection_id).first()
    if connection.user_id_1 != current_user.id and connection.user_id_2 != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso"
        )
    
    if collection_data.name:
        collection.name = collection_data.name
    if collection_data.icon:
        collection.icon = collection_data.icon
    
    collection.version += 1
    db.commit()
    db.refresh(collection)
    
    return collection

@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar carpeta"""
    
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carpeta no encontrada"
        )
    
    connection = db.query(Connection).filter(Connection.id == collection.connection_id).first()
    if connection.user_id_1 != current_user.id and connection.user_id_2 != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso"
        )
    
    db.delete(collection)
    db.commit()