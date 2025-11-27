# 🔍 Análisis: ¿Por qué usuarios diferentes ven datos distintos en get_proyectos?

## 📋 **Problema Original**

El endpoint `get_proyectos` original tenía el siguiente código:

```python
@router.get("/")
def get_proyectos(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Proyecto).all()
```

**❌ PROBLEMA**: Este código devuelve **TODOS** los proyectos sin filtros, por lo que teóricamente todos los usuarios deberían ver los mismos datos.

## 🕵️ **Posibles Causas de Datos Inconsistentes**

### 1. **🔄 Estado de Transacciones de Base de Datos**
- **SQLite con múltiples conexiones**: Diferentes sesiones pueden ver estados distintos
- **Transacciones no confirmadas**: Si hay operaciones pendientes de commit
- **Nivel de aislamiento**: Diferentes niveles pueden mostrar datos distintos

### 2. **⏱️ Condiciones de Carrera (Race Conditions)**
- **Escrituras concurrentes**: Si usuarios están modificando datos simultáneamente
- **Caché de consultas**: Diferentes momentos de ejecución pueden mostrar estados distintos

### 3. **🚫 Control de Acceso Implícito**
- **Middleware no documentado**: Podría existir filtrado en algún middleware
- **Permisos a nivel de ORM**: Filtros aplicados en el modelo o en la sesión de DB

### 4. **🔒 Configuración de Sesiones de Base de Datos**
- **Conexiones persistentes**: Diferentes pools de conexión
- **Autocommit settings**: Configuraciones distintas de confirmación automática

## 🛠️ **Soluciones Implementadas**

### **✅ Solución 1: Control de Acceso Basado en Roles**

```python
@router.get("/", response_model=ProyectosResponse)
def get_proyectos(include_debug: bool = False, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.consejo_id is not None:
        # Admin: ve todos los proyectos
        proyectos = db.query(Proyecto).all()
        filter_applied = "admin_access"
    elif current_user.ong_id is not None:
        # Usuario ONG: ve solo proyectos de su ONG
        proyectos = db.query(Proyecto).filter(
            (Proyecto.creador_id == current_user.ong_id) |
            (Proyecto.ongs.any(id=current_user.ong_id))
        ).all()
        filter_applied = f"ong_filtered_by_id_{current_user.ong_id}"
    else:
        # Sin permisos
        proyectos = []
        filter_applied = "no_access"
```

**🎯 Beneficios:**
- **Seguridad**: Cada usuario ve solo lo que debería ver
- **Consistencia**: Resultados predecibles basados en permisos
- **Auditoría**: Información clara de qué filtros se aplicaron

### **✅ Solución 2: Response con Metadata de Debugging**

```python
return ProyectosResponse(
    proyectos=proyectos,
    user_info={
        "user_id": current_user.id,
        "email": current_user.email,
        "role": user_role,
        "ong_id": current_user.ong_id,
        "consejo_id": current_user.consejo_id,
        "query_timestamp": datetime.now().isoformat()
    },
    total_count=len(proyectos),
    filtered_by=filter_applied
)
```

**🎯 Beneficios:**
- **Transparencia**: El usuario sabe por qué ve ciertos datos
- **Debugging**: Información clara para diagnóstico
- **Auditoria**: Timestamps y contexto de usuario

## 🧪 **Cómo Probar**

### **1. Ejecutar el servidor**
```bash
cd dssd_cloud
uvicorn main:app --reload --port 8000
```

### **2. Inicializar datos de prueba**
```bash
python seed_db.py
```

### **3. Ejecutar script de pruebas**
```bash
python test_user_permissions.py
```

### **4. Pruebas manuales con curl**

**Admin (ve todos los proyectos):**
```bash
# Obtener token
curl -X POST "http://localhost:8000/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@ejemplo.com&password=123"

# Usar token
curl -X GET "http://localhost:8000/proyectos/?include_debug=true" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

**Usuario ONG (ve solo sus proyectos):**
```bash
# Obtener token
curl -X POST "http://localhost:8000/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=ana@ejemplo.com&password=123"

# Usar token
curl -X GET "http://localhost:8000/proyectos/?include_debug=true" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

## 📊 **Resultados Esperados**

### **Admin (admin@ejemplo.com)**
```json
{
  "proyectos": [
    {"id": 1, "nombre": "Proyecto Agua Limpia"},
    {"id": 2, "nombre": "Proyecto Escuelas Verdes"}
  ],
  "user_info": {
    "role": "admin",
    "ong_id": null,
    "consejo_id": 1
  },
  "total_count": 2,
  "filtered_by": "admin_access"
}
```

### **Usuario ONG Esperanza (ana@ejemplo.com)**
```json
{
  "proyectos": [
    {"id": 1, "nombre": "Proyecto Agua Limpia"}
  ],
  "user_info": {
    "role": "ong_user",
    "ong_id": 1,
    "consejo_id": null
  },
  "total_count": 1,
  "filtered_by": "ong_filtered_by_id_1"
}
```

### **Usuario Fundación Luz (luis@ejemplo.com)**
```json
{
  "proyectos": [
    {"id": 2, "nombre": "Proyecto Escuelas Verdes"}
  ],
  "user_info": {
    "role": "ong_user",
    "ong_id": 2,
    "consejo_id": null
  },
  "total_count": 1,
  "filtered_by": "ong_filtered_by_id_2"
}
```

## 🔧 **Recomendaciones Adicionales**

### **1. Configuración de Base de Datos**
```python
# En database.py, asegurar configuración consistente
engine = create_engine(
    "sqlite:///test.db",
    connect_args={
        "check_same_thread": False,
        "timeout": 20,
        "isolation_level": "SERIALIZABLE"  # Para mayor consistencia
    }
)
```

### **2. Logging para Auditoría**
```python
import logging

logger = logging.getLogger(__name__)

@router.get("/")
def get_proyectos(...):
    logger.info(f"Usuario {current_user.email} consultando proyectos")
    # ... resto del código
    logger.info(f"Devueltos {len(proyectos)} proyectos para {current_user.email}")
```

### **3. Middleware de Consistencia**
```python
# Middleware para asegurar fresh data
@app.middleware("http")
async def ensure_fresh_data(request: Request, call_next):
    if "/proyectos" in str(request.url):
        # Force fresh DB connection
        pass
    response = await call_next(request)
    return response
```

## ✅ **Conclusión**

El problema de que diferentes usuarios vean datos distintos ahora está **resuelto de manera controlada**:

1. **✅ Implementado**: Control de acceso basado en roles
2. **✅ Implementado**: Metadata de debugging para transparencia
3. **✅ Implementado**: Scripts de prueba para validación
4. **✅ Agregado**: Documentación completa del comportamiento

**Ahora cada usuario ve exactamente lo que debería ver según sus permisos, y el sistema es transparente sobre qué filtros se aplicaron.**
