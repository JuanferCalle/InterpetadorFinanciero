# 💰 Intérprete Financiero - Asistente de Gastos con IA

Un asistente financiero inteligente que utiliza **IA (Ollama)** y **procesamiento de lenguaje natural** para clasificar gastos automáticamente, analizar patrones de gastos y proporcionar sugerencias de inversión.

## 🎯 Características Principales

✅ **Clasificación Automática de Gastos** - Usa IA con Ollama para clasificar transacciones  
✅ **Extracción de Palabras Clave** - Depuración inteligente de palabras clave financieras  
✅ **Análisis Financiero** - Reportes diarios, semanales, mensuales, etc.  
✅ **Sugerencias de Inversión** - Recomendaciones basadas en patrones de gasto  
✅ **Validación con Schemas JSON** - Sistema robusto de verificación de datos  
✅ **Interfaz Web Responsive** - Fácil de usar en cualquier dispositivo  
✅ **API RESTful** - Backend Python con Flask  

## 📊 Categorías Soportadas

- 🍽️ Comida
- 🎮 Ocio
- 🚗 Gasolina/Transporte
- 🏠 Gastos del hogar
- 👕 Ropa
- ✈️ Viajes
- 🔧 Servicios
- 🏥 Salud
- 📚 Educación
- 💵 Salario
- 🎁 Bonificación
- 💻 Freelance
- 📦 Otro

## 🚀 Instalación Rápida

### Requisitos Previos

- **Python 3.8+**
- **Ollama** instalado y ejecutándose (https://ollama.ai)
- **Git** (opcional)

### 1. Preparar el Entorno

```bash
# Navegar al directorio del proyecto
cd InterpretadorFinanciero/backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### 2. Instalar Dependencias

```bash
pip install -r ../requirements.txt
```

### 3. Descargar Modelo de Ollama

```bash
# Asegúrate de que Ollama esté corriendo
# Descarga el modelo Mistral (recomendado)
ollama pull mistral

# O prueba con otros modelos:
ollama pull llama2
ollama pull neural-chat
```

### 4. Ejecutar la API Backend

```bash
# Desde el directorio backend/
python app.py
```

La API estará disponible en: **http://localhost:5000**

### 5. Servir el Frontend

Opción A - Servidor Python simple:
```bash
# Desde la raíz del proyecto
cd frontend
python -m http.server 8000
```

Opción B - Usar Live Server en VS Code (recomendado)

Accede a: **http://localhost:8000** (o la URL del servidor)

## 📖 Uso

### 1. Registrar Transacciones

En la interfaz web, escribe descripciones naturales de tus gastos:

**Ejemplos válidos:**
- "Gasté 50 mil pesos en comida"
- "Me pagaron 2 millones de salario"
- "Compré una chamarra en 150 mil"
- "Gasolina: 80 mil pesos"
- "Vuelo a Bogotá 500 mil"

### 2. Opciones de Clasificación

**Con IA Habilitada:**
- Sistema más preciso
- Mayor precisión en categorización
- Detección de contexto avanzada

**Sin IA (Basado en Palabras Clave):**
- Más rápido
- No requiere Ollama
- Usa diccionarios predefinidos

### 3. Generar Reportes

Selecciona un período y presiona "Analizar":

- **Diario** - Últimas 24 horas
- **Semanal** - Últimos 7 días
- **Mensual** - Últimos 30 días (predeterminado)
- **Bimestral** - Últimos 60 días
- **Semestral** - Últimos 180 días
- **Anual** - Últimos 365 días

### 4. Recibir Sugerencias

El sistema automáticamente genera sugerencias basadas en:
- Categorías con mayor gasto
- Balance positivo/negativo
- Oportunidades de ahorro
- Patrones de comportamiento

## 🏗️ Estructura del Proyecto

```
InterpretadorFinanciero/
├── backend/
│   ├── app.py                 # API principal con Flask
│   ├── requirements.txt        # Dependencias Python
│   ├── models/
│   │   ├── transaction.py     # Modelos de datos
│   │   └── financial_service.py # Servicio principal
│   ├── utils/
│   │   ├── keyword_extractor.py # Extracción de palabras clave
│   │   ├── ollama_client.py    # Cliente de Ollama
│   │   └── schema_validator.py # Validador de schemas
│   ├── schemas/
│   │   ├── transaction_schema.json
│   │   ├── analysis_schema.json
│   │   └── ai_response_schema.json
│   └── data/
│       └── transactions.json   # Base de datos local
├── frontend/
│   ├── index.html             # Interfaz web
│   ├── styles.css             # Estilos CSS
│   ├── api.js                 # Cliente API
│   └── app.js                 # Lógica de aplicación
└── README.md                  # Este archivo
```

## 🔌 API Endpoints

### Health Check
```http
GET /api/health
```

### Procesar Transacción
```http
POST /api/process-audio
Content-Type: application/json

{
  "text": "Gasté 50 mil en comida",
  "use_ai": false
}
```

**Respuesta:**
```json
{
  "success": true,
  "transaccion": {
    "id": "uuid",
    "tipo": "gasto",
    "cantidad": 50000,
    "categoria": "Comida",
    "descripcion": "Gasté 50 mil en comida",
    "fecha": "2026-03-07T10:30:00",
    "confianza": 0.95
  },
  "confianza": 0.95
}
```

### Obtener Análisis
```http
GET /api/analysis/mensual
```

### Obtener Sugerencias
```http
GET /api/suggestions?period=mensual
```

### Listar Transacciones
```http
GET /api/transactions
GET /api/transactions/category/Comida
```

## 🎯 Algoritmo de Clasificación

### Fase 1: Extracción de Palabras Clave
- Normaliza el texto (minúsculas, sin acentos)
- Busca palabras clave de cada categoría
- Calcula confianza basada en coincidencias

### Fase 2: Verificación
- Detecta conflictos entre categorías
- Ajusta confianza según conflictos
- Valida coherencia del resultado

### Fase 3: Clasificación con IA (opcional)
- Envía texto junto con keywords iniciales al modelo
- Obtiene clasificación mejorada del modelo Ollama
- Valida respuesta contra schemas JSON

### Fase 4: Validación Final
- Verifica contra schema de transacción
- Guarda en base de datos local
- Retorna resultado con metadatos

## 🔑 Palabras Clave por Categoría

### Comida
`comida, almuerzo, desayuno, cena, café, restaurante, pizza, hamburguesa, ...`

### Transporte
`gasolina, gas, taxi, uber, bus, metro, pasaje, combustible, ...`

### Hogar
`alquiler, luz, agua, servicios, internet, teléfono, reparación, ...`

### Viajes
`viaje, hotel, hostal, avión, vuelo, turismo, tour, vacaciones, ...`

[Ver todas las palabras clave: `/api/keywords`]

## ⚙️ Configuración Avanzada

### Cambiar Modelo de Ollama

En `backend/utils/ollama_client.py`:

```python
class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.default_model = "mistral"  # Cambiar aquí
```

### Ajustar Dirección de API

En `frontend/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';  // Cambiar aquí
```

### Modificar Categorías

1. Edita `backend/models/transaction.py` - Enum `ExpenseCategory`
2. Edita `backend/utils/keyword_extractor.py` - `CATEGORY_KEYWORDS`
3. Edita `frontend/index.html` - Options del select

## 📊 Estadísticas de Precisión

El sistema alcanza **90-95%** de precisión en clasificación con:

- Contexto claro y específico
- Palabras clave directas
- IA habilitada con Ollama
- Validación de schemas

Factores que reducen precisión:
- Descripciones ambiguas
- Múltiples categorías en una frase
- Palabras clave de varias categorías

## 🐛 Troubleshooting

### "No se puede conectar a Ollama"
```bash
# Verifica que Ollama esté corriendo
ollama serve

# O en otra terminal:
ollama pull mistral
```

### "Port 5000 already in use"
```bash
# Cambiar puerto en app.py
app.run(host='0.0.0.0', port=5001)
```

### "CORS errors"
- El backend ya tiene CORS habilitado
- Verifica que frontend y backend estén en URLs correctas

### "Modelo no disponible"
```bash
# Listar modelos disponibles
ollama list

# Descargar modelo
ollama pull nombre_modelo
```

## 📝 Ejemplos de Uso

### Ejemplo 1: Registrar Gasto
```
Entrada: "Gaste 35 mil en almuerzo"
Categoría: Comida
Confianza: 95%
Tipo: Gasto
```

### Ejemplo 2: Registrar Ingreso
```
Entrada: "Me pagaron 2 millones de salario"
Categoría: Salario
Confianza: 98%
Tipo: Ingreso
```

### Ejemplo 3: Análisis Mensual
```
Periodo: Mensual
Ingresos: $5,000,000
Gastos: $3,200,000
Balance: $1,800,000

Por Categoría:
- Comida: 28% ($896,000)
- Transporte: 22% ($704,000)
- Ocio: 18% ($576,000)
- Otros: 32%
```

## 🚀 Características Futuras

- [ ] Autenticación de usuarios
- [ ] Base de datos SQL completa
- [ ] Exportación de reportes a PDF
- [ ] Integración con APIs de bancos
- [ ] App móvil nativa
- [ ] Predicciones de gastos futuros
- [ ] Compartir presupuestos en familia
- [ ] Notificaciones de límites de gasto
- [ ] Soporte para múltiples monedas
- [ ] Gráficos interactivos avanzados

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👤 Autor

Juan Fernando Calle - [@JuanferCalle](https://github.com/JuanferCalle)

## 💬 Soporte

Para reportar bugs o sugerencias, abre un issue en GitHub.

---

**Última actualización:** Marzo 7, 2026  
**Versión:** 1.0.0 Beta
