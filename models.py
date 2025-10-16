from sqlalchemy import Column, Integer, String, ForeignKey, Date, Table
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
    proyecto = relationship('Proyecto')