"""
Modelos de datos para transacciones financieras
"""

from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import unicodedata

class TransactionType(str, Enum):
    """Tipos de transacciones"""
    GASTO = "gasto"
    INGRESO = "ingreso"

class ExpenseCategory(str, Enum):
    """Categorías de gastos"""
    COMIDA = "Comida"
    OCIO = "Ocio"
    TRANSPORTE = "Gasolina/Transporte"
    HOGAR = "Gastos del hogar"
    ROPA = "Ropa"
    VIAJES = "Viajes"
    SERVICIOS = "Servicios"
    SALUD = "Salud"
    EDUCACION = "Educacion"
    OTRO = "Otro"
    SALARIO = "Salario"
    BONIFICACION = "Bonificacion"
    FREELANCE = "Freelance"

@dataclass
class Transaction:
    """Modelo de transacción"""
    tipo: TransactionType
    cantidad: float
    categoria: ExpenseCategory
    descripcion: str
    confianza: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha: datetime = field(default_factory=datetime.now)
    notas: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones post-inicialización"""
        if isinstance(self.tipo, str):
            self.tipo = TransactionType(self.tipo.strip().lower())

        if isinstance(self.categoria, str):
            self.categoria = ExpenseCategory(self._normalize_category(self.categoria))

        if isinstance(self.fecha, str):
            self.fecha = datetime.fromisoformat(self.fecha)

        self.cantidad = float(self.cantidad)
        self.confianza = float(self.confianza)

        if not 0 <= self.confianza <= 1:
            raise ValueError("Confianza debe estar entre 0 y 1")
        if self.cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa")

    @staticmethod
    def _normalize_category(category: str) -> str:
        """Normaliza categoría a los valores del enum y schema (sin acentos)."""
        normalized = ''.join(
            c for c in unicodedata.normalize('NFD', category.strip())
            if unicodedata.category(c) != 'Mn'
        )

        mapping = {
            "Educacion": "Educacion",
            "Bonificacion": "Bonificacion",
            "Gastos del hogar": "Gastos del hogar",
            "Gasolina/Transporte": "Gasolina/Transporte",
        }
        return mapping.get(normalized, normalized)
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        data = asdict(self)
        data["tipo"] = self.tipo.value
        data["categoria"] = self.categoria.value
        data["fecha"] = self.fecha.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Crea desde diccionario"""
        data_copy = data.copy()
        return cls(**data_copy)

@dataclass
class AnalysisPeriod(str, Enum):
    """Periodos de análisis"""
    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSUAL = "mensual"
    BIMESTRAL = "bimestral"
    SEMESTRAL = "semestral"
    ANUAL = "anual"

@dataclass
class Analysis:
    """Análisis financiero de un período"""
    periodo: str
    fecha_inicio: datetime
    fecha_fin: datetime
    ingresos_totales: float = 0.0
    gastos_totales: float = 0.0
    por_categoria: dict = field(default_factory=dict)
    tendencias: list = field(default_factory=list)
    
    @property
    def balance(self) -> float:
        """Balance = ingresos - gastos"""
        return self.ingresos_totales - self.gastos_totales
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            "periodo": self.periodo,
            "fecha_inicio": self.fecha_inicio.isoformat(),
            "fecha_fin": self.fecha_fin.isoformat(),
            "ingresos_totales": self.ingresos_totales,
            "gastos_totales": self.gastos_totales,
            "balance": self.balance,
            "por_categoria": self.por_categoria,
            "tendencias": self.tendencias
        }

@dataclass
class Suggestion:
    """Sugerencia de inversión o ahorro"""
    titulo: str
    descripcion: str
    prioridad: str  # alta, media, baja
    categoria_relacionada: Optional[str] = None
    ahorro_estimado: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return asdict(self)
