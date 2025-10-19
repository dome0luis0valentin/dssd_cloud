from sqlalchemy import create_engine
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker
from models import Base, ONG, Proyecto, PlanTrabajo, Etapa, PedidoCobertura, TipoCobertura, Compromiso, ConsejoDirectivo, User, Observacion

# Conectar a la base de datos SQLite
engine = create_engine("sqlite:///test.db")
Base.metadata.create_all(engine)  # 🔹 CREA LAS TABLAS SI NO EXISTEN

Session = sessionmaker(bind=engine)
session = Session()

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


# --- Limpiar tablas para evitar duplicados ---
for table in reversed(Base.metadata.sorted_tables):
    try:
        session.execute(table.delete())
    except Exception as e:
        print(f"⚠️ No se pudo limpiar {table.name}: {e}")

# --- Crear datos de ejemplo ---

# ONG
ong1 = ONG(nombre="ONG Esperanza")
ong2 = ONG(nombre="Fundación Luz")

# Tipos de cobertura
tipo1 = TipoCobertura(nombre="Salud")
tipo2 = TipoCobertura(nombre="Educación")

# Consejo Directivo
consejo = ConsejoDirectivo(nombre="Consejo Central")

# Usuarios con contraseñas hasheadas
user1 = User(
    nombre="Ana", apellido="Pérez", edad=30,
    email="ana@ejemplo.com", password=pwd_context.hash("123"),
    ong=ong1, consejo=consejo
)
user2 = User(
    nombre="Luis", apellido="Gómez", edad=40,
    email="luis@ejemplo.com", password=pwd_context.hash("123"),
    ong=ong2, consejo=consejo
)

# Proyectos
proy1 = Proyecto(nombre="Proyecto Agua Limpia", creador=ong1)
proy2 = Proyecto(nombre="Proyecto Escuelas Verdes", creador=ong2)

# Relación Many-to-Many (ONG participa en proyectos)
ong1.proyectos.append(proy1)
ong2.proyectos.append(proy2)
ong1.proyectos.append(proy2)  # ONG Esperanza también participa en el 2

# Planes de trabajo
plan1 = PlanTrabajo(nombre="Plan Fase 1", proyecto=proy1)
plan2 = PlanTrabajo(nombre="Plan Educación Ambiental", proyecto=proy2)

# Etapas
etapa1 = Etapa(nombre="Diagnóstico", cumplida=True, proyecto=proy1)
etapa2 = Etapa(nombre="Ejecución", cumplida=False, proyecto=proy2)

# Pedidos de cobertura
pedido1 = PedidoCobertura(descripcion="Cobertura médica para zona rural", proyecto=proy1, tipo_cobertura=tipo1)
pedido2 = PedidoCobertura(descripcion="Materiales educativos", proyecto=proy2, tipo_cobertura=tipo2)

# Compromisos
comp1 = Compromiso(descripcion="Proveer filtros de agua", proyecto=proy1)
comp2 = Compromiso(descripcion="Capacitaciones mensuales", proyecto=proy2)

# Observaciones
obs1 = Observacion(descripcion="Buen progreso inicial", proyecto=proy1, consejo=consejo)
obs2 = Observacion(descripcion="Requiere más voluntarios", proyecto=proy2, consejo=consejo)

# Agregar todo a la sesión
session.add_all([
    ong1, ong2, tipo1, tipo2, consejo,
    user1, user2,
    proy1, proy2,
    plan1, plan2,
    etapa1, etapa2,
    pedido1, pedido2,
    comp1, comp2,
    obs1, obs2
])

# Confirmar cambios
session.commit()
print("✅ Base de datos creada y cargada con datos iniciales correctamente.")
