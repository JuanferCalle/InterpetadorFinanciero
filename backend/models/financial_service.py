"""
Servicio principal de análisis financiero
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import unicodedata

from models.transaction import Transaction, Analysis, Suggestion, TransactionType, AnalysisPeriod
from utils.keyword_extractor import extract_keywords, extract_amount, verify_classification
from utils.ollama_client import OllamaClient, create_expense_classification_prompt, create_analysis_prompt
from utils.schema_validator import SchemaValidator

logger = logging.getLogger(__name__)


def _strip_accents(value: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', value)
        if unicodedata.category(c) != 'Mn'
    )

class FinancialAnalysisService:
    """Servicio principal de análisis financiero"""
    
    def __init__(self, data_dir: Path = Path("data"), schema_dir: Path = Path("schemas")):
        self.data_dir = Path(data_dir)
        self.schema_dir = Path(schema_dir)
        self.transactions: List[Transaction] = []
        self.ollama_client = OllamaClient()
        self.validator = SchemaValidator(schema_dir)
        self._load_transactions()
    
    def _load_transactions(self):
        """Carga transacciones desde archivo"""
        transactions_file = self.data_dir / "transactions.json"
        if transactions_file.exists():
            try:
                with open(transactions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.transactions = [Transaction.from_dict(t) for t in data]
                logger.info(f"Cargadas {len(self.transactions)} transacciones")
            except json.JSONDecodeError:
                logger.warning("transactions.json inválido o vacío; se reinicia con lista vacía")
                self.transactions = []
                self._save_transactions()
            except Exception as e:
                logger.error(f"Error cargando transacciones: {e}")
    
    def _save_transactions(self):
        """Guarda transacciones en archivo"""
        self.data_dir.mkdir(exist_ok=True)
        try:
            with open(self.data_dir / "transactions.json", 'w', encoding='utf-8') as f:
                json.dump([t.to_dict() for t in self.transactions], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error guardando transacciones: {e}")
    
    def process_audio_input(self, text: str, use_ai: bool = True) -> Dict[str, Any]:
        """
        Procesa entrada de audio/texto y clasifica la transacción.
        
        FLUJO IA-FIRST:
        1. Si use_ai=True y IA disponible → IA extrae TODO (monto, categoría, tipo)
        2. Si IA falla o no disponible → usa diccionarios como fallback
        
        Args:
            text: Texto a procesar
            use_ai: Si usar IA para clasificación (recomendado True)
            
        Returns:
            dict con transacción procesada
        """
        result = {
            "success": False,
            "transaccion": None,
            "confianza": 0.0,
            "keywords": [],
            "advertencias": [],
            "debug_info": {},
            "metodo": "fallback"  # Indica si usó IA o fallback
        }
        
        # ============ ENFOQUE IA-FIRST ============
        if use_ai and self.ollama_client.is_available():
            ai_result = self._process_with_ai(text)
            result["debug_info"]["ai_processing"] = ai_result
            
            if ai_result.get("success"):
                result["metodo"] = "ia"
                ai_data = ai_result["data"]
                
                try:
                    # Crear transacción directamente desde respuesta de IA
                    categoria_normalizada = _strip_accents(ai_data.get("categoria", "Otro"))
                    
                    transaccion = Transaction(
                        tipo=ai_data.get("tipo", "gasto"),
                        cantidad=float(ai_data.get("cantidad", 0)),
                        categoria=categoria_normalizada,
                        descripcion=ai_data.get("descripcion", text[:100]),
                        confianza=float(ai_data.get("confianza", 0.85))
                    )
                    
                    self.transactions.append(transaccion)
                    self._save_transactions()
                    
                    result["success"] = True
                    result["transaccion"] = transaccion.to_dict()
                    result["confianza"] = transaccion.confianza
                    result["categoria_detectada"] = categoria_normalizada
                    result["keywords"] = ai_data.get("palabras_clave", [])
                    
                    return result
                    
                except (ValueError, TypeError) as e:
                    result["advertencias"].append(f"Error procesando respuesta IA: {str(e)}")
                    logger.warning(f"IA response processing failed: {e}, falling back to dictionary")
        
        # ============ FALLBACK: DICCIONARIOS ============
        result["metodo"] = "fallback"
        result["advertencias"].append("Usando método de diccionarios (IA no disponible o falló)")
        
        # Extrae palabras clave con diccionarios
        keywords = extract_keywords(text, debug=True)
        result["keywords"] = keywords["palabras_detectadas"]
        result["debug_info"]["keywords"] = keywords
        
        # Extrae cantidad con regex
        amount_data = extract_amount(text)
        result["debug_info"]["amount_extraction"] = amount_data
        
        if not amount_data["encontrado"]:
            result["advertencias"].append("No se encontró cantidad monetaria")
            return result
        
        categoria_detectada = keywords.get("categoria") or keywords.get("categoría")

        if not categoria_detectada:
            result["advertencias"].append("No se pudo determinar categoría automáticamente")
            return result
        
        # Verifica clasificación
        verification = verify_classification(text, categoria_detectada, keywords["confianza"])
        result["debug_info"]["verification"] = verification
        keywords["confianza"] = verification["confianza_ajustada"]
        
        if not verification["válida"]:
            result["advertencias"].extend(verification["problemas"])
        
        # Crea transacción
        try:
            categoria_normalizada = _strip_accents(categoria_detectada)

            transaccion = Transaction(
                tipo=keywords["tipo"] or TransactionType.GASTO.value,
                cantidad=amount_data["cantidad"],
                categoria=categoria_normalizada,
                descripcion=text[:100],
                confianza=keywords["confianza"]
            )
            
            self.transactions.append(transaccion)
            self._save_transactions()
            
            result["success"] = True
            result["transaccion"] = transaccion.to_dict()
            result["confianza"] = keywords["confianza"]
            result["categoria_detectada"] = categoria_normalizada
            
        except ValueError as e:
            result["advertencias"].append(f"Error creando transacción: {str(e)}")
        
        return result
    
    def _process_with_ai(self, text: str) -> Dict[str, Any]:
        """
        Usa IA para extraer TODA la información de la transacción.
        Este es el método principal de procesamiento.
        """
        try:
            prompt = create_expense_classification_prompt(text)
            ai_response = self.ollama_client.generate_response(prompt, temperature=0.3)
            
            if not ai_response.get("success"):
                return {"success": False, "error": ai_response.get("error")}
            
            response_text = ai_response["response"].get("response", "")
            json_data = self.ollama_client.extract_json_from_response(response_text)
            
            if not json_data:
                return {"success": False, "error": "No se pudo extraer JSON de la respuesta de IA"}
            
            # Validar campos requeridos
            required_fields = ["tipo", "categoria", "cantidad"]
            missing = [f for f in required_fields if f not in json_data or json_data[f] is None]
            
            if missing:
                return {"success": False, "error": f"Campos faltantes en respuesta IA: {missing}"}
            
            # Validar y normalizar cantidad
            cantidad = json_data.get("cantidad")
            if isinstance(cantidad, str):
                # Limpiar formato si viene como string
                cantidad = cantidad.replace(".", "").replace(",", "").replace(" ", "")
                try:
                    cantidad = float(cantidad)
                except ValueError:
                    return {"success": False, "error": f"Cantidad inválida: {json_data.get('cantidad')}"}
            
            if not isinstance(cantidad, (int, float)) or cantidad <= 0:
                return {"success": False, "error": f"Cantidad debe ser número positivo: {cantidad}"}
            
            json_data["cantidad"] = cantidad
            
            # Validar tipo
            if json_data.get("tipo") not in ["gasto", "ingreso"]:
                json_data["tipo"] = "gasto"
            
            # Validar categoría
            categorias_validas = [
                "Comida", "Ocio", "Gasolina/Transporte", "Gastos del hogar", 
                "Ropa", "Viajes", "Servicios", "Salud", "Educacion", 
                "Salario", "Bonificacion", "Freelance", "Otro"
            ]
            if json_data.get("categoria") not in categorias_validas:
                json_data["categoria"] = "Otro"
            
            return {"success": True, "data": json_data, "raw_response": response_text}
            
        except Exception as e:
            logger.error(f"Error in AI processing: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_analysis(self, period: str = "mensual", end_date: Optional[datetime] = None) -> Analysis:
        """
        Genera análisis para un período
        
        Args:
            period: Período (diario, semanal, mensual, etc.)
            end_date: Fecha final del análisis
            
        Returns:
            Objeto Analysis
        """
        end_date = end_date or datetime.now()
        
        # Calcula fecha de inicio según período
        period_days = {
            "diario": 1,
            "semanal": 7,
            "mensual": 30,
            "bimestral": 60,
            "semestral": 180,
            "anual": 365
        }
        
        days = period_days.get(period, 30)
        start_date = end_date - timedelta(days=days)
        
        # Filtra transacciones del período
        period_transactions = [
            t for t in self.transactions
            if start_date <= t.fecha <= end_date
        ]
        
        # Calcula totales
        ingresos = sum(t.cantidad for t in period_transactions if t.tipo == TransactionType.INGRESO)
        gastos = sum(t.cantidad for t in period_transactions if t.tipo == TransactionType.GASTO)
        
        # Agrupa por categoría
        por_categoria = {}
        for t in period_transactions:
            if t.tipo == TransactionType.GASTO:
                cat = t.categoria.value
                if cat not in por_categoria:
                    por_categoria[cat] = {
                        "total": 0,
                        "porcentaje": 0,
                        "transacciones": 0
                    }
                por_categoria[cat]["total"] += t.cantidad
                por_categoria[cat]["transacciones"] += 1
        
        # Calcula porcentajes
        if gastos > 0:
            for cat in por_categoria:
                por_categoria[cat]["porcentaje"] = (por_categoria[cat]["total"] / gastos) * 100
        
        analysis = Analysis(
            periodo=period,
            fecha_inicio=start_date,
            fecha_fin=end_date,
            ingresos_totales=ingresos,
            gastos_totales=gastos,
            por_categoria=por_categoria
        )
        
        return analysis
    
    def get_suggestions(self, analysis: Analysis) -> List[Suggestion]:
        """
        Genera sugerencias basadas en análisis
        
        Args:
            analysis: Análisis a usar
            
        Returns:
            Lista de sugerencias
        """
        suggestions = []
        
        # Analiza categorías con mayor gasto
        categorias_ordenadas = sorted(
            analysis.por_categoria.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )
        
        # Sugerencia sobre categoría con mayor gasto
        if categorias_ordenadas:
            categoria_mayor = categorias_ordenadas[0]
            if categoria_mayor[1]["porcentaje"] > 40:
                suggestions.append(Suggestion(
                    titulo=f"Revisa gasto en {categoria_mayor[0]}",
                    descripcion=f"Esta categoría representa el {categoria_mayor[1]['porcentaje']:.1f}% de tus gastos",
                    prioridad="alta",
                    categoria_relacionada=categoria_mayor[0],
                    ahorro_estimado=categoria_mayor[1]["total"] * 0.1
                ))
        
        # Sugerencia sobre balance
        if analysis.balance < 0:
            suggestions.append(Suggestion(
                titulo="Balance negativo",
                descripcion=f"Estás gastando más de lo que ganas. Déficit: {abs(analysis.balance):.2f}",
                prioridad="alta"
            ))
        elif analysis.balance > analysis.ingresos_totales * 0.3:
            suggestions.append(Suggestion(
                titulo="Oportunidad de ahorro",
                descripcion=f"Tienes un excedente de {analysis.balance:.2f}. Considera invertirlo",
                prioridad="media",
                ahorro_estimado=analysis.balance
            ))
        
        return suggestions
    
    def get_all_transactions(self) -> List[Dict]:
        """Retorna todas las transacciones"""
        return [t.to_dict() for t in self.transactions]
    
    def get_transactions_by_category(self, category: str) -> List[Dict]:
        """Retorna transacciones de una categoría"""
        return [t.to_dict() for t in self.transactions if t.categoria.value == category]
    
    def clear_all_transactions(self) -> int:
        """Elimina todas las transacciones y retorna cantidad eliminada"""
        count = len(self.transactions)
        self.transactions = []
        self._save_transactions()
        logger.info(f"Eliminadas {count} transacciones")
        return count
