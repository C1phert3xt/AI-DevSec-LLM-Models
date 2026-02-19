# 💀 AI DevSec: Local LLM Arsenal for Cybersecurity

![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-blue)
![Cybersecurity](https://img.shields.io/badge/Cybersecurity-Red_Team_%7C_Blue_Team-red)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

Bienvenidos al **Laboratorio AI DevSec**. Este repositorio es una guía táctica para configurar, desplegar y utilizar Modelos de Lenguaje Grande (LLMs) ejecutados 100% en local para operaciones de seguridad ofensiva (Red Team) y defensiva (Blue Team). 

El objetivo es mantener el **OPSEC (Seguridad de las Operaciones)** intacto: cero fugas de datos hacia APIs en la nube al analizar logs, código o desarrollar exploits.

## 🧰 El Arsenal (Modelos Actuales)

La selección de modelos no es casualidad. Cada IA en este entorno tiene un rol específico en el ciclo de vida de un incidente de seguridad:

### 🔴 Red Team & Desarrollo de Exploits (Uncensored)
Modelos sin filtros de "alineación moral", diseñados para pensar como un atacante, generar payloads y explicar vulnerabilidades sin restricciones.
* `whiterabbit-v2:latest` (8.5 GB): El modelo insignia para Red Team. Excelente para buscar vectores de ataque directo.
* `dolphin-mistral:latest` (4.1 GB): Rápido, ágil y con 32k de contexto. Ideal para tareas ofensivas rápidas.
* `dolphin-llama3:latest` (4.7 GB): La agresividad de Dolphin con el razonamiento de la arquitectura Llama 3.
* `xibalba-hacker:latest` (4.7 GB): Modelo customizado para las operaciones del laboratorio.

### 🔵 Blue Team & Análisis Forense (Contexto Largo)
Modelos con ventanas de contexto masivas (128k tokens) capaces de ingerir miles de líneas de logs (`auth.log`, pcap dumps, JSON de CloudTrail) sin alucinar.
* `llama3.1:latest` (4.9 GB): El estándar de la industria. Analista forense implacable y preciso.
* `mistral-nemo:latest` (7.1 GB): Optimizado para hardware NVIDIA. Equilibrio perfecto entre velocidad y razonamiento de logs.
* `hermes3:latest` (4.7 GB): Capacidades de agente superior, excelente para correlacionar eventos complejos y simular razonamiento de un analista Tier 3.

### 💻 Threat Hunting & Scripting
* `qwen2.5-coder:latest` (4.7 GB): El arquitecto. Supera a muchos modelos más grandes escribiendo scripts en Python, reglas SIGMA/YARA, consultas KQL o automatizaciones en Bash.

---

## ⚙️ Optimización de Entorno (Hardware Tuning)

Para ejecutar este arsenal de forma fluida, especialmente los modelos pesados, se recomienda una máquina con al menos 16GB de VRAM y 64GB de RAM. 

Si ejecutas esto en **WSL2 (Windows Subsystem for Linux)**, es crítico optimizar la asignación de recursos creando un archivo `.wslconfig` en la carpeta raíz de tu usuario de Windows (`C:\Users\TuUsuario\.wslconfig`):

```ini
[wsl2]
# Asignación agresiva de RAM para mantener los LLMs en memoria
memory=48GB
# Asignación de hilos de CPU (Ajustar según tu procesador)
processors=16
# Swap fijo
swap=8GB
pageReporting=true
guiApplications=true

(Nota: Reinicia WSL con wsl --shutdown después de aplicar estos cambios).

🚀 Uso Táctico (Ejemplos de Comandos)
1. Análisis de Logs (Blue Team):
Utilizamos Llama 3.1 por su ventana de contexto extendida para buscar inyecciones SQL en un log web:

ollama run llama3.1 "Actúa como un analista SOC. Analiza este log de Apache y extrae cualquier intento de SQLi, devolviendo solo la IP atacante y el payload: $(cat access.log)"


2. Creación de Reglas de Detección:
Utilizamos Qwen 2.5 Coder para traducir un comportamiento malicioso a una regla de detección:

ollama run qwen2.5-coder "Escribe una regla YARA para detectar un binario de Windows que importa 'VirtualAlloc' y contiene la cadena en base64 'cG93ZXJzaGVsbCAi'"


## 🐍 Automatización: SAST Local con Python y Ollama API

El verdadero poder de tener este arsenal en local es la automatización. En lugar de copiar y pegar código en una interfaz web, podemos usar un script en Python para leer archivos fuente y enviarlos a la API local de Ollama para que busque vulnerabilidades silenciosamente.

### El Script: `ai_devsec_analyzer.py`

Este script utiliza `qwen2.5-coder` (nuestro experto en código) para analizar cualquier archivo en busca de fallos de seguridad (Buffer Overflows, inyecciones SQL, credenciales hardcodeadas, etc.).

Crea el archivo `ai_devsec_analyzer.py`:

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


🚀 Cómo usarlo

Instala la dependencia de colores si no la tienes: pip install requests colorama

Pídele al script que analice un script sospechoso o tu propio desarrollo:

python ai_devsec_analyzer.py -f login_handler.php

Puedes cambiar el modelo al vuelo si necesitas otro enfoque (por ejemplo, usar a Hermes 3 para razonar sobre lógica de negocio):

python ai_devsec_analyzer.py -f payload.c -m hermes3:latest
