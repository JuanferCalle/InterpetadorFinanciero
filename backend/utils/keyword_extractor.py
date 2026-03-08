"""
Utilitario para detección y depuración de palabras clave financieras
"""

import re

# Palabras clave para cada categoría
CATEGORY_KEYWORDS = {
    "Comida": {
        "palabras": [
            "comida", "almuerzo", "desayuno", "cena", "café", "pan", "arroz",
            "pollo", "carne", "pescado", "verdura", "fruta", "restaurante",
            "hamburguesa", "pizza", "comidas", "comí", "comimos", "comer",
            "cenar", "desayunar", "almorzar", "snack", "galletas", "chocolate",
            "bebida", "refresco", "jugo", "agua", "cerveza", "vino", "licor",
            "vianda", "lonchera", "meal", "food", "lunch", "breakfast", "dinner",
            "perro", "hotdog", "empanada", "arepa", "tacos", "burrito", "sushi",
            "domicilio", "rappi", "ifood", "uber eats", "helado", "cafeteria", "panaderia",
            "antojito", "merienda", "postre", "fruver", "mercado"
        ],
        "multiplicadores": ["mercado", "tienda", "supermercado", "carnicería", "panadería"]
    },
    "Ocio": {
        "palabras": [
            "cine", "película", "juego", "videojuego", "console", "ps5", "xbox",
            "entretenimiento", "diversión", "parque", "concierto", "música",
            "hobby", "diversión", "pasatiempo", "ocio", "entretenimiento",
            "bar", "discoteca", "club", "diversiones", "juegos", "apuestas",
            "lotería", "casino", "streaming", "netflix", "spotify", "juguete",
            "rumba", "salida", "karaoke", "teatro", "bowling", "pool", "paseo",
            "play", "steam", "gamepass", "amazon prime", "hbo", "disney plus"
        ],
        "multiplicadores": []
    },
    "Gasolina/Transporte": {
        "palabras": [
            "gasolina", "gas", "combustible", "gasolinera", "uber", "taxi", "bus",
            "transporte", "pasaje", "viaje", "metro", "moto", "auto", "carro",
            "bicicleta", "combustible", "nafta",
            "diesel", "recarga", "pasaje", "pasajes", "boleto", "boletos",
            "transmilenio", "colectivo", "transporte público", "conducción",
            "cabify", "diditaxi", "didi", "inDrive", "parking", "parqueadero", "peaje",
            "soat", "revision tecnicomecanica", "mantenimiento carro", "llanta", "aceite"
        ],
        "multiplicadores": []
    },
    "Gastos del hogar": {
        "palabras": [
            "casa", "hogar", "casa", "alquilar", "alquiler", "luz", "agua",
            "servicios", "internet", "teléfono", "electricidad", "gas natural",
            "reparación", "reparar", "mantenimiento", "decoración", "muebles",
            "limpieza", "utensilio", "piso", "apartamento", "arrendamiento",
            "condominio", "construcción", "herramientas", "pintura", "reforma",
            "administracion", "predial", "electrodomestico", "nevera", "lavadora", "microondas",
            "arriendo", "aseo", "detergente", "escoba", "trapero", "papel higienico"
        ],
        "multiplicadores": []
    },
    "Ropa": {
        "palabras": [
            "ropa", "vestido", "pantalón", "camisa", "zapatos", "zapatilla",
            "tenis", "cinturón", "calcetines", "bufanda", "abrigo", "chaqueta",
            "jeans", "falda", "blusas", "medias", "ropa interior", "complementos",
            "traje", "corbata", "accesorios", "bolsa", "mochila", "cartera",
            "sombrería", "ropa deportiva", "uniforme", "tienda de ropa",
            "sudadera", "saco", "buso", "gorra", "chanclas", "sandalias", "botas",
            "camiseta", "polo", "short", "licra", "ropa de gimnasio", "outfit"
        ],
        "multiplicadores": []
    },
    "Viajes": {
        "palabras": [
            "viaje", "viajé", "viajo", "hotel", "hostal", "alojamiento",
            "avión", "vuelo", "billetes aéreo", "pasaje aéreo", "turismo",
            "tour", "excursión", "vacaciones", "viajando", "maleta", "equipaje",
            "destino", "viaje de vacaciones", "turista", "paseo", "expedición",
            "crucero", "reserva de hotel", "aerolinea", "agencia de viajes",
            "airbnb", "booking", "reserva", "itinerario", "checkin", "pasaporte", "visa",
            "tiquete", "boleto aereo", "equipaje de mano", "tourist"
        ],
        "multiplicadores": []
    },
    "Servicios": {
        "palabras": [
            "servicio", "servicios", "plomería", "electricista", "carpintero",
            "limpieza", "lavandería", "corte de cabello", "salón", "peluquería",
            "masaje", "consulta médica", "abogado", "contador", "asesor",
            "seguros", "póliza", "mantenimiento", "reparación", "instalación",
            "manicurista", "barbero", "uñas", "spa", "tecnico", "soporte tecnico",
            "suscripcion", "membresia", "hosting", "dominio", "nube"
        ],
        "multiplicadores": []
    },
    "Salud": {
        "palabras": [
            "médico", "doctor", "medicina", "farmacia", "medicinas", "pastillas",
            "vitaminas", "salud", "hospital", "clínica", "cirugía", "operación",
            "tratamiento", "consulta", "análisis", "examen", "sangre", "presión",
            "farmacéutico", "medicamento", "receta", "inyección", "vacuna",
            "odontologo", "dentista", "psicologo", "terapia", "eps", "copago",
            "lentes", "optica", "urgencias", "resonancia", "ecografia"
        ],
        "multiplicadores": []
    },
    "Educacion": {
        "palabras": [
            "escuela", "colegio", "universidad", "curso", "educación", "clase",
            "matrícula", "colegiatura", "libros", "libro", "cuaderno", "útiles",
            "papelería", "certificado", "doctorado", "maestría", "diplomado",
            "taller", "seminario", "capacitación", "estudio", "académico",
            "bootcamp", "certificacion", "udemy", "platzi", "coursera", "ingles",
            "matematicas", "programacion", "inscripcion", "derechos de grado"
        ],
        "multiplicadores": []
    },
    "Salario": {
        "palabras": [
            "salario", "sueldo", "pago", "pagé", "pagaron", "me pagaron",
            "cobré", "cobro", "remuneración", "nómina", "ingreso", "plusvalía",
            "recibí", "recibí dinero", "depositaron", "transferencia", "giro",
            "adecuado", "bonificación", "prima", "proyectos", "freelance"
        ],
        "multiplicadores": []
    },
    "Bonificacion": {
        "palabras": [
            "bonificación", "bono", "regalo", "premio", "recompensa", "bonus",
            "extra", "propina", "gratificación", "incentivo", "extra dinero"
        ],
        "multiplicadores": []
    },
    "Freelance": {
        "palabras": [
            "freelance", "proyecto", "trabajo", "trabajé", "trabajando",
            "ganancias", "ingreso extra", "dinero extra", "ingresos", "ganancia",
            "consultoría", "asesoría", "servicios freelance", "trabajo independiente"
        ],
        "multiplicadores": []
    }
}

CATEGORY_INTENTS = {
    "Comida": [
        r"\b(hamburguesa|pizza|perro|empanada|arepa|almuerzo|desayuno|cena|restaurante|domicilio)\b",
        r"\b(compre|compr[eé]|pedi|ped[ií]|pague|pagu[eé]|gaste|gast[eé]).*\b(comida|almuerzo|desayuno|cena|hamburguesa|pizza|restaurante)\b",
    ],
    "Gasolina/Transporte": [
        r"\b(taxi|uber|cabify|bus|metro|pasaje|transporte|gasolina|combustible|peaje|parqueadero)\b",
        r"\b(pague|pagu[eé]|gaste|gast[eé]|recargue|recargu[eé]).*\b(taxi|uber|pasaje|metro|gasolina|combustible|peaje)\b",
    ],
    "Gastos del hogar": [
        r"\b(arriendo|alquiler|luz|agua|internet|telefono|servicios|mercado|supermercado|aseo|hogar)\b",
    ],
    "Ropa": [
        r"\b(camisa|pantalon|jean|tenis|zapatos|chaqueta|ropa|vestido|blusa|sudadera|gorra)\b",
        r"\b(compre|compr[eé]|pague|pagu[eé]|gaste|gast[eé]).*\b(ropa|tenis|zapatos|camisa|pantalon|chaqueta)\b",
    ],
    "Viajes": [
        r"\b(vuelo|avion|hotel|hostal|viaje|vacaciones|reserva|tiquete|aerolinea)\b",
    ],
    "Ocio": [
        r"\b(cine|bar|discoteca|netflix|spotify|videojuego|juego|concierto|rumba|salida)\b",
    ],
    "Salud": [
        r"\b(farmacia|medicamento|medicina|doctor|medico|consulta|clinica|hospital|examen)\b",
    ],
    "Educacion": [
        r"\b(curso|matricula|universidad|colegio|clase|libros|cuaderno|educacion|estudio)\b",
    ],
    "Servicios": [
        r"\b(plomero|electricista|mantenimiento|reparacion|lavanderia|peluqueria|seguro)\b",
    ],
    "Salario": [
        r"\b(me\s+pagaron|salario|sueldo|nomina|pago\s+de\s+la\s+empresa)\b",
    ],
    "Bonificacion": [
        r"\b(bono|bonificacion|prima|incentivo|recompensa)\b",
    ],
    "Freelance": [
        r"\b(freelance|cliente|proyecto|consultoria|asesoria|pago\s+de\s+cliente)\b",
    ],
}

# Palabras de negación (gasto vs ingreso)
NEGATION_WORDS = {
    "gasto": ["gasté", "gaste", "gastaba", "gastar", "pagué", "pague", "pagaba", "pagar"],
    "ingreso": ["recibí", "recibe", "cobré", "cobro", "ganancia", "gané", "gane", "ingreso", "me pagaron", "pagaron"]
}

# Palabras de cantidad de dinero
MONEY_KEYWORDS = ["pesos", "dólares", "euros", "mil", "millón", "dinero", "plata"]

def normalize_text(text: str) -> str:
    """
    Normaliza el texto quitando acentos y convirtiéndolo a minúsculas
    """
    import unicodedata
    
    text = text.lower()
    # Remover acentos
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    return text


def keyword_in_text(normalized_text: str, keyword: str) -> bool:
    """Evalúa coincidencia de keyword evitando falsos positivos por subcadenas."""
    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return False

    if " " in normalized_keyword:
        return normalized_keyword in normalized_text

    pattern = rf"(?<!\w){re.escape(normalized_keyword)}(?!\w)"
    return re.search(pattern, normalized_text) is not None

def extract_keywords(text: str, debug: bool = False) -> dict:
    """
    Extrae palabras clave del texto y clasifica la transacción
    
    Args:
        text: Texto a analizar
        debug: Si True, retorna información de depuración
        
    Returns:
        dict con palabras clave encontradas y clasificación
    """
    normalized_text = normalize_text(text)
    found_keywords = {
        "categoría": None,
        "categoria": None,
        "palabras_detectadas": [],
        "confianza": 0.0,
        "tipo": None,
        "debug_info": {} if debug else None
    }
    
    # Detectar tipo de transacción
    for tipo, palabras in NEGATION_WORDS.items():
        for palabra in palabras:
            if keyword_in_text(normalized_text, palabra):
                found_keywords["tipo"] = tipo
                found_keywords["palabras_detectadas"].append(f"{palabra} ({tipo})")
                break
    
    # Buscar categoría por palabras clave
    for categoria, datos in CATEGORY_KEYWORDS.items():
        matches = 0
        for palabra in datos["palabras"]:
            if keyword_in_text(normalized_text, palabra):
                matches += 1
                found_keywords["palabras_detectadas"].append(f"{palabra} ✓")
        
        if matches > 0:
            # Calcular confianza
            confianza = min(0.55 + (matches - 1) * 0.12, 0.95)
            
            # Aumentar confianza si hay multiplicadores
            for multiplicador in datos["multiplicadores"]:
                if keyword_in_text(normalized_text, multiplicador):
                    confianza = min(confianza + 0.1, 0.99)
            
            if confianza > found_keywords["confianza"]:
                found_keywords["confianza"] = confianza
                found_keywords["categoría"] = categoria
                found_keywords["categoria"] = categoria
                
                if debug:
                    found_keywords["debug_info"][categoria] = {
                        "matches": matches,
                        "confianza": confianza,
                        "multiplicadores_encontrados": [m for m in datos["multiplicadores"] if keyword_in_text(normalized_text, m)]
                    }

    # Reforzar por intención/contexto (frases naturales)
    for categoria, patterns in CATEGORY_INTENTS.items():
        intent_matches = 0
        for pattern in patterns:
            if re.search(pattern, normalized_text):
                intent_matches += 1

        if intent_matches > 0:
            intent_confianza = min(0.62 + (intent_matches - 1) * 0.12, 0.96)
            if intent_confianza > found_keywords["confianza"]:
                found_keywords["confianza"] = intent_confianza
                found_keywords["categoría"] = categoria
                found_keywords["categoria"] = categoria

            found_keywords["palabras_detectadas"].append(f"intencion:{categoria.lower()} ({intent_matches})")

            if debug:
                if categoria not in found_keywords["debug_info"]:
                    found_keywords["debug_info"][categoria] = {}
                found_keywords["debug_info"][categoria]["intent_matches"] = intent_matches
                found_keywords["debug_info"][categoria]["intent_confianza"] = intent_confianza
    
    return found_keywords

def extract_amount(text: str) -> dict:
    """
    Extrae cantidad monetaria del texto.
    Contexto: Colombia (millón = 1,000,000, mil = 1,000)
    Soporta jerga colombiana: palos, barras (millones), lucas (miles)
    """
    import re
    
    normalized = normalize_text(text)
    
    # Números en palabras (español colombiano)
    NUMEROS_PALABRAS = {
        'cero': 0, 'un': 1, 'uno': 1, 'una': 1,
        'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5,
        'seis': 6, 'siete': 7, 'ocho': 8, 'nueve': 9, 'diez': 10,
        'once': 11, 'doce': 12, 'trece': 13, 'catorce': 14, 'quince': 15,
        'dieciseis': 16, 'diecisiete': 17, 'dieciocho': 18, 'diecinueve': 19,
        'veinte': 20, 'veintiuno': 21, 'veintidos': 22, 'veintitres': 23,
        'veinticuatro': 24, 'veinticinco': 25, 'veintiseis': 26, 'veintisiete': 27,
        'veintiocho': 28, 'veintinueve': 29,
        'treinta': 30, 'treinta y uno': 31, 'treinta y dos': 32, 'treinta y tres': 33,
        'treinta y cuatro': 34, 'treinta y cinco': 35, 'treinta y seis': 36,
        'treinta y siete': 37, 'treinta y ocho': 38, 'treinta y nueve': 39,
        'cuarenta': 40, 'cincuenta': 50, 'sesenta': 60,
        'setenta': 70, 'ochenta': 80, 'noventa': 90,
        'cien': 100, 'ciento': 100, 'doscientos': 200, 'trescientos': 300,
        'cuatrocientos': 400, 'quinientos': 500, 'seiscientos': 600,
        'setecientos': 700, 'ochocientos': 800, 'novecientos': 900,
        'medio': 0.5, 'media': 0.5,
    }
    
    # Jerga colombiana para dinero
    JERGA_MILLONES = ['palo', 'palos', 'barra', 'barras', 'millon', 'millones', 'mill', 'melones', 'melon']
    JERGA_MILES = ['luca', 'lucas', 'mil', 'k']
    
    def palabra_a_numero(palabra: str) -> float:
        """Convierte palabra a número"""
        return NUMEROS_PALABRAS.get(palabra.strip(), 0)
    
    def extraer_numero_compuesto(texto: str) -> float:
        """Extrae números compuestos como 'un millon doscientos' o 'doscientos cincuenta mil'"""
        total = 0
        
        # PRIMERO: Detectar "y medio" para millones (ej: "millon y medio" = 1,500,000)
        patron_y_medio = r'(?:(\w+)\s+)?(millon|millones|palo|palos|barra|barras|melones?)\s+y\s+(medio|media)\b'
        match_medio = re.search(patron_y_medio, texto)
        if match_medio:
            antes = match_medio.group(1)
            millones = 1
            if antes:
                millones = palabra_a_numero(antes)
                if millones == 0:
                    try:
                        millones = float(antes.replace(',', '.'))
                    except:
                        millones = 1
            # "y medio" significa + 500,000
            return (millones + 0.5) * 1_000_000
        
        # Patrón para millones con resto: "un millon doscientos [mil]"
        # Ej: "millon doscientos" = 1,200,000 (asume que doscientos son miles)
        patron_millon_completo = r'(?:(\w+)\s+)?(millon|millones|palo|palos|barra|barras|melones?)\s+(\w+)(?:\s+mil)?'
        match = re.search(patron_millon_completo, texto)
        if match:
            # Número antes de millón
            antes = match.group(1)
            millones = 1
            if antes:
                millones = palabra_a_numero(antes)
                if millones == 0:
                    # Podría ser número: "1 millon"
                    try:
                        millones = float(antes.replace(',', '.'))
                    except:
                        millones = 1
            
            total = millones * 1_000_000
            
            # Número después de millón (ej: "doscientos" en "millon doscientos")
            despues = match.group(3)
            if despues and despues not in ['y', 'de', 'en', 'por', 'para']:
                valor_despues = palabra_a_numero(despues)
                if valor_despues > 0:
                    # Centenas o decenas después de millón → asumimos que son miles
                    if valor_despues >= 100:
                        total += valor_despues * 1_000
                    elif valor_despues < 100 and valor_despues > 0:
                        total += valor_despues * 1_000
            
            return total
        
        return 0
    
    # 1. Intentar extraer número compuesto primero (maneja "millon doscientos")
    cantidad_compuesta = extraer_numero_compuesto(normalized)
    if cantidad_compuesta > 0:
        return {
            "cantidad": cantidad_compuesta,
            "texto_original": text,
            "encontrado": True
        }
    
    # 2. Patrón con "y medio/media" PRIMERO (ej: "dos palos y medio" = 2,500,000)
    numeros_pattern = '|'.join(NUMEROS_PALABRAS.keys())
    millones_pattern = '|'.join(JERGA_MILLONES)
    pattern_y_medio = rf'\b(\d+[\.,]?\d*|{numeros_pattern})\s*({millones_pattern})\s+y\s+(medio|media)\b'
    match = re.search(pattern_y_medio, normalized)
    if match:
        num_str = match.group(1)
        try:
            cantidad = float(num_str.replace(',', '.'))
        except ValueError:
            cantidad = palabra_a_numero(num_str)
        if cantidad > 0:
            return {
                "cantidad": (cantidad + 0.5) * 1_000_000,
                "texto_original": match.group(0),
                "encontrado": True
            }
    
    # 3. Patrón: "[número] palos/barras/millones" (jerga colombiana)
    pattern_millones = rf'\b(\d+[\.,]?\d*|{numeros_pattern})\s*({millones_pattern})\b'
    match = re.search(pattern_millones, normalized)
    if match:
        num_str = match.group(1)
        try:
            cantidad = float(num_str.replace(',', '.'))
        except ValueError:
            cantidad = palabra_a_numero(num_str)
        if cantidad > 0:
            return {
                "cantidad": cantidad * 1_000_000,
                "texto_original": match.group(0),
                "encontrado": True
            }
    
    # 4. Patrón: "[número] lucas/mil/k" (jerga colombiana)
    miles_pattern = '|'.join(JERGA_MILES)
    pattern_miles = rf'\b(\d+[\.,]?\d*|{numeros_pattern})\s*({miles_pattern})\b'
    match = re.search(pattern_miles, normalized)
    if match:
        num_str = match.group(1)
        try:
            cantidad = float(num_str.replace(',', '.'))
        except ValueError:
            cantidad = palabra_a_numero(num_str)
        if cantidad > 0:
            return {
                "cantidad": cantidad * 1_000,
                "texto_original": match.group(0),
                "encontrado": True
            }
    
    # 5. Patrón con símbolo de peso o número simple (ej: $100000, 50000 pesos)
    patterns_simple = [
        r'\$\s*([\d\.,]+)',  # $100.000 o $100,000
        r'([\d\.,]+)\s*(?:pesos|cop|pesitos)',  # 100000 pesos
        r'\b(\d{4,})\b',  # Número de 4+ dígitos (sin unidad)
    ]
    
    for pattern in patterns_simple:
        match = re.search(pattern, normalized)
        if match:
            num_str = match.group(1)
            # En Colombia se usa punto como separador de miles
            # Detectar formato: 1.000.000 vs 1,000,000 vs 1000000
            if '.' in num_str and ',' not in num_str:
                parts = num_str.split('.')
                if all(len(p) == 3 for p in parts[1:]):
                    # Es formato de miles: 1.000.000
                    num_str = num_str.replace('.', '')
            elif ',' in num_str and '.' not in num_str:
                parts = num_str.split(',')
                if len(parts) == 2 and len(parts[1]) == 3:
                    num_str = num_str.replace(',', '')
                else:
                    num_str = num_str.replace(',', '.')
            
            if num_str.count('.') > 1:
                num_str = num_str.replace('.', '')
            
            try:
                cantidad = float(num_str.replace(',', ''))
                if cantidad > 0:
                    return {
                        "cantidad": cantidad,
                        "texto_original": match.group(0),
                        "encontrado": True
                    }
            except ValueError:
                pass
    
    return {
        "cantidad": None,
        "texto_original": None,
        "encontrado": False
    }

def verify_classification(text: str, categoria: str, confianza: float) -> dict:
    """
    Verifica si la clasificación tiene sentido comparando con patrones conocidos
    """
    normalized_text = normalize_text(text)
    
    verification = {
        "válida": True,
        "problemas": [],
        "sugerencias": [],
        "confianza_ajustada": confianza
    }
    
    if confianza < 0.3:
        verification["válida"] = False
        verification["problemas"].append("Confianza muy baja (< 30%)")
        verification["sugerencias"].append("Considere proporcionar más detalles")
    
    # Verificar conflictos de palabras clave
    conflictos = 0
    for cat, datos in CATEGORY_KEYWORDS.items():
        if cat != categoria:
            for palabra in datos["palabras"]:
                if keyword_in_text(normalized_text, palabra):
                    conflictos += 1
    
    if conflictos > 3:
        verification["problemas"].append(f"Se detectaron {conflictos} palabras de otras categorías")
        verification["confianza_ajustada"] = min(confianza * 0.8, confianza - 0.15)
    
    return verification
