from sqlalchemy import create_engine
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker
from models import (
    Base, ONG, Proyecto, PlanTrabajo, Etapa, PedidoCobertura, TipoCobertura,
    Compromiso, ConsejoDirectivo, User, Observacion
)

# ==============================
# Configuración de la base de datos
# ==============================
engine = create_engine("sqlite:///test.db")
Base.metadata.create_all(engine)  # 🔹 CREA LAS TABLAS SI NO EXISTEN

Session = sessionmaker(bind=engine)
session = Session()

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# ==============================
# Limpiar tablas para evitar duplicados
# ==============================
for table in reversed(Base.metadata.sorted_tables):
    try:
        session.execute(table.delete())
    except Exception as e:
        print(f"⚠️ No se pudo limpiar {table.name}: {e}")
session.commit()

# ==============================
# Crear datos de ejemplo
# ==============================

# --- ONGs ---
ong1 = ONG(nombre="ONG Esperanza")
ong2 = ONG(nombre="Fundación Luz")
session.add_all([ong1, ong2])
session.commit()  # IDs generados

# --- Tipos de cobertura ---
tipo1 = TipoCobertura(nombre="Salud")
tipo2 = TipoCobertura(nombre="Educación")
session.add_all([tipo1, tipo2])
session.commit()

# --- Consejo Directivo ---
consejo = ConsejoDirectivo(nombre="Consejo Central")
session.add(consejo)
session.commit()

# --- Usuarios ---
user1 = User(
    nombre="Ana",
    apellido="Pérez",
    edad=30,
    email="ana@ejemplo.com",
    password=pwd_context.hash("123"),
    ong=ong1,          # pertenece a ONG
    consejo=None       # no pertenece al consejo
)

user2 = User(
    nombre="Luis",
    apellido="Gómez",
    edad=40,
    email="luis@ejemplo.com",
    password=pwd_context.hash("123"),
    ong=ong2,          # pertenece a ONG
    consejo=None       # no pertenece al consejo
)

admin_user = User(
    nombre="admin",
    apellido="Administrador",
    edad=35,
    email="admin@ejemplo.com",
    password=pwd_context.hash("123"),
    ong=None,          # no pertenece a ONG
    consejo=consejo    # pertenece al consejo
)

session.add_all([user1, user2, admin_user])
session.commit()

# --- Proyectos (creados por usuarios de ONG) ---
proy1 = Proyecto(nombre="Proyecto Agua Limpia", creador=ong1)
proy2 = Proyecto(nombre="Proyecto Escuelas Verdes", creador=ong2)
session.add_all([proy1, proy2])
session.commit()

# --- Relación Many-to-Many (ONG participa en proyectos) ---
ong1.proyectos.append(proy1)
ong2.proyectos.append(proy2)
ong1.proyectos.append(proy2)
session.commit()

# --- Planes de trabajo ---
plan1 = PlanTrabajo(nombre="Plan Fase 1", proyecto=proy1)
plan2 = PlanTrabajo(nombre="Plan Educación Ambiental", proyecto=proy2)
session.add_all([plan1, plan2])
session.commit()

# --- Etapas ---
etapa1 = Etapa(nombre="Diagnóstico", cumplida=True, proyecto=proy1)
etapa2 = Etapa(nombre="Ejecución", cumplida=False, proyecto=proy2)
session.add_all([etapa1, etapa2])
session.commit()

# --- Pedidos de cobertura ---
pedido1 = PedidoCobertura(
    descripcion="Cobertura médica para zona rural",
    proyecto=proy1,
    tipo_cobertura=tipo1
)
pedido2 = PedidoCobertura(
    descripcion="Materiales educativos",
    proyecto=proy2,
    tipo_cobertura=tipo2
)
session.add_all([pedido1, pedido2])
session.commit()

# --- Compromisos ---
comp1 = Compromiso(descripcion="Proveer filtros de agua", proyecto=proy1)
comp2 = Compromiso(descripcion="Capacitaciones mensuales", proyecto=proy2)
session.add_all([comp1, comp2])
session.commit()

# --- Observaciones (hechas por el consejo, no por ONG) ---
obs1 = Observacion(descripcion="Buen progreso inicial", proyecto=proy1, consejo=consejo)
obs2 = Observacion(descripcion="Requiere más voluntarios", proyecto=proy2, consejo=consejo)
session.add_all([obs1, obs2])
session.commit()

print("✅ Base de datos creada y cargada con datos iniciales correctamente.")
print("👤 Usuarios:")
print("   - admin@ejemplo.com / 123 (Consejo Directivo)")
print("   - ana@ejemplo.com / 123 (ONG Esperanza)")
print("   - luis@ejemplo.com / 123 (Fundación Luz)")
