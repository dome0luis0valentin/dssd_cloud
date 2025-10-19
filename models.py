from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table, Boolean, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Asociación Many-to-Many entre ONG y Proyecto (Participa)
ong_proyecto_participa = Table(
    'ong_proyecto_participa', Base.metadata,
    Column('ong_id', Integer, ForeignKey('ongs.id')),
    Column('proyecto_id', Integer, ForeignKey('proyectos.id'))
)

class ONG(Base):
    __tablename__ = 'ongs'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    proyectos = relationship('Proyecto', secondary=ong_proyecto_participa, back_populates='ongs')
    usuarios = relationship('User', back_populates='ong')  #  agregado para coherencia josue

class Proyecto(Base):
    __tablename__ = 'proyectos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    creador_id = Column(Integer, ForeignKey('ongs.id'))
    creador = relationship('ONG', backref='proyectos_creados')
    ongs = relationship('ONG', secondary=ong_proyecto_participa, back_populates='proyectos')
    planes_trabajo = relationship('PlanTrabajo', back_populates='proyecto')
    etapas = relationship('Etapa', back_populates='proyecto')
    pedidos_cobertura = relationship('PedidoCobertura', back_populates='proyecto')
    compromisos = relationship('Compromiso', back_populates='proyecto')
    observaciones = relationship('Observacion', back_populates='proyecto')  # 🔹 agregado para coherencia josue

class PlanTrabajo(Base):
    __tablename__ = 'planes_trabajo'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    proyecto_id = Column(Integer, ForeignKey('proyectos.id'))
    proyecto = relationship('Proyecto', back_populates='planes_trabajo')

class Etapa(Base):
    __tablename__ = 'etapas'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    cumplida = Column(Boolean, default=False, nullable=False)
    proyecto_id = Column(Integer, ForeignKey('proyectos.id'))
    proyecto = relationship('Proyecto', back_populates='etapas')

class PedidoCobertura(Base):
    __tablename__ = 'pedidos_cobertura'
    id = Column(Integer, primary_key=True)
    descripcion = Column(String)
    proyecto_id = Column(Integer, ForeignKey('proyectos.id'))
    proyecto = relationship('Proyecto', back_populates='pedidos_cobertura')
    tipo_cobertura_id = Column(Integer, ForeignKey('tipos_cobertura.id'))
    tipo_cobertura = relationship('TipoCobertura')

class TipoCobertura(Base):
    __tablename__ = 'tipos_cobertura'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)

class Compromiso(Base):
    __tablename__ = 'compromisos'
    id = Column(Integer, primary_key=True)
    descripcion = Column(String)
    proyecto_id = Column(Integer, ForeignKey('proyectos.id'))
    proyecto = relationship('Proyecto', back_populates='compromisos')
    
class ConsejoDirectivo(Base):
    __tablename__ = "consejos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)

    miembros = relationship("User", back_populates="consejo")
    observaciones = relationship("Observacion", back_populates="consejo")
    
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    apellido = Column(String(100))
    edad = Column(Integer)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))

    ong_id = Column(Integer, ForeignKey("ongs.id"), nullable=True)
    consejo_id = Column(Integer, ForeignKey("consejos.id"), nullable=True)

    ong = relationship("ONG", back_populates="usuarios")
    consejo = relationship("ConsejoDirectivo", back_populates="miembros")

class Observacion(Base):
    __tablename__ = "observaciones"
    id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    consejo_id = Column(Integer, ForeignKey("consejos.id"))
    descripcion = Column(Text, nullable=False)

    proyecto = relationship("Proyecto", back_populates="observaciones")
    consejo = relationship("ConsejoDirectivo", back_populates="observaciones")