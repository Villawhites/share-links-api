from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import User, Connection
from app.schemas import ConnectionCreate, ConnectionResponse
import uuid

router = APIRouter(prefix="/connections", tags=["connections"])

@router.get("/", response_model=list[ConnectionResponse])
def get_connections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las conexiones del usuario"""
    
    connections = db.query(Connection).filter(
        (Connection.user_id_1 == current_user.id) | (Connection.user_id_2 == current_user.id)
    ).all()
    
    return connections

@router.post("/", response_model=ConnectionResponse)
def create_connection(
    connection_data: ConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear solicitud de conexión"""
    
    if connection_data.user_id_2 == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes conectarte contigo mismo"
        )
    
    # Verificar que el otro usuario existe
    other_user = db.query(User).filter(User.id == connection_data.user_id_2).first()
    if not other_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Ordenar los IDs para evitar duplicados
    user_1 = min(current_user.id, connection_data.user_id_2)
    user_2 = max(current_user.id, connection_data.user_id_2)
    
    # Verificar que no exista ya
    existing = db.query(Connection).filter(
        Connection.user_id_1 == user_1,
        Connection.user_id_2 == user_2
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La conexión ya existe"
        )
    
    new_connection = Connection(
        user_id_1=user_1,
        user_id_2=user_2,
        status="pending"
    )
    
    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)
    
    return new_connection

@router.put("/{connection_id}/accept", response_model=ConnectionResponse)
def accept_connection(
    connection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aceptar solicitud de conexión"""
    
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
            detail="No tienes permiso para aceptar esta conexión"
        )
    
    connection.status = "accepted"
    db.commit()
    db.refresh(connection)
    
    return connection