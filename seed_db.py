from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from models import (
    Base, ONG, User, ConsejoDirectivo, Proyecto, PlanTrabajo, Etapa,
    PedidoCobertura, TipoCobertura, Observacion
)

# ==============================
# Configuración DB
# ==============================
engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
session = Session()

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# ==============================
# LIMPIAR TABLAS
# ==============================
for table in reversed(Base.metadata.sorted_tables):
    try:
        session.execute(table.delete())
    except Exception as e:
        print(f"⚠️ No se pudo limpiar: {table.name} → {e}")
session.commit()

print("🧹 Datos anteriores eliminados.")

# ==============================
# CREAR 5 ONGs + 2 usuarios cada una
# ==============================

usuarios_ong = [
    ("Isabel", "Bissale", "isabel.bissale"),
    ("Jan", "Fisher", "jan.fisher"),
    ("Patrick", "Gardenier", "patrick.gardenier"),
    ("Thorsten", "Hartmann", "thorsten.hartmann"),
    ("Joseph", "Hovell", "joseph.hovell"),
    ("William", "Jobs", "william.jobs"),
    ("Virginie", "Jomphe", "virginie.jomphe"),
    ("Helen", "Kelly", "helen.kelly"),
    ("Carlos", "Mendez", "carlos.mendez"),
    ("Lucia", "Ramirez", "lucia.ramirez")
]

ong_objects = []

for i in range(5):
    ong = ONG(nombre=f"ONG{i+1}")
    session.add(ong)
    session.commit()
    ong_objects.append(ong)

    for j in range(2):
        idx = i * 2 + j
        nombre, apellido, username = usuarios_ong[idx]

        user = User(
            nombre=nombre,
            apellido=apellido,
            edad=28 + idx,
            email=f"{username}@correo.com",
            username=username,
            password=pwd_context.hash("admin"),
            ong_id=ong.id
        )
        session.add(user)
        session.commit()

    print(f"ONG creada: {ong.nombre} con usuarios {usuarios_ong[i*2][0]} y {usuarios_ong[i*2+1][0]}")

# ==============================
# CONSEJO DIRECTIVO (3 usuarios)
# ==============================

consejo = ConsejoDirectivo(nombre="Consejo Directivo Principal")
session.add(consejo)
session.commit()

miembros_cd = [
    ("Walter", "Bates", "walter.bates"),
    ("Daniela", "Angelo", "daniela.angelo"),
    ("Giovanna", "Almeida", "giovanna.almeida")
]

for i, (nombre, apellido, username) in enumerate(miembros_cd):
    user = User(
        nombre=nombre,
        apellido=apellido,
        edad=35 + i,
        email=f"{username}@consejo.com",
        username=username,
        password=pwd_context.hash("admin"),
        consejo_id=consejo.id,
        ong_id=None
    )
    session.add(user)
    session.commit()

print(f"Consejo creado: {consejo.nombre}")

# ==============================
# TIPOS DE COBERTURA
# ==============================

tipo1 = TipoCobertura(nombre="Salud")
tipo2 = TipoCobertura(nombre="Educación")
session.add_all([tipo1, tipo2])
session.commit()

# ==============================
# PROYECTOS (usamos las primeras 2 ONGs creadas)
# ==============================

ong1, ong2 = ong_objects[0], ong_objects[1]

proy1 = Proyecto(nombre="Proyecto Agua Limpia", creador=ong1)
proy2 = Proyecto(nombre="Proyecto Escuelas Verdes", creador=ong2)
session.add_all([proy1, proy2])
session.commit()

# Relación Many-to-Many
ong1.proyectos.append(proy1)
ong2.proyectos.append(proy2)
session.commit()

# ==============================
# PLANES DE TRABAJO
# ==============================

plan1 = PlanTrabajo(nombre="Plan Fase 1", proyecto=proy1)
plan2 = PlanTrabajo(nombre="Plan Educación Ambiental", proyecto=proy2)
session.add_all([plan1, plan2])
session.commit()

# ==============================
# ETAPAS
# ==============================

etapa1 = Etapa(nombre="Diagnóstico", cumplida=True, proyecto=proy1)
etapa2 = Etapa(nombre="Ejecución", cumplida=False, proyecto=proy2)
session.add_all([etapa1, etapa2])
session.commit()

# ==============================
# PEDIDOS DE COBERTURA
# ==============================

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

# ==============================
# OBSERVACIONES
# ==============================

obs1 = Observacion(
    descripcion="Buen progreso inicial",
    proyecto=proy1,
    consejo=consejo
)

obs2 = Observacion(
    descripcion="Requiere más voluntarios",
    proyecto=proy2,
    consejo=consejo
)

session.add_all([obs1, obs2])
session.commit()

# ==============================
# DONE ✔
# ==============================

print("✅ Base de datos inicial cargada exitosamente.")
print("👤 Usuarios de ONGs: contraseña = admin")
print("👤 Consejo Directivo: contraseña = admin")
