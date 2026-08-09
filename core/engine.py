# ===============================================================
# VPSI-TRUTH — core/engine.py
# ===============================================================
# ENGINE
# Versión:            18.3
# Esquema contrato:   VPSI-CONTRACT-1.0
# API Engine:         1.0
# Función:
#   Agente ejecutor del sistema.
#   Descubre módulos. Lee contratos. Valida contratos.
#   Registra módulos. Resuelve dependencias.
#   Construye grafo estructural. Ejecuta capacidades declaradas.
#   Entrega contenido al módulo correspondiente.
#   Recibe el resultado real del módulo.
#   Registra trazas. Registra mapa de ruta de ejecución.
#   Consolida reportes. Entrega paquete_omega().
# Qué NO hace:
#   No inventa capacidades. No adivina campos.
#   No calcula Tru. No explora código fuente.
#   No interpreta reportes.
# Principio:
#   Agencia limitada por la unión coherente de los contratos.
# ===============================================================

from __future__ import annotations
import importlib.util
import inspect
import re
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from core.centinela import Centinela, Veredicto

# ===============================================================
# CONSTANTES
# ===============================================================

VERSION_ENGINE = "18.3"
ESQUEMA_CONTRATO_REQUERIDO = "VPSI-CONTRACT-1.0"
VERSION_CONTRATO_REQUERIDA = "1.0"
API_ENGINE_ACTUAL = "1.0"

ESTADO_NO_INICIADO = "NO_INICIADO"
ESTADO_OPERATIVO = "OPERATIVO"
ESTADO_DEGRADADO = "DEGRADADO"
ESTADO_RECHAZADO = "RECHAZADO"

ESTADOS_CANONICOS = (ESTADO_NO_INICIADO, ESTADO_OPERATIVO, ESTADO_DEGRADADO, ESTADO_RECHAZADO)

CLAVES_OBLIGATORIAS_CONTRATO = ("esquema", "version_contrato", "version_modulo", "id", "nombre", "rol", "descripcion", "funcion", "no_hace", "autoridad", "conocimiento_exportable", "requiere", "autoriza_engine", "consultas_soportadas", "capacidades", "capacidades_meta", "reporting", "estados_validos", "invariantes", "estabilidad", "compatible_desde", "api_engine")

PERMISOS_AUTORIZA_ENGINE = ("leer", "ejecutar", "consultar", "recombinar", "reportar", "auditar", "inventariar", "modificar", "alterar", "reescribir", "metricas", "estado", "version", "salud", "inventario", "capacidades", "errores", "advertencias", "dependencias", "contrato", "conocimiento", "diagnostico", "reporte", "crear", "eliminar", "actualizar", "validar", "procesar", "analizar", "generar", "transformar", "exportar", "importar", "respaldar", "recuperar", "sincronizar", "monitorear", "alertar")

BANDERAS_REPORTING = ("estado", "salud", "inventario", "capacidades", "errores", "advertencias", "dependencias", "version", "contrato", "conocimiento", "metricas", "diagnostico", "reporte")

CLAVES_META_CAPACIDAD = ("descripcion", "entrada", "salida")

LISTAS_STR_OBLIGATORIAS = ("no_hace", "autoridad", "conocimiento_exportable", "consultas_soportadas", "invariantes")

# ===============================================================
# DEFINICIONES
# ===============================================================

class ArranqueError(Exception):
    """Fallo estructural durante el arranque del Engine."""
    pass


class Contenedor:
    """Materialización de un CONTENEDOR. El Engine no completa ni inventa campos del contrato."""

    def __init__(self, meta: Dict[str, Any], modulo: Any, ruta: Path) -> None:
        self.meta = meta
        self.modulo = modulo
        self.ruta = ruta
        self.id: str = str(meta.get("id", ""))
        self.nombre: str = str(meta.get("nombre", ""))
        self.rol: str = str(meta.get("rol", ""))
        self.version: str = str(meta.get("version_modulo", meta.get("version", "")))
        self.version_contrato: str = str(meta.get("version_contrato", ""))
        self.esquema: str = str(meta.get("esquema", ""))
        self.estabilidad: str = str(meta.get("estabilidad", ""))
        self.compatible_desde: str = str(meta.get("compatible_desde", ""))
        self.api_engine: str = str(meta.get("api_engine", ""))
        self.descripcion: str = str(meta.get("descripcion", ""))
        self.funcion = meta.get("funcion")
        self.no_hace = list(meta.get("no_hace") or [])
        self.autoridad = list(meta.get("autoridad") or [])
        self.conocimiento_exportable = list(meta.get("conocimiento_exportable") or [])
        self.consultas_soportadas = list(meta.get("consultas_soportadas") or [])
        self.invariantes = list(meta.get("invariantes") or [])
        self.requiere: List[str] = list(meta.get("requiere") or [])
        self.autoriza_engine: Dict[str, Any] = dict(meta.get("autoriza_engine") or {})
        self.capacidades: Dict[str, Any] = dict(meta.get("capacidades") or {})
        self.capacidades_meta: Dict[str, Any] = dict(meta.get("capacidades_meta") or {})
        self.reporting: Dict[str, Any] = dict(meta.get("reporting") or {})
        self.estados_validos = list(meta.get("estados_validos") or [])

    def fn(self, clave: str) -> Any:
        """Devuelve únicamente la capacidad declarada y callable."""
        ref = self.capacidades.get(clave)
        return ref if callable(ref) else None


class RegistroModulos:

    def __init__(self) -> None:
        self.contenedores: Dict[str, Contenedor] = {}
        self.por_id: Dict[str, Contenedor] = {}
        self.por_rol: Dict[str, List[Contenedor]] = {}

    def registrar(self, cont: Contenedor) -> List[str]:
        errores: List[str] = []
        if cont.nombre in self.contenedores:
            errores.append(f"duplicado de nombre: '{cont.nombre}' ya registrado")
        if cont.id and cont.id in self.por_id:
            errores.append(f"duplicado de id: '{cont.id}' ya registrado (módulo {self.por_id[cont.id].nombre})")
        if cont.rol in self.por_rol and self.por_rol[cont.rol]:
            existente = self.por_rol[cont.rol][0].nombre
            errores.append(f"duplicado de rol: '{cont.rol}' ya ocupado por '{existente}'")
        if errores:
            return errores
        self.contenedores[cont.nombre] = cont
        if cont.id:
            self.por_id[cont.id] = cont
        self.por_rol.setdefault(cont.rol, []).append(cont)
        return []

    def primero(self, clave: Any) -> Optional[Contenedor]:
        if not isinstance(clave, str):
            return None
        if clave in self.contenedores:
            return self.contenedores[clave]
        if clave in self.por_id:
            return self.por_id[clave]
        lista = self.por_rol.get(clave)
        return lista[0] if lista else None

    def total(self) -> int:
        return len(self.contenedores)


# ===============================================================
# ENGINE
# ===============================================================

class Engine:

    VERSION = VERSION_ENGINE

    def __init__(self, raiz_modulos: str | Path, invocador_id: str = "core", strict: bool = True) -> None:
        self.raiz = Path(raiz_modulos).resolve()
        self.invocador_id = invocador_id
        self.strict = strict
        self.estado = ESTADO_NO_INICIADO
        self.registro = RegistroModulos()
        self.errores_arranque: List[str] = []
        self.advertencias: List[str] = []
        self.fallos: List[Dict[str, Any]] = []
        self.resultados_evaluacion: List[Any] = []
        self._trazas: List[Dict[str, Any]] = []
        self._traza_seq: int = 0
        self._mapa_ruta: List[Dict[str, Any]] = []
        self._ruta_seq: int = 0
        self._centinela: Optional[Centinela] = None
        self._modulos_descubiertos: List[Path] = []
        self._reportes_modulos: Dict[str, Any] = {}
        self._diagnosticos: Dict[str, Any] = {}
        self._inventarios: Dict[str, Any] = {}
        self._dependencias: Dict[str, Any] = {}
        self._grafo: Dict[str, Any] = {}
        self._modulos_descubiertos = self._descubrir_modulos()
        self._cargar_y_validar()
        self._resolver_dependencias()
        self._construir_grafo()
        if self.errores_arranque:
            self.estado = ESTADO_RECHAZADO
            if self.strict:
                raise ArranqueError("Engine no pudo arrancar:\n  - " + "\n  - ".join(self.errores_arranque))
        else:
            self.estado = ESTADO_OPERATIVO

    def _descubrir_modulos(self) -> List[Path]:
        if not self.raiz.is_dir():
            return []
        return [p for p in sorted(self.raiz.iterdir()) if p.is_dir() and (p / "__init__.py").is_file()]

    def _leer_contrato(self, path_dir: Path) -> Optional[Dict[str, Any]]:
        init_path = path_dir / "__init__.py"
        nombre_mod = f"vpsi_dinamico_{path_dir.name}"
        try:
            spec = importlib.util.spec_from_file_location(nombre_mod, init_path, submodule_search_locations=[str(path_dir)])
            if spec is None or spec.loader is None:
                return None
            mod = importlib.util.module_from_spec(spec)
            sys.modules[nombre_mod] = mod
            spec.loader.exec_module(mod)
            meta = getattr(mod, "CONTENEDOR", None)
            if not isinstance(meta, dict):
                self.errores_arranque.append(f"{path_dir.name}: CONTENEDOR ausente o no es dict")
                return None
            return {"meta": meta, "modulo": mod, "ruta": init_path, "nombre_carpeta": path_dir.name}
        except Exception as e:
            self.errores_arranque.append(f"{path_dir.name}: error al cargar → {type(e).__name__}: {e}")
            return None

    def _validar_lista_str(self, meta: Dict[str, Any], clave: str, nombre: str) -> List[str]:
        errores: List[str] = []
        val = meta.get(clave)
        if not isinstance(val, list):
            errores.append(f"{nombre}: '{clave}' debe ser list")
            return errores
        for i, item in enumerate(val):
            if not isinstance(item, str):
                errores.append(f"{nombre}: '{clave}[{i}]' debe ser str, es {type(item).__name__}")
        return errores

    @staticmethod
    def _parse_version(s: str) -> Optional[Tuple[int, ...]]:
        m = re.match(r"^(\d+(?:\.\d+)*)", str(s).strip())
        if not m:
            return None
        try:
            return tuple(int(x) for x in m.group(1).split("."))
        except ValueError:
            return None

    def _comparar_api(self, declarado: str) -> Optional[str]:
    raw = str(declarado).strip()
    if not raw:
        return "api_engine vacío"
    exacto, ver_str = (False, raw[2:].strip()) if raw.startswith(">=") else (True, raw)
    requerida = self._parse_version(ver_str)
    if requerida is None:
        return f"api_engine no parseable: '{declarado}'"
    actual = self._parse_version(API_ENGINE_ACTUAL)
    if actual is None:
        return f"API_ENGINE_ACTUAL inválida: '{API_ENGINE_ACTUAL}'"
    n = max(len(requerida), len(actual))
    requerida += (0,) * (n - len(requerida))
    actual += (0,) * (n - len(actual))  # ← LÍNEA CORREGIDA
