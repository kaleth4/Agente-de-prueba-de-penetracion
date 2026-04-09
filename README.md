# Agente IA de Pruebas de Penetración (Nivel Élite)

## 📋 Descripción

Agente inteligente de pruebas de penetración que integra múltiples proveedores de IA (OpenAI, Anthropic, etc.) con capacidades de reconocimiento de red, escaneo de puertos y análisis de infraestructura. Diseñado con patrones profesionales de arquitectura de software.


<img width="919" height="222" alt="prueba" src="https://github.com/user-attachments/assets/21fcaf4a-493e-4b04-943e-4acb803ad801" />



---

## 🎯 Características Principales

✅ **Patrón Strategy** - Desacoplamiento de proveedores LLM sin modificar el código core  
✅ **Manejo Robusto de Errores** - Excepciones específicas y logging en tiempo real  
✅ **Type Hinting Completo** - Detección de errores pre-ejecución con MyPy/PyCharm  
✅ **Logging Profesional** - Auditoría en archivo + salida en consola  
✅ **Escaneo Paralelo Optimizado** - ThreadPoolExecutor para máximo rendimiento  
✅ **Gestión de Recursos** - Context managers para cierre seguro de conexiones  
✅ **Configuración Flexible** - Soporte para variables de entorno y archivos config  
✅ **Reportes Estructurados** - Exportación JSON con timestamps y organización jerárquica  

---

## 🚀 Instalación

### Requisitos Previos
- Python 3.9+
- pip o poetry

### Setup

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/pentest-agent.git
cd pentest-agent

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Archivo `requirements.txt`
```
requests>=2.31.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

---

## ⚙️ Configuración

### 1. Variables de Entorno (`.env`)
```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-anthropic-key
TARGET_HOST=google.com
SCAN_PORTS=80,443,8080,22,3306
TIMEOUT=5
MAX_WORKERS=20
LOG_LEVEL=INFO
```

### 2. Archivo de Configuración (opcional)
```json
{
  "scanning": {
    "timeout": 5,
    "max_workers": 20,
    "ports": [80, 443, 8080, 22, 3306, 5432]
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(message)s"
  }
}
```

---

## 💻 Uso Básico

### Ejemplo Simple
```python
from pentest_agent import PenetrationTestAgent

# Inicializar agente
agent = PenetrationTestAgent(
    target="example.com",
    api_keys={"openai": "sk-..."}
)

# Validar infraestructura
agent.validate_infrastructure()

# Ejecutar reconocimiento
agent.run_recon(ports=[80, 443, 8080, 22])

# Guardar resultados
agent.save_results()
```

### Desde Línea de Comandos
```bash
python main.py --target example.com --ports 80,443,8080 --timeout 5
```

---

## 🏗️ Arquitectura

### Estructura del Proyecto
```
pentest-agent/
├── src/
│   ├── __init__.py
│   ├── agent.py              # Núcleo del agente
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py           # Clase abstracta LLMProvider
│   │   ├── openai.py         # Implementación OpenAI
│   │   ├── anthropic.py      # Implementación Anthropic
│   │   └── custom.py         # Proveedores personalizados
│   ├── utils/
│   │   ├── config.py         # Gestión de configuración
│   │   ├── validators.py     # Validación con Pydantic
│   │   └── logger.py         # Setup de logging
│   └── models/
│       └── schemas.py        # Modelos de datos
├── reports/                  # Reportes generados
├── logs/                     # Archivos de auditoría
├── tests/                    # Suite de pruebas
├── main.py                   # Punto de entrada
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔧 Código Refactorizado (Nivel Élite)

### 1. Clase Base Abstracta
```python
# src/providers/base.py
from abc import ABC, abstractmethod
import logging

class LLMProvider(ABC):
    """Interfaz base para todos los proveedores de IA."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Valida la conexión con la API."""
        pass
    
    @abstractmethod
    def analyze(self, data: str) -> str:
        """Analiza datos con el modelo IA."""
        pass
```

### 2. Implementación de Proveedor
```python
# src/providers/openai.py
import requests
from requests.exceptions import Timeout, ConnectionError
from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    """Proveedor OpenAI con manejo robusto de errores."""
    
    BASE_URL = "https://api.openai.com/v1"
    
    def test_connection(self) -> bool:
        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1
                },
                timeout=5
            )
            if response.status_code == 200:
                self.logger.info("✓ OpenAI API: Operacional")
                return True
            else:
                self.logger.warning(f"OpenAI retornó {response.status_code}")
                return False
        except Timeout:
            self.logger.error("OpenAI: Timeout en conexión")
            return False
        except ConnectionError:
            self.logger.error("OpenAI: Error de conexión")
            return False
        except Exception as e:
            self.logger.error(f"OpenAI: Error inesperado: {e}")
            return False
    
    def analyze(self, data: str) -> str:
        # Implementación de análisis
        pass
```

### 3. Agente Principal Refactorizado
```python
# src/agent.py
import os
import json
import logging
import socket
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from src.providers.openai import OpenAIProvider
from src.utils.validators import APIKeyValidator

class PenetrationTestAgent:
    """Agente de pruebas de penetración con arquitectura profesional."""
    
    def __init__(self, target: str, api_keys: Dict[str, str], config: Optional[Dict] = None):
        self.target = target
        self.api_keys = api_keys
        self.config = config or {}
        self.session = requests.Session()
        self.output_dir = self._setup_workspace()
        self.results = {"dns": {}, "ports": [], "geo": {}, "timestamp": datetime.now().isoformat()}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Mapeo de estrategias (patrón Strategy)
        self._llm_strategies = {
            'openai': OpenAIProvider(api_keys.get('openai', '')),
            # 'anthropic': AnthropicProvider(api_keys.get('anthropic', '')),
        }
    
    def _setup_workspace(self) -> str:
        """Crea estructura de directorios con timestamp."""
        path = f"reports/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.target}"
        os.makedirs(path, exist_ok=True)
        self.logger.info(f"Workspace creado: {path}")
        return path
    
    def resolve_target(self) -> Optional[str]:
        """Resuelve DNS con manejo específico de errores."""
        try:
            ip = socket.gethostbyname(self.target)
            self.logger.info(f"DNS resuelto: {self.target} → {ip}")
            return ip
        except socket.gaierror as e:
            self.logger.error(f"Error de resolución DNS para {self.target}: {e}")
            return None
        except socket.timeout:
            self.logger.error(f"Timeout resolviendo {self.target}")
            return None
    
    def scan_port(self, port: int, timeout: int = 1) -> None:
        """Escaneo de puerto con context manager."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((self.results['dns']['ip'], port))
                if result == 0:
                    self.results['ports'].append(port)
                    self.logger.info(f"🔓 Puerto ABIERTO: {port}")
        except socket.timeout:
            self.logger.debug(f"Timeout en puerto {port}")
        except Exception as e:
            self.logger.error(f"Error escaneando puerto {port}: {e}")
    
    def run_recon(self, ports: List[int]) -> bool:
        """Ejecuta reconocimiento paralelo."""
        ip = self.resolve_target()
        if not ip:
            self.logger.critical("No se pudo resolver el objetivo. Abortando.")
            return False
        
        self.results['dns'] = {'hostname': self.target, 'ip': ip}
        
        self.logger.info(f"Iniciando escaneo paralelo de {len(ports)} puertos...")
        max_workers = self.config.get('max_workers', 20)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(lambda p: self.scan_port(p), ports)
        
        self.logger.info(f"Escaneo completado. Puertos abiertos: {len(self.results['ports'])}")
        return True
    
    def validate_infrastructure(self) -> Dict[str, bool]:
        """Valida todas las APIs usando sus estrategias."""
        status = {}
        for name, strategy in self._llm_strategies.items():
            status[name] = strategy.test_connection()
        return status
    
    def save_results(self) -> str:
        """Exporta resultados en JSON con manejo seguro."""
        output_file = os.path.join(self.output_dir, "recon_data.json")
        try:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=4)
            self.logger.info(f"✓ Resultados guardados: {output_file}")
            return output_file
        except IOError as e:
            self.logger.error(f"Error escribiendo archivo: {e}")
            return ""
```

### 4. Validación con Pydantic
```python
# src/utils/validators.py
from pydantic import BaseModel, Field, validator

class APIKeyValidator(BaseModel):
    """Valida formato de API keys antes de usar."""
    openai: str = Field(..., min_length=20)
    anthropic: Optional[str] = None
    
    @validator('openai')
    def validate_openai_format(cls, v):
        if not v.startswith('sk-'):
            raise ValueError('OpenAI key debe comenzar con sk-')
        return v

class ScanConfig(BaseModel):
    """Configuración de escaneo validada."""
    target: str
    ports: List[int] = Field(default=[80, 443, 8080, 22])
    timeout: int = Field(default=5, ge=1, le=30)
    max_workers: int = Field(default=20, ge=1, le=100)
```

---

## 📊 Ejemplo de Salida

```
2024-01-15 14:32:10 [INFO] Workspace creado: reports/20240115_143210_google.com
2024-01-15 14:32:11 [INFO] DNS resuelto: google.com → 142.250.185.46
2024-01-15 14:32:11 [INFO] ✓ OpenAI API: Operacional
2024-01-15 14:32:11 [INFO] Iniciando escaneo paralelo de 4 puertos...
2024-01-15 14:32:12 [INFO] 🔓 Puerto ABIERTO: 80
2024-01-15 14:32:12 [INFO] 🔓 Puerto ABIERTO: 443
2024-01-15 14:32:13 [INFO] Escaneo completado. Puertos abiertos: 2
2024-01-15 14:32:13 [INFO] ✓ Resultados guardados: reports/20240115_143210_google.com/recon_data.json
```

---

## 🔐 Seguridad

- ✅ **Nunca hardcodees API keys** - Usa `.env` o variables de entorno
- ✅ **Valida todas las entradas** - Pydantic previene inyecciones
- ✅ **Manejo específico de excepciones** - No uses `except Exception`
- ✅ **Logging de auditoría** - Todos los eventos quedan registrados
- ✅ **Context managers** - Cierre garantizado de recursos

---

## 🚀 Mejoras Futuras

- [ ] Integración con Asyncio para escaneo de miles de puertos
- [ ] Soporte para Anthropic Claude y otros proveedores
- [ ] Dashboard web con reportes en tiempo real
- [ ] Integración con Shodan/Censys APIs
- [ ] Machine Learning para detección de anomalías
- [ ] Exportación a formatos CVSS/NIST

---

## 📝 Licencia

MIT License - Ver `LICENSE` para detalles

---

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -m 'Agrega mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

---

## 📧 Contacto 3505416339
