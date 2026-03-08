"""
Ejemplos de uso de la API del Asistente Financiero
Ejecuta estos ejemplos después de que el servidor esté corriendo
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:5000/api"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_response(response):
    print(json.dumps(response, indent=2, ensure_ascii=False))

# ==================== EJEMPLOS ====================

def example_1_health_check():
    """Ejemplo 1: Verificar estado de la API"""
    print_section("1. Health Check")
    
    response = requests.get(f"{API_BASE}/health")
    print_response(response.json())

def example_2_process_simple():
    """Ejemplo 2: Procesar transacción simple sin IA"""
    print_section("2. Procesar Transacción (sin IA)")
    
    data = {
        "text": "Gasté 50 mil pesos en comida",
        "use_ai": False
    }
    
    response = requests.post(f"{API_BASE}/process-audio", json=data)
    print_response(response.json())

def example_3_process_with_ai():
    """Ejemplo 3: Procesar transacción con IA"""
    print_section("3. Procesar Transacción (con IA)")
    
    data = {
        "text": "Compré un vuelo a Bogotá por 900 mil pesos",
        "use_ai": True
    }
    
    response = requests.post(f"{API_BASE}/process-audio", json=data)
    print_response(response.json())

def example_4_multiple_transactions():
    """Ejemplo 4: Registrar múltiples transacciones"""
    print_section("4. Registrar Múltiples Transacciones")
    
    transactions = [
        "Desayuno: 15 mil pesos",
        "Taxi al trabajo: 25 mil",
        "Almuerzo con cliente: 80 mil",
        "Gasolina: 60 mil pesos",
        "Cine: 45 mil",
    ]
    
    for i, text in enumerate(transactions, 1):
        print(f"\n[{i}] Procesando: {text}")
        data = {"text": text, "use_ai": False}
        response = requests.post(f"{API_BASE}/process-audio", json=data)
        result = response.json()
        
        if result.get("success"):
            trans = result.get("transaccion", {})
            print(f"    ✓ {trans.get('categoria')} - ${trans.get('cantidad'):,.0f}")
        else:
            print(f"    ✗ Error: {result.get('error')}")

def example_5_income():
    """Ejemplo 5: Registrar ingresos"""
    print_section("5. Registrar Ingresos")
    
    incomes = [
        "Me pagaron 2 millones de salario",
        "Ganancia freelance: 500 mil pesos",
        "Bonificación de 300 mil",
    ]
    
    for text in incomes:
        print(f"\nProcesando: {text}")
        data = {"text": text, "use_ai": False}
        response = requests.post(f"{API_BASE}/process-audio", json=data)
        result = response.json()
        
        if result.get("success"):
            trans = result.get("transaccion", {})
            print(f"  ✓ {trans.get('tipo').upper()} - ${trans.get('cantidad'):,.0f}")

def example_6_get_transactions():
    """Ejemplo 6: Obtener todas las transacciones"""
    print_section("6. Obtener Todas las Transacciones")
    
    response = requests.get(f"{API_BASE}/transactions")
    data = response.json()
    
    print(f"Total de transacciones: {data.get('total', 0)}")
    
    if data.get('transactions'):
        print("\nÚltimas 3 transacciones:")
        for trans in data['transactions'][-3:]:
            print(f"  • {trans['categoria']} - ${trans['cantidad']:,.0f} ({trans['tipo']})")

def example_7_filter_by_category():
    """Ejemplo 7: Filtrar transacciones por categoría"""
    print_section("7. Filtrar por Categoría")
    
    category = "Comida"
    response = requests.get(f"{API_BASE}/transactions/category/{category}")
    data = response.json()
    
    print(f"Transacciones en categoría '{category}': {data.get('total', 0)}")
    
    if data.get('transactions'):
        total = sum(t['cantidad'] for t in data['transactions'])
        print(f"Total gastado: ${total:,.0f}")

def example_8_daily_analysis():
    """Ejemplo 8: Análisis diario"""
    print_section("8. Análisis Diario")
    
    response = requests.get(f"{API_BASE}/analysis/diario")
    analysis = response.json().get('analysis', {})
    
    print(f"Período: {analysis.get('periodo')}")
    print(f"Ingresos: ${analysis.get('ingresos_totales', 0):,.0f}")
    print(f"Gastos: ${analysis.get('gastos_totales', 0):,.0f}")
    print(f"Balance: ${analysis.get('balance', 0):,.0f}")

def example_9_monthly_analysis():
    """Ejemplo 9: Análisis mensual"""
    print_section("9. Análisis Mensual")
    
    response = requests.get(f"{API_BASE}/analysis/mensual")
    analysis = response.json().get('analysis', {})
    
    print(f"Período: {analysis.get('periodo')}")
    print(f"Ingresos: ${analysis.get('ingresos_totales', 0):,.0f}")
    print(f"Gastos: ${analysis.get('gastos_totales', 0):,.0f}")
    print(f"Balance: ${analysis.get('balance', 0):,.0f}")
    
    print("\nDesglose por categoría:")
    por_categoria = analysis.get('por_categoria', {})
    for cat, data in sorted(por_categoria.items(), key=lambda x: x[1]['total'], reverse=True)[:5]:
        pct = data.get('porcentaje', 0)
        total = data.get('total', 0)
        print(f"  • {cat}: ${total:,.0f} ({pct:.1f}%)")

def example_10_suggestions():
    """Ejemplo 10: Obtener sugerencias"""
    print_section("10. Obtener Sugerencias")
    
    response = requests.get(f"{API_BASE}/analysis-with-suggestions/mensual")
    data = response.json()
    
    suggestions = data.get('suggestions', [])
    print(f"Total de sugerencias: {len(suggestions)}")
    
    for i, sug in enumerate(suggestions, 1):
        print(f"\n[{i}] {sug.get('titulo')}")
        print(f"    Prioridad: {sug.get('prioridad').upper()}")
        print(f"    {sug.get('descripcion')}")
        if sug.get('ahorro_estimado'):
            print(f"    Ahorro estimado: ${sug.get('ahorro_estimado'):,.0f}")

def example_11_keywords_info():
    """Ejemplo 11: Información de palabras clave"""
    print_section("11. Información de Palabras Clave")
    
    response = requests.get(f"{API_BASE}/keywords")
    data = response.json().get('categories', {})
    
    print("Categorías y palabras clave disponibles:\n")
    for category, info in list(data.items())[:5]:
        print(f"  {category}:")
        print(f"    - Palabras: {', '.join(info.get('keywords', [])[:5])}...")
        print(f"    - Total: {info.get('total_keywords', 0)}")

def example_12_test_classification():
    """Ejemplo 12: Prueba de clasificación detallada"""
    print_section("12. Prueba de Clasificación Detallada")
    
    text = "Gasté 120 mil en unas chanclas allá en el centro comercial"
    
    data = {"text": text}
    response = requests.post(f"{API_BASE}/test/classify", json=data)
    result = response.json()
    
    print(f"Texto: {result.get('text')}")
    print(f"\nPalabras clave detectadas:")
    keywords = result.get('keywords', {})
    print(f"  Categoría: {keywords.get('categoría')}")
    print(f"  Confianza: {keywords.get('confianza', 0):.1%}")
    print(f"  Palabras: {', '.join(keywords.get('palabras_detectadas', []))}")
    
    print(f"\nCantidad extraída:")
    amount = result.get('amount', {})
    print(f"  Valor: ${amount.get('cantidad', 0):,.0f}")
    print(f"  Encontrada: {'Sí' if amount.get('encontrado') else 'No'}")

def example_13_edge_cases():
    """Ejemplo 13: Casos especiales"""
    print_section("13. Casos Especiales")
    
    test_cases = [
        "Gastos varios: 25 mil",  # Cantidad sin categoría clara
        "10 mil",  # Solo cantidad
        "Comida",  # Solo categoría
        "",  # Vacío
        "Me robaron 100 mil",  # Contexto inusual
    ]
    
    for text in test_cases:
        print(f"\nProbando: '{text}'")
        
        if text:
            data = {"text": text, "use_ai": False}
            response = requests.post(f"{API_BASE}/process-audio", json=data)
            result = response.json()
            
            if result.get("success"):
                print(f"  ✓ Éxito")
            else:
                print(f"  ⚠ {result.get('error', 'Error desconocido')}")
        else:
            print(f"  ✗ Texto vacío (error esperado)")

# ==================== EJECUTOR ====================

def menu():
    """Menú interactivo"""
    examples = [
        ("Health Check", example_1_health_check),
        ("Procesar Transacción (sin IA)", example_2_process_simple),
        ("Procesar Transacción (con IA)", example_3_process_with_ai),
        ("Múltiples Transacciones", example_4_multiple_transactions),
        ("Registrar Ingresos", example_5_income),
        ("Obtener Transacciones", example_6_get_transactions),
        ("Filtrar por Categoría", example_7_filter_by_category),
        ("Análisis Diario", example_8_daily_analysis),
        ("Análisis Mensual", example_9_monthly_analysis),
        ("Sugerencias", example_10_suggestions),
        ("Palabras Clave", example_11_keywords_info),
        ("Prueba de Clasificación", example_12_test_classification),
        ("Casos Especiales", example_13_edge_cases),
        ("Ejecutar Todos", None),
    ]
    
    print("\n" + "="*60)
    print("  Ejemplos del Asistente Financiero")
    print("="*60)
    print("\nSelecciona un ejemplo a ejecutar:\n")
    
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print(f"\n  0. Salir")
    
    while True:
        try:
            choice = int(input("\nOpción: "))
            
            if choice == 0:
                print("\n¡Hasta luego!")
                break
            elif choice == len(examples):
                # Ejecutar todos
                print("\nEjecutando todos los ejemplos...\n")
                for name, func in examples[:-1]:
                    try:
                        func()
                    except Exception as e:
                        print(f"\n✗ Error en {name}: {e}")
                input("\nPresiona Enter para salir...")
                break
            elif 1 <= choice < len(examples):
                try:
                    examples[choice-1][1]()
                    input("\nPresiona Enter para continuar...")
                except requests.exceptions.ConnectionError:
                    print("\n✗ Error: No se puede conectar con la API")
                    print("  Asegúrate de que el servidor esté corriendo en http://localhost:5000")
                except Exception as e:
                    print(f"\n✗ Error: {e}")
                    input("\nPresiona Enter para continuar...")
            else:
                print("\nOpción no válida")
        
        except ValueError:
            print("\nIngresa un número válido")

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\n¡Hasta luego!")
