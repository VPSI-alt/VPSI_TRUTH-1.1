# ===============================================================
# VPSI-TRUTH — modules/constante/__init__.py
# ===============================================================
#
# MÓDULO:              constante
# ID:                  CT
# Rol:                 CT
# Versión módulo:      2.1
# Versión contrato:    1.0
# Esquema contrato:    VPSI-CONTRACT-1.0
# Estabilidad:         ESTABLE
# Compatible desde:    1.0
# API Engine:          >=1.0
#
# Función:
#   Única autoridad del dominio de constantes del sistema VPSI.
#   Toda constante oficial utilizada por cualquier módulo debe ser
#   declarada, validada y exportada por CT. ALPHA y BETA son las
#   constantes fundacionales estructurales.
#
# Qué hace:
#   - Expone ALPHA = 26/27 y BETA = 1/27 (fundacionales)
#   - Descubre todas las constantes oficiales declaradas en el módulo
#   - Valida, lista y busca constantes
#   - Audita coherencia del dominio de constantes
#   - Inventario, reporte y diagnóstico del conjunto completo
#
# Qué NO hace:
#   - No calcula Tru_total ni Tru_Ri
#   - No clasifica entrada de usuario
#   - No orquesta el sistema (eso es Engine)
#   - No modifica otros módulos
#
# Responsabilidad:
#   Ser la única autoridad del dominio de constantes del sistema VPSI.
#   FO, AX, MC y el resto no definen constantes: todo pasa por CT.
#
# Autoridad:
#   - Exponer ALPHA y BETA
#   - Descubrir, validar y listar constantes oficiales
#   - Auditar coherencia del dominio de constantes
#   - Reportar inventario completo de constantes
#
# Conocimiento exportable:
#   ALPHA, BETA, constantes, inventario, estado, reporte, diagnostico
#
# Relación con Engine:
#   Engine descubre este CONTENEDOR y ejecuta las capacidades
#   declaradas. CT es la autoridad de dominio de constantes;
#   Engine ejerce la agencia autorizada por el contrato.
#
# Relación con Omega:
#   Omega no calcula nada de CT. Solo presenta lo que Engine entrega.
#
# ===============================================================


# ===============================================================
# IMPORTACIONES
# ===============================================================

from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional

# ===============================================================
# FIN IMPORTACIONES
# ===============================================================


# ===============================================================
# CONSTANTES
# ===============================================================

ID_MODULO = "CT"
NOMBRE_MODULO = "constante"
ROL_MODULO = "CT"

VERSION_MODULO = "2.1"
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
    "ALPHA y BETA son invariantes del cubo 3x3x3 en R³",
    "ALPHA + BETA == 1",
    "CT es la única autoridad del dominio de constantes",
    "las capacidades declaradas son siempre callables tras la resolución",
    "este módulo no modifica el estado de otros módulos",
    "este módulo siempre puede reportar su propio estado",
)

ALPHA = Fraction(26, 27)
BETA = Fraction(1, 27)

CONSTANTES_FUNDACIONALES: Dict[str, Any] = {
    "ALPHA": ALPHA,
    "BETA": BETA,
}

FUNDACIONALES = frozenset(CONSTANTES_FUNDACIONALES.keys())

CAMPOS_OBLIGATORIOS_CONSTANTE = ("nombre", "valor", "tipo", "origen", "descripcion")

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
        "Unica autoridad del dominio de constantes del sistema VPSI. "
        "Toda constante oficial utilizada por cualquier modulo debe ser "
        "declarada, validada y exportada por CT. ALPHA y BETA son las "
        "constantes fundacionales estructurales (cubo 3x3x3 en R3)."
    ),

    # ============================================================
    # PROPÓSITO
    # ============================================================
    "funcion": (
        "Ser la unica autoridad del dominio de constantes del sistema VPSI. "
        "Descubrir, validar, integrar, auditar y exportar todas las "
        "constantes oficiales. ALPHA y BETA constituyen las constantes "
        "fundacionales del sistema."
    ),
    "no_hace": [
        "No calcula Tru_total ni Tru_Ri",
        "No clasifica entrada de usuario",
        "No orquesta el sistema (eso es Engine)",
        "No modifica otros modulos",
        "No permite que FO, AX o MC definan constantes",
    ],

    # ============================================================
    # AUTORIDAD
    # ============================================================
    "autoridad": [
        "Unica autoridad del dominio de constantes",
        "Exponer ALPHA = 26/27 y BETA = 1/27",
        "Descubrir y validar constantes oficiales del modulo",
        "Listar y buscar constantes",
        "Auditar coherencia del dominio de constantes",
        "Reportar inventario completo de constantes",
        "Reportar estado y diagnostico propios",
    ],

    # ============================================================
    # CONOCIMIENTO EXPORTABLE
    # ============================================================
    "conocimiento_exportable": [
        "ALPHA",
        "BETA",
        "constantes",
        "inventario",
        "estado",
        "reporte",
        "diagnostico",
    ],

    # ============================================================
    # DEPENDENCIAS
    # ============================================================
    "requiere": [],

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
        "obtener_alpha",
        "obtener_beta",
        "descubrir_constantes",
        "listar_constantes",
        "buscar_constante",
        "verificar_constantes",
        "obtener_inventario",
        "obtener_reporte",
        "obtener_diagnostico",
        "verificar_coherencia",
    ],

    # ============================================================
    # CAPACIDADES
    # ============================================================
    "capacidades": {
        "alpha": "get_alpha",
        "beta": "get_beta",
        "descubrir_constantes": "descubrir_constantes",
        "listar_constantes": "listar_constantes",
        "buscar_constante": "buscar_constante",
        "verificar_constantes": "verificar_constantes",
        "inventario": "inventario",
        "reporte": "reporte",
        "diagnostico": "diagnostico",
        "verificar": "verificar",
    },

    # ============================================================
    # METADATOS DE CAPACIDADES (1:1 OBLIGATORIO)
    # ============================================================
    "capacidades_meta": {
        "alpha": {
            "descripcion": "Devuelve la constante fundacional ALPHA = 26/27.",
            "entrada": "peticion opcional (ignorada)",
            "salida": "Fraction(26, 27)",
        },
        "beta": {
            "descripcion": "Devuelve la constante fundacional BETA = 1/27.",
            "entrada": "peticion opcional (ignorada)",
            "salida": "Fraction(1, 27)",
        },
        "descubrir_constantes": {
            "descripcion": (
                "Descubre todas las constantes oficiales declaradas "
                "dentro del modulo."
            ),
            "entrada": "ninguna",
            "salida": "dict nombre -> meta de constante + errores_carga + total",
        },
        "listar_constantes": {
            "descripcion": "Lista nombres de constantes fundacionales y auxiliares.",
            "entrada": "ninguna",
            "salida": "dict con fundacionales, auxiliares, total",
        },
        "buscar_constante": {
            "descripcion": "Busca una constante oficial por nombre.",
            "entrada": "nombre: str",
            "salida": "dict de la constante o None",
        },
        "verificar_constantes": {
            "descripcion": (
                "Audita el dominio de constantes: invariante fundacional, "
                "duplicados, tipos, campos obligatorios, conflictos y carga."
            ),
            "entrada": "ninguna",
            "salida": "dict con coherente, problemas, advertencias, total_constantes",
        },
        "inventario": {
            "descripcion": "Inventario completo de constantes del modulo.",
            "entrada": "peticion opcional",
            "salida": (
                "dict con total, fundacionales, auxiliares, "
                "constantes descubiertas"
            ),
        },
        "reporte": {
            "descripcion": "Reporte interno de estado del modulo CT.",
            "entrada": "ninguna",
            "salida": "dict con estado, ALPHA, BETA, total_constantes, capacidades",
        },
        "diagnostico": {
            "descripcion": "Diagnostico de coherencia del dominio de constantes.",
            "entrada": "ninguna",
            "salida": "dict con estado, problemas, advertencias, recomendaciones",
        },
        "verificar": {
            "descripcion": "Verifica la invariante fundacional ALPHA + BETA == 1.",
            "entrada": "ninguna",
            "salida": "dict con coherente, ALPHA, BETA, suma",
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

def _archivo_declara_constante(archivo: Path) -> bool:
    try:
        texto = archivo.read_text(encoding="utf-8")
    except Exception:  # noqa: BLE001
        return False
    return "CONSTANTE" in texto


def _descubrir_archivos() -> Dict[str, Any]:
    hallado: Dict[str, Any] = {}
    errores: List[Dict[str, str]] = []
    origen_por_nombre: Dict[str, List[str]] = {}

    for archivo in sorted(_DIR.glob("*.py")):
        if archivo.name.startswith("_") or archivo.name == "__init__.py":
            continue
        if not _archivo_declara_constante(archivo):
            continue

        clave = f"constante_{archivo.stem}"
        spec = importlib.util.spec_from_file_location(clave, archivo)
        if spec is None or spec.loader is None:
            errores.append({
                "archivo": archivo.name,
                "error": "no se pudo crear spec de importacion",
            })
            continue

        mod = importlib.util.module_from_spec(spec)
        sys.modules[clave] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception as e:  # noqa: BLE001
            errores.append({
                "archivo": archivo.name,
                "error": f"archivo_corrupto: {type(e).__name__}: {e}",
            })
            continue

        meta = getattr(mod, "CONSTANTE", None)
        if meta is None:
            continue

        items = meta if isinstance(meta, list) else [meta]
        for item in items:
            if not isinstance(item, dict):
                errores.append({
                    "archivo": archivo.name,
                    "error": "CONSTANTE no es dict ni list[dict]",
                })
                continue

            nombre = str(item.get("nombre", "")).strip()
            if not nombre:
                errores.append({
                    "archivo": archivo.name,
                    "error": "CONSTANTE sin 'nombre'",
                })
                continue

            if nombre in FUNDACIONALES:
                errores.append({
                    "archivo": archivo.name,
                    "error": f"constante_fundacional_redefinida: {nombre}",
                })
                continue

            faltan = [
                c for c in CAMPOS_OBLIGATORIOS_CONSTANTE
                if c not in item or item.get(c) in (None, "")
            ]
            if faltan:
                errores.append({
                    "archivo": archivo.name,
                    "error": f"campos_faltantes en '{nombre}': {faltan}",
                })

            origen_por_nombre.setdefault(nombre, []).append(archivo.name)

            if nombre in hallado:
                errores.append({
                    "archivo": archivo.name,
                    "error": f"nombre_duplicado: {nombre}",
                })
                continue

            hallado[nombre] = {
                "nombre": nombre,
                "valor": item.get("valor"),
                "valor_str": str(item.get("valor")),
                "tipo": str(item.get("tipo", "")),
                "origen": str(item.get("origen", "")),
                "descripcion": str(item.get("descripcion", "")),
                "archivo": archivo.name,
                "fundacional": False,
            }

    for nombre, archivos in origen_por_nombre.items():
        if len(archivos) > 1:
            errores.append({
                "archivo": ",".join(archivos),
                "error": f"conflicto_entre_archivos: '{nombre}' en {archivos}",
            })

    return {"constantes": hallado, "errores": errores}


def _fundacionales() -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for nombre, valor in CONSTANTES_FUNDACIONALES.items():
        out[nombre] = {
            "nombre": nombre,
            "valor": valor,
            "valor_str": str(valor),
            "tipo": type(valor).__name__,
            "origen": "cubo 3x3x3 en R3",
            "descripcion": (
                "Techo estructural" if nombre == "ALPHA" else "Piso estructural"
            ),
            "archivo": "__init__.py",
            "fundacional": True,
        }
    return out


def _todas() -> Dict[str, Any]:
    base = _fundacionales()
    desc = _descubrir_archivos()
    base.update(desc["constantes"])
    return {
        "constantes": base,
        "errores_carga": desc["errores"],
        "archivos": sorted({c["archivo"] for c in base.values()}),
    }


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
            f"{NOMBRE_MODULO}: version_contrato invalida: {cont.get('version_contrato')}"
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
# CAPACIDADES PÚBLICAS
# ===============================================================

def get_alpha(peticion=None) -> Fraction:
    return CONSTANTES_FUNDACIONALES["ALPHA"]


def get_beta(peticion=None) -> Fraction:
    return CONSTANTES_FUNDACIONALES["BETA"]


def descubrir_constantes() -> Dict[str, Any]:
    pack = _todas()
    return {
        "constantes": {
            k: {
                "nombre": v["nombre"],
                "valor_str": v["valor_str"],
                "tipo": v["tipo"],
                "origen": v["origen"],
                "descripcion": v["descripcion"],
                "archivo": v["archivo"],
                "fundacional": v["fundacional"],
            }
            for k, v in pack["constantes"].items()
        },
        "errores_carga": pack["errores_carga"],
        "archivos": pack["archivos"],
        "total": len(pack["constantes"]),
    }


def listar_constantes() -> Dict[str, Any]:
    pack = _todas()
    fund = sorted(k for k, v in pack["constantes"].items() if v["fundacional"])
    aux = sorted(k for k, v in pack["constantes"].items() if not v["fundacional"])
    return {
        "fundacionales": fund,
        "auxiliares": aux,
        "total": len(pack["constantes"]),
        "archivos": pack["archivos"],
    }


def buscar_constante(nombre: str) -> Optional[Dict[str, Any]]:
    pack = _todas()
    c = pack["constantes"].get(str(nombre).strip())
    if c is None:
        return None
    return {
        "nombre": c["nombre"],
        "valor_str": c["valor_str"],
        "tipo": c["tipo"],
        "origen": c["origen"],
        "descripcion": c["descripcion"],
        "archivo": c["archivo"],
        "fundacional": c["fundacional"],
    }


def verificar_constantes() -> Dict[str, Any]:
    problemas: List[Dict[str, Any]] = []
    advertencias: List[str] = []

    alpha = CONSTANTES_FUNDACIONALES["ALPHA"]
    beta = CONSTANTES_FUNDACIONALES["BETA"]
    suma = alpha + beta
    if suma != Fraction(1):
        problemas.append({
            "tipo": "invariante_fundacional",
            "detalle": f"ALPHA + BETA = {suma} != 1",
        })

    pack = _todas()
    for err in pack["errores_carga"]:
        problemas.append({
            "tipo": "error_carga_o_conflicto",
            "detalle": err,
        })

    for nombre, meta in pack["constantes"].items():
        if meta["fundacional"]:
            continue
        if not meta.get("tipo"):
            problemas.append({"tipo": "tipo_invalido_o_vacio", "detalle": nombre})
        if not meta.get("origen"):
            problemas.append({"tipo": "sin_origen", "detalle": nombre})
        if not meta.get("descripcion"):
            problemas.append({"tipo": "sin_descripcion", "detalle": nombre})
        if meta.get("valor") is None and meta.get("valor_str") in ("None", ""):
            problemas.append({"tipo": "constante_sin_valor", "detalle": nombre})

    if not pack["constantes"]:
        advertencias.append("No hay constantes registradas")

    return {
        "coherente": not problemas,
        "ALPHA": str(alpha),
        "BETA": str(beta),
        "suma": str(suma),
        "total_constantes": len(pack["constantes"]),
        "problemas": problemas,
        "advertencias": advertencias,
    }


def verificar() -> Dict[str, Any]:
    alpha = CONSTANTES_FUNDACIONALES["ALPHA"]
    beta = CONSTANTES_FUNDACIONALES["BETA"]
    suma = alpha + beta
    return {
        "coherente": suma == Fraction(1),
        "ALPHA": str(alpha),
        "BETA": str(beta),
        "suma": str(suma),
        "invariante": "ALPHA + BETA == 1",
    }


def inventario(peticion=None) -> Dict[str, Any]:
    pack = _todas()
    fund = {
        k: v["valor_str"]
        for k, v in pack["constantes"].items()
        if v["fundacional"]
    }
    aux = {
        k: {
            "valor_str": v["valor_str"],
            "archivo": v["archivo"],
            "tipo": v["tipo"],
            "origen": v["origen"],
        }
        for k, v in pack["constantes"].items()
        if not v["fundacional"]
    }
    return {
        "id": ID_MODULO,
        "nombre": NOMBRE_MODULO,
        "rol": ROL_MODULO,
        "version": VERSION_MODULO,
        "version_contrato": VERSION_CONTRATO,
        "esquema": ESQUEMA_CONTRATO,
        "estabilidad": ESTABILIDAD,
        "ALPHA": str(CONSTANTES_FUNDACIONALES["ALPHA"]),
        "BETA": str(CONSTANTES_FUNDACIONALES["BETA"]),
        "tipo_fundacionales": "Fraction",
        "origen_fundacionales": "cubo 3x3x3 en R3",
        "total_constantes": len(pack["constantes"]),
        "constantes_fundacionales": fund,
        "constantes_auxiliares": aux,
        "archivos": pack["archivos"],
        "errores_carga": pack["errores_carga"],
        "capacidades": list(CONTENEDOR["capacidades"].keys()),
        "requiere": list(CONTENEDOR.get("requiere") or []),
        "invariantes": CONTENEDOR.get("invariantes"),
    }

# ===============================================================
# FIN CAPACIDADES PÚBLICAS
# ===============================================================


# ===============================================================
# REPORTING INTERNO
# ===============================================================

def reporte() -> Dict[str, Any]:
    v = verificar()
    vc = verificar_constantes()
    pack = _todas()
    estado = ESTADO_OPERATIVO if (v["coherente"] and vc["coherente"]) else ESTADO_DEGRADADO
    return {
        "id": ID_MODULO,
        "modulo": NOMBRE_MODULO,
        "rol": ROL_MODULO,
        "version": VERSION_MODULO,
        "version_contrato": VERSION_CONTRATO,
        "esquema": ESQUEMA_CONTRATO,
        "estabilidad": ESTABILIDAD,
        "estado": estado,
        "coherente": v["coherente"] and vc["coherente"],
        "ALPHA": v["ALPHA"],
        "BETA": v["BETA"],
        "suma": v["suma"],
        "total_constantes": len(pack["constantes"]),
        "archivos": pack["archivos"],
        "capacidades": list(CONTENEDOR["capacidades"].keys()),
        "requiere": list(CONTENEDOR.get("requiere") or []),
        "autoridad": CONTENEDOR.get("autoridad"),
        "conocimiento_exportable": CONTENEDOR.get("conocimiento_exportable"),
        "consultas_soportadas": CONTENEDOR.get("consultas_soportadas"),
    }


def diagnostico() -> Dict[str, Any]:
    v = verificar()
    vc = verificar_constantes()
    problemas = list(vc.get("problemas") or [])
    advertencias = list(vc.get("advertencias") or [])
    recomendaciones: List[str] = []

    if not v["coherente"]:
        recomendaciones.append(
            "Verificar definicion de ALPHA y BETA en CONSTANTES_FUNDACIONALES"
        )
    if vc.get("problemas"):
        recomendaciones.append("Resolver problemas del dominio de constantes")
    if not _descubrir_archivos()["constantes"] and not problemas:
        advertencias.append(
            "Solo hay constantes fundacionales; no hay auxiliares declaradas"
        )

    estado = ESTADO_OPERATIVO if (v["coherente"] and vc["coherente"]) else ESTADO_DEGRADADO
    return {
        "id": ID_MODULO,
        "modulo": NOMBRE_MODULO,
        "estado": estado,
        "problemas": problemas,
        "advertencias": advertencias,
        "recomendaciones": recomendaciones,
        "coherente": v["coherente"] and vc["coherente"],
        "ALPHA": v["ALPHA"],
        "BETA": v["BETA"],
        "suma": v["suma"],
        "total_constantes": vc.get("total_constantes"),
    }

# ===============================================================
# FIN REPORTING
# ===============================================================


# ===============================================================
# EXPORTACIONES + RESOLUCIÓN ESTRICTA
# ===============================================================

_CAP_MAP = {
    "get_alpha": get_alpha,
    "get_beta": get_beta,
    "descubrir_constantes": descubrir_constantes,
    "listar_constantes": listar_constantes,
    "buscar_constante": buscar_constante,
    "verificar_constantes": verificar_constantes,
    "inventario": inventario,
    "reporte": reporte,
    "diagnostico": diagnostico,
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
            f"tiene tipo invalido: {type(ref).__name__}"
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
    "ALPHA",
    "BETA",
    "CONSTANTES_FUNDACIONALES",
    "get_alpha",
    "get_beta",
    "descubrir_constantes",
    "listar_constantes",
    "buscar_constante",
    "verificar_constantes",
    "inventario",
    "verificar",
    "reporte",
    "diagnostico",
    "ContratoInvalido",
]

# ===============================================================
# FIN EXPORTACIONES
# ===============================================================


# ===============================================================
# EXTENSIONES FUTURAS
# ===============================================================
#
# Archivos nuevos solo si declaran CONSTANTE:
#
#   CONSTANTE = {
#       "nombre": "PI",
#       "valor": ...,
#       "tipo": "Fraction",
#       "origen": "...",
#       "descripcion": "...",
#   }
#
# ===============================================================
# FIN EXTENSIONES FUTURAS
# ===============================================================


# ===============================================================
# FIN DEL MÓDULO
# ===============================================================
