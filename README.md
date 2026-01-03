Instrucciones para levantar el proyecto
# 1. Crear el venv en la carpeta del proyecto
python3 -m venv venv

# 2. Activar el venv
source venv/bin/activate

# Deberías ver "(venv)" al inicio del prompt
# villablanca@villawhite:~/share-links-api (venv)$ 

# 3. Ahora instala las dependencias
pip install -r requirements.txt

# 4. Verifica que se instaló correctamente
pip list

Crea un archivo .gitignore en la raíz del proyecto:
# En la carpeta share-links-api/
cat > .gitignore << 'EOF'
# Virtual Environment
venv/
env/
ENV/
.venv

1. Crear BD en PostgreSQL
bash
# Acceder a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE share_links_db;

# Salir
\q
2. Instalar dependencias
bash
pip install -r requirements.txt
3. Crear archivo .env con la config correcta
bash
cp .env .env.local  # si quieres duplicar
4. Levantar el servidor
bash
python run.py
Deberías ver:

vbnet
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
5. Acceder a Swagger
bash
http://localhost:8000/docs


DB URL="postgresql+asyncpg://share_user:tu_password_segura@localhost/share_links_db"
BD NAME:share_links_db
BD USER:share_user
BD USER PASS:123456789
BD HOST:localhost
DB PORT: 5432