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
#   - Carga, normaliza y recolecta declaraciones de todos los archivos
#   - Detecta contradicción directa y de cota
#   - Expone generatividad (TR1 / capa canónica)
#   - Responde consultas por id, dominio, sujeto, relación, objeto
#   - Cita cualquier declaración del grafo
#   - Genera inventario, reporte y diagnóstico propios
#   - Notifica a DiagnosticoGlobal cuando hay choques o errores
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
#   - Responder consultas y citar lo que el grafo contenga
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

ID_MODULO = "AX"
NOMBRE_MODULO = "axiomas"
ROL_MODULO = "AX"

VERSION_MODULO = "9.6"
VERSION_CONTRATO = "1.0"
ESQUEMA_CONTRATO = "VPSI-CONTRACT-1.0"

COMPATIBLE_DESDE = "9.5"
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
    "este módulo no inventa capacidades no declaradas en CONTENEDOR",
    "este módulo siempre puede reportar su propio estado",
)

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
        "Responsable del conocimiento axiomático del sistema. "
        "Mantiene, valida, organiza y expone todas las declaraciones "
        "oficiales del repositorio."
    ),

    # ============================================================
    # PROPÓSITO
    # ============================================================
    "funcion": (
        "Ser la fuente oficial del conocimiento axiomático: "
        "cargar, normalizar, validar coherencia, responder consultas, "
        "citar declaraciones y exponer generatividad."
    ),
    "no_hace": [
        "No calcula Tru_total ni Tru_Ri",
        "No clasifica entrada de usuario (eso es CX)",
        "No orquesta el sistema (eso es Engine)",
        "No genera reportes de otros módulos",
        "No modifica declaraciones ajenas",
    ],

    # ============================================================
    # AUTORIDAD
    # ============================================================
    "autoridad": [
        "Exponer cualquier axioma, lema, teorema, corolario o definición",
        "Responder consultas por id, dominio, sujeto, relación, objeto",
        "Citar y relacionar declaraciones del grafo",
        "Verificar coherencia interna",
        "Reportar estado, salud, inventario y diagnóstico propios",
        "Notificar a DiagnosticoGlobal cuando hay choques o errores",
    ],

    # ============================================================
    # CONOCIMIENTO EXPORTABLE
    # ============================================================
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

    # ============================================================
    # DEPENDENCIAS
    # ============================================================
    "requiere": [],

    # ============================================================
    # CONSULTAS SOPORTADAS
    # ============================================================
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

    # ============================================================
    # CAPACIDADES
    # ============================================================
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

    # ============================================================
    # METADATOS DE CAPACIDADES
    # ============================================================
    "capacidades_meta": {
        "verificar": {
            "descripcion": "Alias de barrer. Verifica coherencia interna del módulo.",
            "entrada": "declaraciones_externas opcional (dict)",
            "salida": "dict con coherente, choques, errores, declaraciones, cuerpos, por_tipo",
        },
        "barrer": {
            "descripcion": "Analiza coherencia de todas las declaraciones (contradicción directa y de cota).",
            "entrada": "declaraciones_externas opcional (dict)",
            "salida": "dict con coherente, choques, errores, declaraciones, cuerpos, por_tipo, ids_dominio_k_o",
        },
        "verificar_salida": {
            "descripcion": "Comprueba si una salida de barrer/verificar es coherente.",
            "entrada": "salida: dict",
            "salida": "bool",
        },
        "inventario": {
            "descripcion": "Inventario completo del módulo (declaraciones, cuerpos, capacidades).",
            "entrada": "peticion opcional",
            "salida": "dict con id, nombre, rol, version, declaraciones, cuerpos, capacidades",
        },
        "axiomas": {
            "descripcion": "Devuelve las declaraciones si el módulo es coherente; lista vacía si no.",
            "entrada": "declaraciones_externas opcional (dict)",
            "salida": "list[dict] de declaraciones normalizadas",
        },
        "declaraciones": {
            "descripcion": "Igual que axiomas: declaraciones normalizadas si coherente.",
            "entrada": "declaraciones_externas opcional (dict)",
            "salida": "list[dict] de declaraciones normalizadas",
        },
        "generatividad": {
            "descripcion": "Mide generatividad operativa y canónica (TR1).",
            "entrada": "ninguna",
            "salida": "dict con theta_n, pares, im_vs_theta, capa canonica, dominios, u1_proxy",
        },
        "por_dominio": {
            "descripcion": "Filtra declaraciones por dominio en gobierna.",
            "entrada": "dominio: str; declaraciones_externas opcional",
            "salida": "list[dict] de declaraciones del dominio",
        },
        "ids_dominio_k_o": {
            "descripcion": "Ids de declaraciones ligadas a dominios K/O o Def-5.3.1.",
            "entrada": "declaraciones_externas opcional (dict)",
            "salida": "list[str] de ids ordenados",
        },
        "recolectar": {
            "descripcion": "Carga y normaliza todas las declaraciones de los cuerpos del módulo.",
            "entrada": "declaraciones_externas opcional (dict)",
            "salida": "tuple[list[dict], list[dict]] → (declaraciones, errores)",
        },
        "reporte": {
            "descripcion": "Reporte interno de estado del módulo.",
            "entrada": "ninguna",
            "salida": "dict con estado, coherente, declaraciones, choques, errores, capacidades",
        },
        "diagnostico": {
            "descripcion": "Diagnóstico: qué me sucede, qué falta, qué está mal, qué necesito.",
            "entrada": "ninguna",
            "salida": "dict con estado, problemas, advertencias, recomendaciones",
        },
        "buscar_por_id": {
            "descripcion": "Busca y cita una declaración por su id.",
            "entrada": "id_decl: str",
            "salida": "dict de la declaración o None",
        },
    },

    # ============================================================
    # AUTORIZACIÓN AL ENGINE (SOLO PERMISOS)
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
        "crear": True,
        "eliminar": False,
        "actualizar": False,

        # --- PERMISOS DE PROCESAMIENTO ---
        "validar": True,
        "procesar": True,
        "analizar": True,
        "generar": True,
        "transformar": False,

        # --- PERMISOS DE DATOS ---
        "exportar": True,
        "importar": True,
        "respaldar": True,
        "recuperar": True,
        "sincronizar": True,

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
    # REPORTING (NECESARIO PARA EL CONTRATO)
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
        "lemma": "lema",
        "definition": "definicion",
    }.get(tipo, tipo)

    if tipo not in TIPOS:
        raise ValueError(
            "{0}:{1} tipo '{2}' no válido. Admitidos: {3}".format(
                cuerpo, decl["id"], tipo, TIPOS
            )
        )
    if not isinstance(decl["polaridad"], bool):
        raise ValueError(
            "{0}:{1} polaridad debe ser bool".format(cuerpo, decl["id"])
        )

    return {
        "id": str(decl["id"]),
        "cuerpo": cuerpo,
        "tipo": tipo,
        "sujeto": str(decl["sujeto"]),
        "relacion": str(decl["relacion"]),
        "objeto": str(decl["objeto"]),
        "polaridad": bool(decl["polaridad"]),
        "cota": None if decl.get("cota") is None else str(decl["cota"]),
        "depende_de": [str(x) for x in decl.get("depende_de", [])],
        "gobierna": [str(x) for x in decl.get("gobierna", [])],
        "enunciado": str(decl.get("enunciado", "")),
    }


def clave(d: Dict) -> Tuple[str, str, str]:
    return (
        d["sujeto"].lower().strip(),
        d["relacion"].lower().strip(),
        d["objeto"].lower().strip(),
    )


def ref(d: Dict) -> str:
    return "{0}:{1}".format(d["cuerpo"], d["id"])


def contradiccion_directa(decls: List[Dict]) -> List[Dict]:
    grupos: Dict[Tuple[str, str, str], List[Dict]] = {}
    for d in decls:
        grupos.setdefault(clave(d), []).append(d)

    choques: List[Dict] = []
    for k, grupo in grupos.items():
        afirman = [d for d in grupo if d["polaridad"]]
        niegan = [d for d in grupo if not d["polaridad"]]
        for a in afirman:
            for n in niegan:
                choques.append({
                    "tipo": "contradiccion_directa",
                    "tripleta": " - ".join(k),
                    "declaracion_1": {
                        "id": a["id"],
                        "ubicacion": ref(a),
                        "enunciado": a["enunciado"],
                    },
                    "declaracion_2": {
                        "id": n["id"],
                        "ubicacion": ref(n),
                        "enunciado": n["enunciado"],
                    },
                    "mensaje": (
                        "Contradicción en '{0}': {1} AFIRMA vs {2} NIEGA".format(
                            " - ".join(k), ref(a), ref(n)
                        )
                    ),
                })
    return choques


def contradiccion_de_cota(decls: List[Dict]) -> List[Dict]:
    grupos: Dict[Tuple[str, str], List[Dict]] = {}
    for d in decls:
        if d["cota"] is None:
            continue
        grupos.setdefault(
            (d["sujeto"].lower().strip(), d["relacion"].lower().strip()),
            [],
        ).append(d)

    choques: List[Dict] = []
    for (suj, rel), grupo in grupos.items():
        porcota: Dict[str, List[str]] = {}
        for d in grupo:
            porcota.setdefault(d["cota"], []).append(ref(d))
        if len(porcota) > 1:
            choques.append({
                "tipo": "contradiccion_de_cota",
                "sujeto": suj,
                "relacion": rel,
                "cotas": porcota,
                "mensaje": (
                    "Contradicción de cota en '{0} {1}'. Cotas: {2}".format(
                        suj, rel, list(porcota.keys())
                    )
                ),
            })
    return choques


def _dominios_canonicos(gobierna) -> set:
    out = set()
    for g in gobierna or []:
        key = str(g).lower().strip()
        out.add(DOMINIO_CANONICO.get(key, key.upper()[:3]))
    return out


def _medir_pares(theta: list) -> dict:
    n = len(theta)
    pares_tot = n * (n - 1) // 2 if n >= 2 else 0
    compatibles = 0
    novedosos = 0
    for i in range(n):
        Di = theta[i]["dominios"]
        for j in range(i + 1, n):
            Dj = theta[j]["dominios"]
            if not (Di & Dj):
                continue
            compatibles += 1
            union = Di | Dj
            if union > Di and union > Dj:
                novedosos += 1
    return {
        "theta_n": n,
        "pares_totales": pares_tot,
        "pares_compatibles": compatibles,
        "pares_novedosos": novedosos,
        "im_vs_theta": (
            "GENERATIVO"
            if n > 0 and novedosos > n
            else ("ESTANCADO" if n > 0 else "SIN_DATOS")
        ),
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
# CAPACIDADES PÚBLICAS
# ===============================================================

def recolectar(
    declaraciones_externas: Optional[Dict[str, List[Dict]]] = None,
) -> Tuple[List[Dict], List[Dict]]:
    decls: List[Dict] = []
    errores: List[Dict] = []

    for archivo in sorted(_DIR.glob("**/*.py")):
        if archivo.name == "__init__.py":
            continue
        try:
            for d in _cargar_declaraciones_desde_archivo(archivo):
                decls.append(normalizar(d, archivo.stem))
        except Exception as e:  # noqa: BLE001
            errores.append({
                "archivo": archivo.name,
                "error": "{0}: {1}".format(type(e).__name__, e),
            })

    vpsi = _ruta_vpsi()
    if vpsi is not None:
        try:
            for d in _cargar_declaraciones_desde_archivo(vpsi):
                decls.append(normalizar(d, "VPSI"))
        except Exception as e:  # noqa: BLE001
            errores.append({
                "archivo": str(vpsi.name),
                "error": "{0}: {1}".format(type(e).__name__, e),
            })

    if declaraciones_externas:
        for nombre, lista in declaraciones_externas.items():
            if not isinstance(lista, list):
                errores.append({
                    "modulo": nombre,
                    "error": "declaraciones externas no es lista",
                })
                continue
            for d in lista:
                try:
                    decls.append(normalizar(d, nombre))
                except ValueError as e:
                    errores.append({"modulo": nombre, "error": str(e)})

    return decls, errores


def por_dominio(
    dominio: str,
    declaraciones_externas: Optional[Dict[str, List[Dict]]] = None,
) -> List[Dict]:
    dom = str(dominio).lower().strip()
    decls, _ = recolectar(declaraciones_externas)
    out = []
    for d in decls:
        gobs = [str(g).lower().strip() for g in (d.get("gobierna") or [])]
        if dom in gobs or any(dom in g for g in gobs):
            out.append(d)
    return out


def ids_dominio_k_o(
    declaraciones_externas: Optional[Dict[str, List[Dict]]] = None,
) -> List[str]:
    decls, _ = recolectar(declaraciones_externas)
    ids: List[str] = []
    for d in decls:
        gobs = {str(g).lower().strip() for g in (d.get("gobierna") or [])}
        if gobs & DOMINIOS_K_O:
            ids.append(d["id"])
        blob = (
            "{0} {1} {2}".format(
                d.get("sujeto", ""),
                d.get("objeto", ""),
                d.get("enunciado", ""),
            )
        ).lower()
        if any(
            x in blob
            for x in ("def-5.3.1", "o_context", "dominio o", "permite_k")
        ):
            if d["id"] not in ids:
                ids.append(d["id"])
    return sorted(set(ids))


def barrer(
    declaraciones_externas: Optional[Dict[str, List[Dict]]] = None,
) -> Dict:
    decls, errores = recolectar(declaraciones_externas)
    choques = contradiccion_directa(decls) + contradiccion_de_cota(decls)

    if (choques or errores) and DiagnosticoGlobal is not None:
        try:
            DiagnosticoGlobal.recibir_reporte(
                modulo="axiomas",
                errores=(
                    [{"tipo": "choque", "detalle": c} for c in choques]
                    + [{"tipo": "error_carga", "detalle": e} for e in errores]
                ),
            )
        except Exception:  # noqa: BLE001
            pass

    cuerpos = sorted({d["cuerpo"] for d in decls})
    por_tipo = {t: sum(1 for d in decls if d["tipo"] == t) for t in TIPOS}

    return {
        "coherente": not (choques or errores),
        "choques": choques,
        "errores": errores,
        "declaraciones": len(decls),
        "cuerpos": cuerpos,
        "por_tipo": por_tipo,
        "ids_dominio_k_o": (
            ids_dominio_k_o(declaraciones_externas)
            if not (choques or errores)
            else []
        ),
    }


def verificar_salida(salida: Dict) -> bool:
    return bool(salida.get("coherente", False))


def declaraciones(
    declaraciones_externas: Optional[Dict[str, List[Dict]]] = None,
) -> List[Dict]:
    resultado = barrer(declaraciones_externas)
    if not resultado["coherente"]:
        return []
    decls, _ = recolectar(declaraciones_externas)
    return decls


def axiomas(
    declaraciones_externas: Optional[Dict[str, List[Dict]]] = None,
) -> List[Dict]:
    return declaraciones(declaraciones_externas)


def generatividad() -> dict:
    decls, errores = recolectar()

    oper = []
    for d in decls:
        if d.get("tipo") not in ("teorema", "axioma"):
            continue
        gob = d.get("gobierna") or []
        if not gob:
            continue
        oper.append({
            "id": d["id"],
            "tipo": d["tipo"],
            "dominios": set(gob),
        })
    m_op = _medir_pares(oper)
    dominios_op = sorted({g for n in oper for g in n["dominios"]})

    por_id = {}
    for d in decls:
        i = str(d.get("id", ""))
        if i in THETA_CANONICO:
            cand = {
                "id": i,
                "tipo": d.get("tipo"),
                "dominios": _dominios_canonicos(d.get("gobierna")),
            }
            prev = por_id.get(i)
            if prev is None or len(cand["dominios"]) >= len(prev["dominios"]):
                por_id[i] = cand

    can = [por_id[i] for i in sorted(por_id.keys()) if por_id[i]["dominios"]]
    m_can = _medir_pares(can)
    dominios_can = sorted({g for n in can for g in n["dominios"]})
    faltan = sorted(THETA_CANONICO - set(por_id.keys()))
    sin_dominio = sorted(i for i, n in por_id.items() if not n["dominios"])

    u1_proxy = (
        "NO_STAGNANT"
        if m_can.get("pares_novedosos", 0) > 0
        or m_op.get("pares_novedosos", 0) > 0
        else "REVISAR"
    )

    return {
        "contenedor": "axiomas",
        "theta_n": m_op["theta_n"],
        "pares_totales": m_op["pares_totales"],
        "pares_compatibles": m_op["pares_compatibles"],
        "pares_novedosos": m_op["pares_novedosos"],
        "im_vs_theta": m_op["im_vs_theta"],
        "dominios": dominios_op,
        "u1_proxy": u1_proxy,
        "errores_recoleccion": len(errores),
        "por_tipo_theta": {
            "axioma": sum(1 for n in oper if n["tipo"] == "axioma"),
            "teorema": sum(1 for n in oper if n["tipo"] == "teorema"),
        },
        "canonica": {
            **m_can,
            "ids_presentes": sorted(por_id.keys()),
            "ids_faltantes": faltan,
            "ids_sin_dominio": sin_dominio,
            "dominios": dominios_can,
            "objetivo_paper": {
                "theta_n": 24,
                "im_esperada": 153,
                "nota": "|Im(⊕)|=153 > 24=|Θ| en enumeración del texto",
            },
        },
        "ids_dominio_k_o": ids_dominio_k_o(),
        "nota": (
            "Capa operativa = grafo del repo. "
            "Capa canonica = solo ids TR1 del paper. "
            "Dominio O/K: ver ids_dominio_k_o y cuerpos."
        ),
    }


def buscar_por_id(id_decl: str) -> Optional[Dict]:
    decls, _ = recolectar()
    for d in decls:
        if d.get("id") == id_decl:
            return d
    return None


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
        "declaraciones": r.get("declaraciones"),
        "choques": len(r.get("choques") or []),
        "errores": len(r.get("errores") or []),
        "cuerpos": r.get("cuerpos"),
        "por_tipo": r.get("por_tipo"),
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

    if r.get("errores"):
        problemas.append({"tipo": "errores_carga", "detalle": r["errores"]})
        recomendaciones.append("Revisar archivos de cuerpos con error de carga")

    if r.get("choques"):
        problemas.append({
            "tipo": "contradicciones",
            "cantidad": len(r["choques"]),
            "detalle": r["choques"][:5],
        })
        recomendaciones.append("Resolver contradicciones directas o de cota")

    if not r.get("declaraciones"):
        advertencias.append("No hay declaraciones cargadas")
        recomendaciones.append("Verificar que existan cuerpos .py con DECLARACIONES")

    estado = ESTADO_OPERATIVO
    if problemas:
        estado = ESTADO_DEGRADADO
    if not r.get("declaraciones") and not problemas:
        estado = ESTADO_NO_INICIADO

    return {
        "id": ID_MODULO,
        "modulo": NOMBRE_MODULO,
        "estado": estado,
        "problemas": problemas,
        "advertencias": advertencias,
        "recomendaciones": recomendaciones,
        "coherente": r.get("coherente"),
        "declaraciones": r.get("declaraciones"),
        "choques_n": len(r.get("choques") or []),
        "errores_n": len(r.get("errores") or []),
    }

# ===============================================================
# FIN REPORTING
# ===============================================================


# ===============================================================
# INVENTARIO
# ===============================================================

def inventario(peticion=None) -> Dict:
    decls, errores = recolectar()
    return {
        "id": ID_MODULO,
        "nombre": NOMBRE_MODULO,
        "rol": ROL_MODULO,
        "version": VERSION_MODULO,
        "version_contrato": VERSION_CONTRATO,
        "esquema": ESQUEMA_CONTRATO,
        "estabilidad": ESTABILIDAD,
        "tipos": list(TIPOS),
        "declaraciones": len(decls),
        "por_tipo": {
            t: sum(1 for d in decls if d["tipo"] == t) for t in TIPOS
        },
        "cuerpos": sorted({d["cuerpo"] for d in decls}),
        "errores": errores,
        "capacidades": list(CONTENEDOR["capacidades"].keys()),
        "requiere": list(CONTENEDOR.get("requiere") or []),
        "autoridad": CONTENEDOR.get("autoridad"),
        "conocimiento_exportable": CONTENEDOR.get("conocimiento_exportable"),
        "consultas_soportadas": CONTENEDOR.get("consultas_soportadas"),
        "invariantes": CONTENEDOR.get("invariantes"),
        "vigila": ["contradiccion_directa", "contradiccion_de_cota"],
        "ids_dominio_k_o": ids_dominio_k_o(),
        "nota": (
            "Def-5.3.1 y dominio O viven en los cuerpos cargados; "
            "este módulo los vigila y expone, no los clasifica en entrada."
        ),
    }

# ===============================================================
# FIN INVENTARIO
# ===============================================================


# ===============================================================
# EXPORTACIONES + RESOLUCIÓN ESTRICTA
# ===============================================================

_CAP_MAP = {
    "barrer": barrer,
    "verificar_salida": verificar_salida,
    "inventario": inventario,
    "axiomas": axiomas,
    "declaraciones": declaraciones,
    "generatividad": generatividad,
    "por_dominio": por_dominio,
    "ids_dominio_k_o": ids_dominio_k_o,
    "recolectar": recolectar,
    "reporte": reporte,
    "diagnostico": diagnostico,
    "buscar_por_id": buscar_por_id,
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
    "AXIOMA",
    "LEMA",
    "TEOREMA",
    "COROLARIO",
    "DEFINICION",
    "TIPOS",
    "normalizar",
    "clave",
    "ref",
    "recolectar",
    "por_dominio",
    "ids_dominio_k_o",
    "declaraciones",
    "axiomas",
    "contradiccion_directa",
    "contradiccion_de_cota",
    "barrer",
    "verificar_salida",
    "inventario",
    "generatividad",
    "verificar",
    "reporte",
    "diagnostico",
    "buscar_por_id",
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
# ===============================================================
# FIN EXTENSIONES FUTURAS
# ===============================================================


# ===============================================================
# FIN DEL MÓDULO
# ===============================================================
