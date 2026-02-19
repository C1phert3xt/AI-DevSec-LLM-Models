## 🐍 Automatización: SAST Local con Python y Ollama API

El verdadero poder de tener este arsenal en local es la automatización. En lugar de copiar y pegar código en una interfaz web, podemos usar un script en Python para leer archivos fuente y enviarlos a la API local de Ollama para que busque vulnerabilidades silenciosamente.

### El Script: `ai_devsec_analyzer.py`

Este script utiliza `qwen2.5-coder` (nuestro experto en código) para analizar cualquier archivo en busca de fallos de seguridad (Buffer Overflows, inyecciones SQL, credenciales hardcodeadas, etc.).

Crea el archivo `xibalba_analyzer.py`:

```python
import requests
import json
import argparse
import sys
from colorama import Fore, Style, init

# Inicializar colores para la terminal
init(autoreset=True)

OLLAMA_API = "http://localhost:11434/api/generate"

def analyze_code(file_path, model="qwen2.5-coder:latest"):
    print(f"{Fore.CYAN}[*] Iniciando Análisis de Código Estático (SAST) con {model}...{Style.RESET_ALL}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"{Fore.RED}[!] Error: Archivo '{file_path}' no encontrado.{Style.RESET_ALL}")
        sys.exit(1)

    # Prompt táctico diseñado para Red/Blue Team
    prompt = f"""
    Actúa como un Auditor de Seguridad de Software Senior (Offensive Security Engineer).
    Analiza el siguiente código fuente en busca de vulnerabilidades (OWASP Top 10, RCE, LFI, SQLi, etc.).
    
    Reglas de respuesta:
    1. Si es seguro, di "CÓDIGO SEGURO" y da una breve razón.
    2. Si es vulnerable, explica el vector de ataque paso a paso.
    3. Proporciona el código corregido.
    
    Código a analizar:
    \n\n{source_code}
    """

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False # Falso para recibir la respuesta completa al final
    }

    try:
        print(f"{Fore.YELLOW}[*] Procesando {len(source_code)} caracteres. El modelo está pensando...{Style.RESET_ALL}\n")
        response = requests.post(OLLAMA_API, json=payload)
        response.raise_for_status()
        
        result = response.json()
        print(f"{Fore.GREEN}=== REPORTE DE VULNERABILIDAD ==={Style.RESET_ALL}")
        print(result.get("response", "Sin respuesta del modelo."))
        print(f"{Fore.GREEN}================================={Style.RESET_ALL}")

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[!] Error de conexión con Ollama. ¿Está el servicio corriendo? Detalle: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Xibalba AI Code Analyzer")
    parser.add_argument("-f", "--file", required=True, help="Ruta del archivo de código a analizar")
    parser.add_argument("-m", "--model", default="qwen2.5-coder:latest", help="Modelo a utilizar (default: qwen2.5-coder)")
    
    args = parser.parse_args()
    analyze_code(args.file, args.model)
