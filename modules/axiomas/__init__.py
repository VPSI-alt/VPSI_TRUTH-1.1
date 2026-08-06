# ===============================================================
# VPSI-TRUTH — modules/axiomas/__init__.py
# ===============================================================
#
# MÓDULO:              axiomas
# ID:                  AX
# Rol:                 AX
# Versión módulo:      9.6
# Versión contrato:    1.0
# Esquema contrato:    VPSI-CONTRACT-1.0
# Estabilidad:         ESTABLE
# Compatible desde:    9.5
# API Engine:          >=1.0
#
# Función:
#   Responsable del conocimiento axiomático del sistema.
#   Mantiene, valida, organiza y expone todas las declaraciones
#   oficiales del repositorio para cualquier módulo autorizado.
#
# Qué hace:
#   - Carga, normaliza y recolecta declaraciones
#   - Detecta contradicción directa y de cota
#   - Expone generatividad (TR1 / capa canónica)
#   - Responde consultas por id, dominio, sujeto, relación, objeto
#   - Genera inventario, reporte y diagnóstico propios
#
# Qué NO hace:
#   - No calcula Tru_total ni Tru_Ri
#   - No clasifica entrada de usuario (eso es CX)
#   - No orquesta el sistema (eso es Engine)
#   - No genera reportes de otros módulos
#   - No modifica declaraciones ajenas
#
# Responsabilidad:
#   Ser la fuente oficial y coherente del conocimiento axiomático.
#
# Autoridad:
#   - Exponer cualquier axioma, lema, teorema, corolario o definición
#   - Responder consultas sobre ellos
#   - Citarlos y relacionarlos
#   - Verificar coherencia interna
#   - Reportar estado, salud, inventario y diagnóstico propios
#
# Conocimiento exportable:
#   declaraciones, referencias, dependencias, dominios,
#   generatividad, choques, inventario, estado, reporte, diagnóstico
#
# Relación con Engine:
#   Engine descubre este CONTENEDOR, ejecuta solo las capacidades
#   declaradas y consolida el reporte que este módulo produce.
#
# Relación con Omega:
#   Omega no calcula nada de AX. Solo presenta lo que Engine entrega.
#
# ===============================================================


# ===============================================================
# IMPORTACIONES
# ===============================================================

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from core.diagnostico import DiagnosticoGlobal  # type: ignore
except Exception:  # noqa: BLE001
    DiagnosticoGlobal = None  # type: ignore

# ===============================================================
# FIN IMPORTACIONES
# ===============================================================


# ===============================================================
# CONSTANTES
# ===============================================================

# Identidad inmutable
ID_MODULO = "AX"
NOMBRE_MODULO = "axiomas"
ROL_MODULO = "AX"

# Versiones
VERSION_MODULO = "9.6"
VERSION_CONTRATO = "1.0"
ESQUEMA_CONTRATO = "VPSI-CONTRACT-1.0"

# Compatibilidad
COMPATIBLE_DESDE = "9.5"
API_ENGINE = ">=1.0"

# Estabilidad
ESTABILIDAD = "ESTABLE"

# Estados centralizados
ESTADO_NO_INICIADO = "NO_INICIADO"
ESTADO_OPERATIVO = "OPERATIVO"
ESTADO_DEGRADADO = "DEGRADADO"
ESTADO_RECHAZADO = "RECHAZADO"
ESTADOS_VALIDOS = (
    ESTADO_NO_INICIADO,
    ESTADO_OPERATIVO,
    ESTADO_DEGRADADO,
    ESTADO_RECHAZADO,
)

# Invariantes
INVARIANTES = (
    "el id del módulo nunca cambia",
    "el rol nunca cambia",
    "las capacidades declaradas son siempre callables tras la resolución",
    "este módulo no modifica el estado de otros módulos",
    "este módulo no inventa capacidades no declaradas en CONTENEDOR",
)

# Dominio axiomático
OBLIGATORIOS = ("id", "tipo", "sujeto", "relacion", "objeto", "polaridad")
TIPOS = ("axioma", "lema", "teorema", "corolario", "definicion")

AXIOMA = "axioma"
LEMA = "lema"
TEOREMA = "teorema"
COROLARIO = "corolario"
DEFINICION = "definicion"

TRADUCCION_CLAVES = {
    "type": "tipo",
    "subject": "sujeto",
    "relation": "relacion",
    "object": "objeto",
    "polarity": "polaridad",
    "statement": "enunciado",
    "depends_on": "depende_de",
    "governs": "gobierna",
    "cota": "cota",
}

DOMINIOS_K_O = frozenset({
    "contexto", "ontologia", "epistemologia", "verificacion",
    "dominio", "k", "o_context", "correlacion",
})

THETA_CANONICO = frozenset({
    "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10",
    "T11", "T12", "T13", "T14", "T15", "T16", "T17",
    "U0", "U1", "M1", "M.1", "B-Canonical", "TT.6.1", "TR1",
})

DOMINIO_CANONICO = {
    "ontologia": "ONT", "ont": "ONT", "informacion": "INF", "info": "INF",
    "logica": "LOG", "log": "LOG", "epistemologia": "EPI", "epi": "EPI",
    "semantica": "SEM", "sem": "SEM", "temporal": "TMP", "tmp": "TMP",
    "meta": "MET", "met": "MET", "constantes": "MET", "self": "EPI",
    "inferencia_causal": "INF", "verificacion": "EPI", "ver": "VER",
    "contexto": "SEM",
}

# ===============================================================
# FIN CONSTANTES
# ===============================================================


# ===============================================================
# CONFIGURACIÓN
# ===============================================================

_DIR = Path(__file__).parent


def _ruta_vpsi() -> Optional[Path]:
    candidatos = [
        _DIR.parent.parent / "VPSI.py",
        _DIR.parent / "VPSI.py",
        _DIR / "VPSI.py",
    ]
    for p in candidatos:
        if p.exists():
            return p
    return None

# ===============================================================
# FIN CONFIGURACIÓN
# ===============================================================


# ===============================================================
# DEFINICIONES
# ===============================================================

class ContratoInvalido(Exception):
    """El CONTENEDOR no cumple el esquema o la resolución de capacidades falló."""
    pass

# ===============================================================
# FIN DEFINICIONES
# ===============================================================


# ===============================================================
# CONTRATO OFICIAL DEL MÓDULO
# ===============================================================

CONTENEDOR: Dict[str, Any] = {
    # ----- ESQUEMA -----
    "esquema": ESQUEMA_CONTRATO,
    "version_contrato": VERSION_CONTRATO,
    "version_modulo": VERSION_MODULO,
    "estabilidad": ESTABILIDAD,
    "compatible_desde": COMPATIBLE_DESDE,
    "api_engine": API_ENGINE,

    # ----- IDENTIDAD -----
    "id": ID_MODULO,
    "nombre": NOMBRE_MODULO,
    "rol": ROL_MODULO,
    "descripcion": (
        "Responsable del conocimiento axiomático del sistema. "
        "Mantiene, valida, organiza y expone todas las declaraciones "
        "oficiales del repositorio."
    ),

    # ----- PROPÓSITO -----
    "funcion": (
        "Ser la fuente oficial del conocimiento axiomático: "
        "cargar, normalizar, validar coherencia, responder consultas "
        "y exponer generatividad."
    ),
    "no_hace": [
        "No calcula Tru_total ni Tru_Ri",
        "No clasifica entrada de usuario (eso es CX)",
        "No orquesta el sistema (eso es Engine)",
        "No genera reportes de otros módulos",
        "No modifica declaraciones ajenas",
    ],

    # ----- AUTORIDAD -----
    "autoridad": [
        "Exponer cualquier axioma, lema, teorema, corolario o definición",
        "Responder consultas por id, dominio, sujeto, relación, objeto",
        "Citar y relacionar declaraciones",
        "Verificar coherencia interna",
        "Reportar estado, salud, inventario y diagnóstico propios",
    ],

    # ----- CONOCIMIENTO EXPORTABLE -----
    "conocimiento_exportable": [
        "declaraciones",
        "referencias",
        "dependencias",
        "dominios",
        "generatividad",
        "choques",
        "inventario",
        "estado",
        "reporte",
        "diagnostico",
    ],

    # ----- DEPENDENCIAS -----
    "requiere": [],

    # ----- AUTORIZACIÓN AL ENGINE -----
    "autoriza_engine": {
        "leer": True,
        "ejecutar": True,
        "consultar": True,
        "recombinar": True,
        "reportar": True,
        "auditar": True,
        "inventariar": True,
        "modificar": False,
        "alterar": False,
        "reescribir": False,
    },

    # ----- CONSULTAS SOPORTADAS -----
    "consultas_soportadas": [
        "buscar_por_id",
        "buscar_por_dominio",
        "obtener_generatividad",
        "obtener_inventario",
        "obtener_reporte",
        "obtener_diagnostico",
        "verificar_coherencia",
        "ids_dominio_k_o",
        "recolectar",
    ],

    # ----- CAPACIDADES -----
    "capacidades": {
        "verificar": "barrer",
        "barrer": "barrer",
        "verificar_salida": "verificar_salida",
        "inventario": "inventario",
        "axiomas": "axiomas",
        "declaraciones": "declaraciones",
        "generatividad": "generatividad",
        "por_dominio": "por_dominio",
        "ids_dominio_k_o": "ids_dominio_k_o",
        "recolectar": "recolectar",
        "reporte": "reporte",
        "diagnostico": "diagnostico",
        "buscar_por_id": "buscar_por_id",
    },

    # ----- METADATOS DE CAPACIDADES -----
    "capacidades_meta": {
        "barrer": {
            "descripcion": "Analiza coherencia de todas las declaraciones.",
            "entrada": "declaraciones_externas opcional",
            "salida": "dict con coherente, choques, errores, declaraciones, ...",
        },
        "inventario": {
            "descripcion": "Inventario completo del módulo.",
            "entrada": "ninguna",
            "salida": "dict con id, nombre, rol, version, declaraciones, cuerpos, ...",
        },
        "generatividad": {
            "descripcion": "Mide generatividad operativa y canónica (TR1).",
            "entrada": "ninguna",
            "salida": "dict con theta_n, pares, im_vs_theta, capa canonica, ...",
        },
        "reporte": {
            "descripcion": "Reporte interno de estado del módulo.",
            "entrada": "ninguna",
            "salida": "dict con estado, coherente, choques, errores, ...",
        },
        "diagnostico": {
            "descripcion": "Diagnóstico: qué me sucede, qué falta, qué está mal.",
            "entrada": "ninguna",
            "salida": "dict con problemas, advertencias, recomendaciones",
        },
        "buscar_por_id": {
            "descripcion": "Busca una declaración por su id.",
            "entrada": "id: str",
            "salida": "dict de la declaración o None",
        },
    },

    # ----- REPORTING -----
    "reporting": {
        "estado": True,
        "salud": True,
        "inventario": True,
        "capacidades": True,
        "errores": True,
        "advertencias": True,
        "dependencias": True,
        "version": True,
        "contrato": True,
        "conocimiento": True,
        "metricas": True,
        "diagnostico": True,
    },

    # ----- ESTADOS VÁLIDOS -----
    "estados_validos": list(ESTADOS_VALIDOS),

    # ----- INVARIANTES -----
    "invariantes": list(INVARIANTES),
}

# ===============================================================
# FIN CONTRATO
# ===============================================================


# ===============================================================
# FUNCIONES PRIVADAS
# ===============================================================

def _cargar_declaraciones_desde_archivo(archivo: Path) -> List[Dict]:
    if archivo.name.startswith("_"):
        return []

    nombre_mod = "axiomas_{0}".format(archivo.stem)
    spec = importlib.util.spec_from_file_location(nombre_mod, archivo)
    if spec is None or spec.loader is None:
        return []

    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre_mod] = mod
    spec.loader.exec_module(mod)

    declaraciones_raw = getattr(mod, "DECLARACIONES", None)
    if declaraciones_raw is None and callable(getattr(mod, "declaraciones", None)):
        try:
            declaraciones_raw = mod.declaraciones()
        except Exception:  # noqa: BLE001
            declaraciones_raw = []

    if declaraciones_raw is None:
        for attr in ("CUERPO", "declaraciones_lista"):
            val = getattr(mod, attr, None)
            if isinstance(val, list):
                declaraciones_raw = val
                break

    return declaraciones_raw if isinstance(declaraciones_raw, list) else []


def normalizar(decl_original: Dict, cuerpo: str) -> Dict:
    if not isinstance(decl_original, dict):
        raise ValueError("{0}: declaración no es dict".format(cuerpo))

    decl: Dict[str, Any] = {}
    for clave_orig, valor in decl_original.items():
        decl[TRADUCCION_CLAVES.get(clave_orig, clave_orig)] = valor

    for k in OBLIGATORIOS:
        if k not in decl:
            raise ValueError(
                "{0}:{1} sin clave obligatoria '{2}'".format(
                    cuerpo, decl.get("id", "?"), k
                )
            )

    tipo = str(decl["tipo"]).lower()
    tipo = {
        "axiom": "axioma",
        "theorem": "teorema",
        "corollary": "corolario",
            }
