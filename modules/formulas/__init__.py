# ===============================================================
# VPSI-TRUTH — modules/formulas/__init__.py
# ===============================================================
#
# MÓDULO:              formulas
# ID:                  FO
# Rol:                 FO
# Versión módulo:      1.1
# Versión contrato:    1.0
# Esquema contrato:    VPSI-CONTRACT-1.0
# Estabilidad:         ESTABLE
# Compatible desde:    1.0
# API Engine:          >=1.0
#
# Función:
#   Contenedor de fórmulas canónicas del sistema.
#   Expone y ejecuta tru_ri y tru_total, y cualquier fórmula
#   descubierta en los archivos del módulo.
#
# Qué hace:
#   - Descubre y carga todos los archivos .py del módulo
#   - Evalúa tru_ri(C, L, K) y tru_total(C, L, K) sin límites artificiales
#   - Valida coherencia de fórmulas (piso, canónicas)
#   - Expone declaraciones FO-1..FO-4
#   - Inventario, reporte y diagnóstico propios
#
# Qué NO hace:
#   - No calcula C, L, K (los recibe como entrada)
#   - No clasifica entrada de usuario (eso es CX)
#   - No orquesta el sistema (eso es Engine)
#   - No modifica otros módulos
#
# Responsabilidad:
#   Ser la fuente oficial de las fórmulas de verdad y su verificación.
#
# Autoridad:
#   - Ejecutar cualquier fórmula registrada o descubierta en el módulo
#   - Calcular tru_ri y tru_total para cualquier C, L, K válidos
#   - Reportar estado, inventario y diagnóstico propios
#
# Conocimiento exportable:
#   tru_ri, tru_total, fórmulas descubiertas, declaraciones,
#   inventario, estado, reporte, diagnóstico
#
# Relación con Engine:
#   Engine descubre este CONTENEDOR, ejecuta solo las capacidades
#   declaradas y consolida el reporte que este módulo produce.
#
# Relación con Omega:
#   Omega no calcula nada de FO. Solo presenta lo que Engine entrega.
#
# ===============================================================


# ===============================================================
# IMPORTACIONES
# ===============================================================

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

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

ID_MODULO = "FO"
NOMBRE_MODULO = "formulas"
ROL_MODULO = "FO"

VERSION_MODULO = "1.1"
VERSION_CONTRATO = "1.0"
ESQUEMA_CONTRATO = "VPSI-CONTRACT-1.0"

COMPATIBLE_DESDE = "1.0"
API_ENGINE = ">=1.0"
ESTABILIDAD = "ESTABLE"

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

INVARIANTES = (
    "el id del módulo nunca cambia",
    "el rol nunca cambia",
    "las capacidades declaradas son siempre callables tras la resolución",
    "este módulo no modifica el estado de otros módulos",
    "tru_ri y tru_total no imponen límites artificiales sobre C, L, K",
)

PISO_FORMULAS = 1

# ===============================================================
# FIN CONSTANTES
# ===============================================================


# ===============================================================
# CONFIGURACIÓN
# ===============================================================

_DIR = Path(__file__).parent

# ===============================================================
# FIN CONFIGURACIÓN
# ===============================================================


# ===============================================================
# DEFINICIONES
# ===============================================================

class ContratoInvalido(Exception):
    """El CONTENEDOR no cumple el esquema o la resolución falló."""
    pass


class FormulaError(Exception):
    pass


class FormulaNoEncontradaError(Exception):
    pass


# Estado interno del módulo
_DECLARACIONES: List[Dict[str, Any]] = []
_REGLAS: List[Callable[[], List[str]]] = []
_FORMULAS: Dict[str, Dict[str, Any]] = {}

# ===============================================================
# FIN DEFINICIONES
# ===============================================================

# ===============================================================
# CONTRATO OFICIAL DEL MÓDULO
# ===============================================================

CONTENEDOR: Dict[str, Any] = {
    # ============================================================
    # ESQUEMA
    # ============================================================
    "esquema": ESQUEMA_CONTRATO,
    "version_contrato": VERSION_CONTRATO,
    "version_modulo": VERSION_MODULO,
    "estabilidad": ESTABILIDAD,
    "compatible_desde": COMPATIBLE_DESDE,
    "api_engine": API_ENGINE,

    # ============================================================
    # IDENTIDAD
    # ============================================================
    "id": ID_MODULO,
    "nombre": NOMBRE_MODULO,
    "rol": ROL_MODULO,
    "descripcion": (
        "Contenedor de fórmulas. Rol FO. "
        "Expone y ejecuta tru_ri y tru_total, y cualquier fórmula "
        "descubierta en los archivos del módulo. "
        "Sin límites artificiales sobre C, L, K."
    ),

    # ============================================================
    # PROPÓSITO
    # ============================================================
    "funcion": (
        "Ser la fuente oficial de las fórmulas de verdad: "
        "descubrir archivos del módulo, registrar fórmulas, "
        "evaluar tru_ri(C,L,K) y tru_total(C,L,K), validar coherencia."
    ),
    "no_hace": [
        "No calcula C, L, K (los recibe como entrada)",
        "No clasifica entrada de usuario (eso es CX)",
        "No orquesta el sistema (eso es Engine)",
        "No modifica otros módulos",
    ],

    # ============================================================
    # AUTORIDAD
    # ============================================================
    "autoridad": [
        "Ejecutar cualquier fórmula registrada o descubierta en el módulo",
        "Calcular tru_ri y tru_total para cualquier C, L, K válidos",
        "Leer y ejecutar todos los archivos .py del módulo",
        "Reportar estado, inventario y diagnóstico propios",
    ],

    # ============================================================
    # CONOCIMIENTO EXPORTABLE
    # ============================================================
    "conocimiento_exportable": [
        "tru_ri",
        "tru_total",
        "formulas_descubiertas",
        "declaraciones",
        "inventario",
        "estado",
        "reporte",
        "diagnostico",
    ],

    # ============================================================
    # DEPENDENCIAS
    # ============================================================
    "requiere": ["CT", "AX", "MC", "SF", "CA", "CX", "RE", "VX", "TX", "CH", "CIT"],

    # ============================================================
    # AUTORIZACIÓN AL ENGINE (TODOS LOS PERMISOS)
    # ============================================================
    "autoriza_engine": {
        # --- PERMISOS BASE ---
        "leer": True,
        "ejecutar": True,
        "consultar": True,
        "recombinar": True,
        "reportar": True,
        "auditar": True,
        "inventariar": True,

        # --- PERMISOS DE ESCRITURA ---
        "modificar": False,
        "alterar": False,
        "reescribir": False,
        "crear": False,
        "eliminar": False,
        "actualizar": False,

        # --- PERMISOS DE PROCESAMIENTO ---
        "validar": True,
        "procesar": True,
        "analizar": True,
        "generar": False,
        "transformar": False,

        # --- PERMISOS DE DATOS ---
        "exportar": True,
        "importar": False,
        "respaldar": False,
        "recuperar": True,
        "sincronizar": False,

        # --- PERMISOS DE MONITOREO ---
        "monitorear": True,
        "alertar": True,
        "metricas": True,
        "diagnostico": True,

        # --- PERMISOS DE ESTADO (OBLIGATORIOS) ---
        "estado": True,
        "version": True,
        "salud": True,
        "inventario": True,
        "capacidades": True,
        "errores": True,
        "advertencias": True,
        "dependencias": True,
        "contrato": True,
        "conocimiento": True,
        "reporte": True,
    },

    # ============================================================
    # CONSULTAS SOPORTADAS
    # ============================================================
    "consultas_soportadas": [
        "calcular_tru_ri",
        "calcular_tru_total",
        "obtener_inventario",
        "obtener_reporte",
        "obtener_diagnostico",
        "verificar_coherencia",
        "listar_formulas",
        "listar_declaraciones",
    ],

    # ============================================================
    # CAPACIDADES
    # ============================================================
    "capacidades": {
        "verificar": "barrer",
        "barrer": "barrer",
        "evaluar": "barrer",
        "verificar_salida": "verificar_salida",
        "inventario": "inventario",
        "axiomas": "axiomas",
        "tru_ri": "tru_ri",
        "tru_total": "tru_total",
        "reporte": "reporte",
        "diagnostico": "diagnostico",
        "listar_formulas": "listar_formulas",
    },

    # ============================================================
    # METADATOS DE CAPACIDADES (1:1 OBLIGATORIO)
    # ============================================================
    "capacidades_meta": {
        "verificar": {
            "descripcion": "Alias de barrer. Verifica coherencia de fórmulas.",
            "entrada": "ninguna",
            "salida": "dict con coherente, faltas, reglas, formulas",
        },
        "barrer": {
            "descripcion": "Ejecuta todas las reglas y reporta faltas de coherencia.",
            "entrada": "ninguna",
            "salida": "dict con estado, coherente, faltas, reglas, formulas",
        },
        "evaluar": {
            "descripcion": "Alias de barrer. Evalúa coherencia del módulo.",
            "entrada": "ninguna",
            "salida": "dict con estado, coherente, faltas, reglas, formulas",
        },
        "verificar_salida": {
            "descripcion": "Comprueba si una salida de barrer es coherente.",
            "entrada": "salida: dict",
            "salida": "bool",
        },
        "inventario": {
            "descripcion": "Inventario de fórmulas descubiertas y registradas.",
            "entrada": "peticion opcional",
            "salida": "dict con formulas, formulas_registradas, reglas, declaraciones",
        },
        "axiomas": {
            "descripcion": "Declaraciones FO registradas (FO-1..FO-4).",
            "entrada": "ninguna",
            "salida": "list[dict] de declaraciones",
        },
        "tru_ri": {
            "descripcion": (
                "Calcula Tru_Ri = C * L * K. Sin límites artificiales "
                "sobre los valores de C, L, K."
            ),
            "entrada": "C, L, K (numéricos o Fraction)",
            "salida": "resultado de C * L * K",
        },
        "tru_total": {
            "descripcion": (
                "Calcula Tru_total = (Tru_Ri * ALPHA) + BETA. "
                "Sin límites artificiales sobre C, L, K."
            ),
            "entrada": "C, L, K (numéricos o Fraction)",
            "salida": "resultado de (C*L*K)*ALPHA + BETA",
        },
        "reporte": {
            "descripcion": "Reporte interno de estado del módulo FO.",
            "entrada": "ninguna",
            "salida": "dict con estado, coherente, formulas, faltas, capacidades",
        },
        "diagnostico": {
            "descripcion": "Diagnóstico: qué falta, qué está mal en FO.",
            "entrada": "ninguna",
            "salida": "dict con estado, problemas, advertencias, recomendaciones",
        },
        "listar_formulas": {
            "descripcion": "Lista todas las fórmulas descubiertas y registradas.",
            "entrada": "ninguna",
            "salida": "dict con descubiertas y registradas",
        },
    },

    # ============================================================
    # REPORTING
    # ============================================================
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
        "reporte": True,
    },

    # ============================================================
    # ESTADOS VÁLIDOS
    # ============================================================
    "estados_validos": list(ESTADOS_VALIDOS),

    # ============================================================
    # INVARIANTES
    # ============================================================
    "invariantes": list(INVARIANTES),

}  # <--- CIERRE FINAL

# ===============================================================
# FIN CONTRATO
# ===============================================================


# ===============================================================
# FUNCIONES PRIVADAS
# ===============================================================
def regla(fn: Callable[[], List[str]]) -> Callable[[], List[str]]:
    _REGLAS.append(fn)
    return fn


def declarar(d: Dict[str, Any]) -> Dict[str, Any]:
    _DECLARACIONES.append(d)
    return d


def registrar_formula(nombre: str, meta: Dict[str, Any]):
    def decorator(fn: Callable) -> Callable:
        _FORMULAS[nombre] = {**meta, "funcion": fn}
        return fn
    return decorator


def _descubrir_formulas() -> Dict[str, Dict[str, Any]]:
    """Lee y ejecuta absolutamente todos los .py del módulo (excepto _*)."""
    registro: Dict[str, Dict[str, Any]] = {}
    for f in sorted(_DIR.glob("*.py")):
        if f.name.startswith("_") or f.name == "__init__.py":
            continue
        clave = "formulas_{0}".format(f.stem)
        spec = importlib.util.spec_from_file_location(clave, f)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:  # noqa: BLE001
            continue
        meta = getattr(mod, "FORMULA", None)
        if isinstance(meta, dict) and "nombre" in meta:
            registro[meta["nombre"]] = {
                "archivo": f.name,
                "expresion": meta.get("expresion", "No definida"),
                "fuente": meta.get("fuente", "Desconocida"),
            }
    return registro


def _validar_contrato(cont: Dict[str, Any]) -> None:
    obligatorias = (
        "esquema", "version_contrato", "version_modulo",
        "id", "nombre", "rol", "descripcion",
        "funcion", "no_hace", "autoridad",
        "conocimiento_exportable", "requiere",
        "autoriza_engine", "consultas_soportadas",
        "capacidades", "capacidades_meta",
        "reporting", "estados_validos", "invariantes",
        "estabilidad", "compatible_desde", "api_engine",
    )
    faltantes = [k for k in obligatorias if k not in cont]
    if faltantes:
        raise ContratoInvalido(
            f"{NOMBRE_MODULO}: CONTENEDOR incompleto. Faltan: {faltantes}"
        )
    if cont.get("esquema") != ESQUEMA_CONTRATO:
        raise ContratoInvalido(
            f"{NOMBRE_MODULO}: esquema incompatible: {cont.get('esquema')}"
        )
    if str(cont.get("version_contrato")) != VERSION_CONTRATO:
        raise ContratoInvalido(
            f"{NOMBRE_MODULO}: version_contrato inválida: {cont.get('version_contrato')}"
        )
    meta_caps = cont.get("capacidades_meta") or {}
    for nombre_cap in cont.get("capacidades") or {}:
        if nombre_cap not in meta_caps:
            raise ContratoInvalido(
                f"{NOMBRE_MODULO}: capacidad '{nombre_cap}' sin capacidades_meta"
            )
        entrada = meta_caps[nombre_cap]
        if not isinstance(entrada, dict):
            raise ContratoInvalido(
                f"{NOMBRE_MODULO}: capacidades_meta['{nombre_cap}'] debe ser dict"
            )
        for campo in ("descripcion", "entrada", "salida"):
            if campo not in entrada or not isinstance(entrada[campo], str):
                raise ContratoInvalido(
                    f"{NOMBRE_MODULO}: capacidades_meta['{nombre_cap}'] "
                    f"requiere '{campo}: str'"
                )

# ===============================================================
# FIN FUNCIONES PRIVADAS
# ===============================================================


# ===============================================================
# REGLAS
# ===============================================================

@regla
def _validar_piso_formulas() -> List[str]:
    if len(_descubrir_formulas()) < PISO_FORMULAS:
        return [
            "Menos de {0} fórmulas: coherencia por vacuidad".format(
                PISO_FORMULAS
            )
        ]
    return []


@regla
def _validar_formulas_canonicas() -> List[str]:
    faltas = []
    descubiertas = _descubrir_formulas()
    if "tru_ri" not in _FORMULAS and "tru_ri" not in descubiertas:
        faltas.append("Fórmula tru_ri no encontrada.")
    if "tru_total" not in _FORMULAS and "tru_total" not in descubiertas:
        faltas.append("Fórmula tru_total no encontrada.")
    return faltas

# ===============================================================
# FIN REGLAS
# ===============================================================


# ===============================================================
# DECLARACIONES
# ===============================================================

declarar({
    "id": "FO-1",
    "tipo": "axioma",
    "sujeto": "Tru_Ri",
    "relacion": "=",
    "objeto": "C * L * K",
    "polaridad": True,
    "enunciado": (
        "Tru_Ri(D) = C(D) * L(D) * K(D) (Axioma TA5: Multiplicatividad)."
    ),
    "cota": None,
    "depende_de": ["TA5"],
    "gobierna": ["tru_ri"],
})

declarar({
    "id": "FO-2",
    "tipo": "axioma",
    "sujeto": "Tru_total",
    "relacion": "=",
    "objeto": "(Tru_Ri * ALPHA) + BETA",
    "polaridad": True,
    "enunciado": (
        "Tru_total(D) = (Tru_Ri(D) * ALPHA) + BETA (Definición 2.14)."
    ),
    "cota": None,
    "depende_de": ["Def-2.14"],
    "gobierna": ["tru_total"],
})

declarar({
    "id": "FO-3",
    "tipo": "teorema",
    "sujeto": "Tru_Ri",
    "relacion": "≤",
    "objeto": "ALPHA",
    "polaridad": True,
    "enunciado": (
        "Tru_Ri(D) ≤ ALPHA = 26/27 (Teorema 16: Techo Estructural)."
    ),
    "cota": "26/27",
    "depende_de": ["T16"],
    "gobierna": ["tru_ri"],
})

declarar({
    "id": "FO-4",
    "tipo": "teorema",
    "sujeto": "Tru_total",
    "relacion": "≥",
    "objeto": "BETA",
    "polaridad": True,
    "enunciado": (
        "Tru_total(D) ≥ BETA = 1/27 (Teorema 17: Piso Estructural)."
    ),
    "cota": "1/27",
    "depende_de": ["T17"],
    "gobierna": ["tru_total"],
})

# ===============================================================
# FIN DECLARACIONES
# ===============================================================


# ===============================================================
# FÓRMULAS CANÓNICAS
# ===============================================================

from .truth import tru_ri, tru_total, FORMULA as TRUTH_FORMULA  # noqa: E402


@registrar_formula("tru_ri", TRUTH_FORMULA)
def _tru_ri_wrapper(C, L, K):
    """Sin límites artificiales: acepta cualquier C, L, K válidos."""
    return tru_ri(C, L, K)


@registrar_formula("tru_total", TRUTH_FORMULA)
def _tru_total_wrapper(C, L, K):
    """Sin límites artificiales: acepta cualquier C, L, K válidos."""
    return tru_total(C, L, K)

# ===============================================================
# FIN FÓRMULAS CANÓNICAS
# ===============================================================


# ===============================================================
# CAPACIDADES PÚBLICAS
# ===============================================================

def barrer() -> Dict[str, Any]:
    faltas: List[str] = []
    for regla_fn in _REGLAS:
        try:
            faltas.extend(regla_fn() or [])
        except Exception as e:  # noqa: BLE001
            faltas.append(
                "{0}: {1}: {2}".format(
                    regla_fn.__name__, type(e).__name__, e
                )
            )

    if faltas and DiagnosticoGlobal is not None:
        try:
            DiagnosticoGlobal.recibir_reporte(
                modulo="formulas",
                errores=[
                    {"tipo": "falta", "detalle": falta}
                    for falta in faltas
                ],
            )
        except Exception:  # noqa: BLE001
            pass

    return {
        "contenedor": NOMBRE_MODULO,
        "estado": "APROBADO" if not faltas else "RECHAZADO",
        "coherente": not faltas,
        "faltas": faltas,
        "reglas": [r.__name__ for r in _REGLAS],
        "formulas": list(_FORMULAS.keys()) or list(_descubrir_formulas().keys()),
    }


def verificar_salida(salida: Dict[str, Any]) -> bool:
    return bool(salida.get("coherente", False))


def inventario(peticion=None) -> Dict[str, Any]:
    return {
        "id": ID_MODULO,
        "nombre": NOMBRE_MODULO,
        "rol": ROL_MODULO,
        "version": VERSION_MODULO,
        "version_contrato": VERSION_CONTRATO,
        "esquema": ESQUEMA_CONTRATO,
        "estabilidad": ESTABILIDAD,
        "formulas": _descubrir_formulas(),
        "formulas_registradas": list(_FORMULAS.keys()),
        "reglas": len(_REGLAS),
        "declaraciones": len(_DECLARACIONES),
        "capacidades": list(CONTENEDOR["capacidades"].keys()),
        "requiere": list(CONTENEDOR.get("requiere") or []),
        "invariantes": CONTENEDOR.get("invariantes"),
    }


def axiomas() -> List[Dict[str, Any]]:
    return list(_DECLARACIONES)


def listar_formulas() -> Dict[str, Any]:
    return {
        "descubiertas": _descubrir_formulas(),
        "registradas": list(_FORMULAS.keys()),
    }


def verificar() -> Dict[str, Any]:
    return barrer()

# ===============================================================
# FIN CAPACIDADES PÚBLICAS
# ===============================================================


# ===============================================================
# REPORTING INTERNO
# ===============================================================

def reporte() -> Dict[str, Any]:
    r = barrer()
    return {
        "id": ID_MODULO,
        "modulo": NOMBRE_MODULO,
        "rol": ROL_MODULO,
        "version": VERSION_MODULO,
        "version_contrato": VERSION_CONTRATO,
        "esquema": ESQUEMA_CONTRATO,
        "estabilidad": ESTABILIDAD,
        "estado": ESTADO_OPERATIVO if r.get("coherente") else ESTADO_DEGRADADO,
        "coherente": r.get("coherente"),
        "faltas": r.get("faltas"),
        "formulas": r.get("formulas"),
        "reglas": r.get("reglas"),
        "capacidades": list(CONTENEDOR["capacidades"].keys()),
        "requiere": list(CONTENEDOR.get("requiere") or []),
        "autoridad": CONTENEDOR.get("autoridad"),
        "conocimiento_exportable": CONTENEDOR.get("conocimiento_exportable"),
        "consultas_soportadas": CONTENEDOR.get("consultas_soportadas"),
    }


def diagnostico() -> Dict[str, Any]:
    r = barrer()
    problemas = []
    advertencias = []
    recomendaciones = []

    if r.get("faltas"):
        problemas.append({
            "tipo": "faltas_coherencia",
            "detalle": r["faltas"],
        })
        recomendaciones.append("Resolver faltas de fórmulas o reglas")

    if not r.get("formulas"):
        advertencias.append("No hay fórmulas descubiertas ni registradas")
        recomendaciones.append("Verificar archivos .py del módulo formulas")

    estado = ESTADO_OPERATIVO if r.get("coherente") else ESTADO_DEGRADADO
    if not r.get("formulas") and not problemas:
        estado = ESTADO_NO_INICIADO

    return {
        "id": ID_MODULO,
        "modulo": NOMBRE_MODULO,
        "estado": estado,
        "problemas": problemas,
        "advertencias": advertencias,
        "recomendaciones": recomendaciones,
        "coherente": r.get("coherente"),
        "faltas_n": len(r.get("faltas") or []),
        "formulas_n": len(r.get("formulas") or []),
    }

# ===============================================================
# FIN REPORTING
# ===============================================================


# ===============================================================
# VERIFICACIÓN / INVENTARIO
# ===============================================================

# verificar() e inventario() en CAPACIDADES PÚBLICAS

# ===============================================================
# FIN VERIFICACIÓN / INVENTARIO
# ===============================================================


# ===============================================================
# EXPORTACIONES + RESOLUCIÓN ESTRICTA
# ===============================================================

_CAP_MAP = {
    "barrer": barrer,
    "verificar_salida": verificar_salida,
    "inventario": inventario,
    "axiomas": axiomas,
    "tru_ri": tru_ri,
    "tru_total": tru_total,
    "reporte": reporte,
    "diagnostico": diagnostico,
    "listar_formulas": listar_formulas,
    "verificar": verificar,
}


def _resolver_capacidades(cont: Dict[str, Any]) -> None:
    resueltas: Dict[str, Any] = {}
    for nombre, ref in cont["capacidades"].items():
        if callable(ref):
            resueltas[nombre] = ref
            continue
        if isinstance(ref, str):
            if ref not in _CAP_MAP:
                raise ContratoInvalido(
                    f"{NOMBRE_MODULO}: capacidad '{nombre}' "
                    f"referencia inexistente: '{ref}'"
                )
            fn = _CAP_MAP[ref]
            if not callable(fn):
                raise ContratoInvalido(
                    f"{NOMBRE_MODULO}: '{ref}' no es callable"
                )
            resueltas[nombre] = fn
            continue
        raise ContratoInvalido(
            f"{NOMBRE_MODULO}: capacidad '{nombre}' "
            f"tiene tipo inválido: {type(ref).__name__}"
        )
    cont["capacidades"] = resueltas


_validar_contrato(CONTENEDOR)
_resolver_capacidades(CONTENEDOR)

__all__ = [
    "CONTENEDOR",
    "ID_MODULO",
    "NOMBRE_MODULO",
    "ROL_MODULO",
    "VERSION_MODULO",
    "VERSION_CONTRATO",
    "ESQUEMA_CONTRATO",
    "ESTABILIDAD",
    "barrer",
    "verificar_salida",
    "inventario",
    "axiomas",
    "tru_ri",
    "tru_total",
    "listar_formulas",
    "verificar",
    "reporte",
    "diagnostico",
    "FormulaError",
    "FormulaNoEncontradaError",
    "ContratoInvalido",
]

# ===============================================================
# FIN EXPORTACIONES
# ===============================================================


# ===============================================================
# EXTENSIONES FUTURAS
# ===============================================================
#
# Toda capacidad nueva DEBE agregarse simultáneamente en:
#   1. capacidades
#   2. capacidades_meta  (descripcion, entrada, salida: str)
#   3. _CAP_MAP
#   4. VERSION_MODULO
#
# Cualquier archivo .py nuevo en este módulo será descubierto
# automáticamente por _descubrir_formulas().
#
# ===============================================================
# FIN EXTENSIONES FUTURAS
# ===============================================================


# ===============================================================
# FIN DEL MÓDULO
# ===============================================================
