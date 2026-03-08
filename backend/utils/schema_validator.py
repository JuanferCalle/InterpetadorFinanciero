"""
Validador de schemas JSON
"""

import json
import jsonschema
from jsonschema import validate, ValidationError
from pathlib import Path
from typing import Dict, Any, Tuple

class SchemaValidator:
    """Validador de esquemas JSON"""
    
    def __init__(self, schema_dir: Path):
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """Carga todos los schemas del directorio"""
        for schema_file in self.schema_dir.glob("*.json"):
            schema_name = schema_file.stem
            with open(schema_file, 'r', encoding='utf-8') as f:
                self.schemas[schema_name] = json.load(f)
    
    def validate_transaction(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida una transacción contra el schema
        
        Args:
            data: Datos a validar
            
        Returns:
            Tupla (válido, mensaje)
        """
        try:
            validate(instance=data, schema=self.schemas["transaction_schema"])
            return True, "Transacción válida"
        except ValidationError as e:
            return False, f"Error de validación: {e.message}"
        except KeyError:
            return False, "Schema de transacción no encontrado"
    
    def validate_analysis(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida un análisis contra el schema
        
        Args:
            data: Datos a validar
            
        Returns:
            Tupla (válido, mensaje)
        """
        try:
            validate(instance=data, schema=self.schemas["analysis_schema"])
            return True, "Análisis válido"
        except ValidationError as e:
            return False, f"Error de validación: {e.message}"
        except KeyError:
            return False, "Schema de análisis no encontrado"
    
    def validate_ai_response(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida una respuesta de IA contra el schema
        
        Args:
            data: Datos a validar
            
        Returns:
            Tupla (válido, mensaje)
        """
        try:
            validate(instance=data, schema=self.schemas["ai_response_schema"])
            return True, "Respuesta de IA válida"
        except ValidationError as e:
            return False, f"Error de validación: {e.message}"
        except KeyError:
            return False, "Schema de respuesta de IA no encontrado"

def validate_json_structure(data: Dict[str, Any], required_keys: list) -> Tuple[bool, list]:
    """
    Valida que un JSON tenga todas las claves requeridas
    
    Args:
        data: Datos a validar
        required_keys: Claves requeridas
        
    Returns:
        Tupla (válido, claves faltantes)
    """
    missing_keys = [key for key in required_keys if key not in data]
    return len(missing_keys) == 0, missing_keys
