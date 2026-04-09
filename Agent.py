#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agente de Pruebas de Penetración con APIs Múltiples
ADVERTENCIA: Usar solo en sistemas autorizados para pruebas de penetración
"""

import os
import json
import logging
import socket
import requests
from datetime import datetime
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURACIÓN Y LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler("pentest.log"), logging.StreamHandler()]
)

# --- ABSTRACCIÓN DE LLMs (Pattern Strategy) ---
class LLMProvider(ABC):
    @abstractmethod
    def test_connection(self, api_key: str) -> bool:
        pass

class OpenAIProvider(LLMProvider):
    def test_connection(self, api_key: str) -> bool:
        try:
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
                timeout=5
            )
            return r.status_code == 200
        except requests.RequestException:
            return False

# --- NÚCLEO DEL AGENTE ---
class PenetrationTestAgent:
    def __init__(self, target: str, api_keys: Dict[str, str]):
        self.target = target
        self.api_keys = api_keys
        self.session = requests.Session() # Reutilización de conexiones
        self.output_dir = self._setup_workspace()
        self.results = {"dns": {}, "ports": [], "geo": {}}
        
        # Mapeo de proveedores para evitar IF/ELIF
        self._llm_strategies = {
            'openai': OpenAIProvider(),
            # 'anthropic': AnthropicProvider(), ...
        }

    def _setup_workspace(self) -> str:
        path = f"reports/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.target}"
        os.makedirs(path, exist_ok=True)
        return path

    def resolve_target(self) -> Optional[str]:
        try:
            return socket.gethostbyname(self.target)
        except socket.gaierror as e:
            logging.error(f"Error de resolución DNS: {e}")
            return None

    def scan_port(self, port: int, timeout: int = 1):
        """Escaneo de bajo nivel optimizado."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((self.results['dns']['ip'], port)) == 0:
                logging.info(f"Puerto ABIERTO detectado: {port}")
                self.results['ports'].append(port)

    def run_recon(self, ports: List[int]):
        ip = self.resolve_target()
        if not ip: return
        
        self.results['dns'] = {'hostname': self.target, 'ip': ip}
        
        logging.info(f"Iniciando escaneo paralelo sobre {len(ports)} puertos...")
        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(lambda p: self.scan_port(p), ports)

    def validate_infrastructure(self):
        """Valida todas las APIs registradas usando sus estrategias."""
        for name, key in self.api_keys.items():
            strategy = self._llm_strategies.get(name)
            if strategy and strategy.test_connection(key):
                logging.info(f"API {name.upper()}: Operacional")
            else:
                logging.warning(f"API {name.upper()}: Fuera de servicio o Key inválida")

    def save_results(self):
        output_file = os.path.join(self.output_dir, "recon_data.json")
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=4)
        logging.info(f"Resultados exportados a {output_file}")

# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    # En un entorno élite, esto vendría de un .env o HashiCorp Vault
    KEYS = {"openai": "API_KEY_HERE"}
    
    agent = PenetrationTestAgent("google.com", KEYS)
    agent.validate_infrastructure()
    agent.run_recon(ports=[80, 443, 8080, 22])
    agent.save_results()
