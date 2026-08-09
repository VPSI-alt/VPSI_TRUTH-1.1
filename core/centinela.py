# ===============================================================
# VPSI-TRUTH — core/centinela.py
# ===============================================================
#
# Centinela v5.3
#
# Clasificación del paquete (solo lo que trae el paquete):
#   SIN_PAQUETE_AUDITABLE
#   SOLO_ESTRUCTURAL
#   CANDIDATO_OPERACIONAL
#
# Confirmación tras CACHE:
#   tipo_auditoria = ESTRUCTURAL | OPERACIONAL
#
# ===============================================================

from __future__ import annotations

import copy
import hashlib
import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List, Optional, Protocol, Set, Tuple

from core.paquete_contrato import (
    PKG_CICLO_ID,
    PKG_CONTEXTO,
    PKG_ESTADO,
    PKG_ESTADO_OK,
    PKG_ESTADO_PARCIAL,
    PKG_ESTADO_UNDEFINED,
    PKG_ESTADOS_VALIDOS,
    PKG_O_CONTEXT,
)
from modules.cache.cs import (
    CS_CAMPO_CICLO_ID,
    CS_CAMPO_ESTADO,
    CS_CAMPO_MOTIVOS,
    CS_CAMPO_PAQUETE_REF,
    CS_CAMPO_VEREDICTO,
    CS_CATEGORIA_VEREDICTO,
    CS_ESTADO_APROBADO,
    CS_ESTADO_PARCIAL,
    CS_ESTADO_RETENIDO,
    CS_TIPO_VEREDICTO,
    MODULO as CS_MODULO,
    VERSION_EVENTOS as CS_VERSION_EVENTOS,
)
from modules.cache.en import (
    EN_CAMPO_PAQUETE,
    EN_CATEGORIA_SALIDA,
    EN_TIPO_CICLO_FIN,
    MODULO as EN_MODULO,
)


# ===============================================================
# IDENTIDAD
# ===============================================================

CS_ID = "CS"
CS_NOMBRE = "centinela"
CS_ROL = "CS"
CS_VERSION = "5.3"
CS_ESQUEMA = "VPSI-CONTRACT-1.0"
CS_VERSION_CONTRATO = "1.0"

CS_FUNCION = (
    "Intérprete universal del expediente de CACHE y de los contratos "
    "depositados. Certifica la salida de Engine sin conocimiento de dominio."
)

CS_NO_HACE = (
    "No orquesta el ciclo",
    "No modifica factores ni contexto",
    "No inventa evidencia",
    "No reconstruye evidencia inexistente",
    "No hardcodea variables, fórmulas ni tipos de dominio",
    "No importa módulos de cálculo",
)

CS_AUTORIDAD = (
    "Consultar el expediente completo del ciclo en CACHE",
    "Descubrir contratos, capacidades, dependencias y variables",
    "Verificar coherencia, autorizaciones, secuencia e integridad",
    "Reproducir capacidades vía invocador dinámico",
    "Emitir veredicto y registrarlo en CACHE",
)

CS_ESTADO_SOLO_ESTRUCTURAL = "SOLO_ESTRUCTURAL"
CS_ESTADO_SIN_PAQUETE_AUDITABLE = "SIN_PAQUETE_AUDITABLE"

CS_ESTADOS = (
    CS_ESTADO_APROBADO,
    CS_ESTADO_RETENIDO,
    CS_ESTADO_PARCIAL,
    CS_ESTADO_SOLO_ESTRUCTURAL,
    CS_ESTADO_SIN_PAQUETE_AUDITABLE,
)

# Clasificación provisional (solo paquete)
CLASE_SIN_PAQUETE = CS_ESTADO_SIN_PAQUETE_AUDITABLE
CLASE_ESTRUCTURAL = CS_ESTADO_SOLO_ESTRUCTURAL
CLASE_CANDIDATO_OPERACIONAL = "CANDIDATO_OPERACIONAL"

# tipo_auditoria confirmado (tras CACHE si aplica)
TIPO_AUDITORIA_ESTRUCTURAL = "ESTRUCTURAL"
TIPO_AUDITORIA_OPERACIONAL = "OPERACIONAL"

_CLAVES_FORMA = frozenset({
    PKG_CICLO_ID, PKG_ESTADO, PKG_O_CONTEXT, PKG_CONTEXTO,
    "tipo", "origen", "modulo", "capacidad", "categoria",
    "seq", "timestamp", "payload", "ciclo_id", "estado",
    "error", "errores", "advertencias", "notas", "mensaje",
    "mensajes", "contrato", "CONTENEDOR", "contenedor",
    "entrada", "resultado", "requiere", "version", "version_modulo",
    "version_contrato", "esquema", "autoriza_engine", "capacidades",
    "capacidades_meta", "reporting", "invariantes", "descripcion",
    "nombre", "rol", "id", "funcion", "no_hace", "autoridad",
})


# ===============================================================
# PROTOCOLOS
# ===============================================================

class CacheEvidencia(Protocol):
    def guardar(self, registro: Dict[str, Any]) -> None: ...
    def leer_ciclo(self, ciclo_id: str) -> List[Dict[str, Any]]: ...


class InvocadorCapacidades(Protocol):
    def invocar(
        self,
        modulo: str,
        capacidad: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any: ...


# ===============================================================
# CACHE
# ===============================================================

class _CacheMemoriaLocal:
    def __init__(self) -> None:
        self._regs: List[Dict[str, Any]] = []

    def guardar(self, registro: Dict[str, Any]) -> None:
        self._regs.append(dict(registro))

    def leer_ciclo(self, ciclo_id: str) -> List[Dict[str, Any]]:
        return [
            dict(r)
            for r in self._regs
            if str(r.get(PKG_CICLO_ID)) == str(ciclo_id)
        ]


class _CachePublicoAdapter:
    def guardar(self, registro: Dict[str, Any]) -> None:
        from modules.cache import depositar

        tipo = str(registro.get("tipo") or CS_TIPO_VEREDICTO)
        omitir = {
            "tipo", PKG_CICLO_ID, "origen", "modulo",
            "categoria", "estado", "capacidad",
        }
        payload = {k: v for k, v in registro.items() if k not in omitir}
        depositar(
            tipo,
            payload,
            ciclo_id=registro.get(PKG_CICLO_ID),
            origen=registro.get("origen"),
        )

    def leer_ciclo(self, ciclo_id: str) -> List[Dict[str, Any]]:
        try:
            from modules.cache import leer_por_ciclo
            return list(leer_por_ciclo(str(ciclo_id)))
        except Exception:
            pass
        try:
            from modules.cache import secuencia
            return list(secuencia(str(ciclo_id)))
        except Exception:
            pass
        from modules.cache import leer
        return list(leer(ciclo_id=str(ciclo_id)))


def _resolver_cache(
    cache: Optional[CacheEvidencia] = None,
) -> CacheEvidencia:
    if cache is not None:
        return cache
    try:
        return _CachePublicoAdapter()
    except Exception:
        return _CacheMemoriaLocal()


# ===============================================================
# ERRORES / VEREDICTO / STATS
# ===============================================================

class CentinelaError(Exception):
    """Error de forma del centinela, no de negocio."""


@dataclass
class Veredicto:
    estado: str
    ciclo_id: str
    motivos: List[str] = field(default_factory=list)
    advertencias: List[str] = field(default_factory=list)
    tipo_auditoria: str = TIPO_AUDITORIA_OPERACIONAL
    id_verificacion: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
    hash_expediente: Optional[str] = None
    hash_flujo: Optional[str] = None
    hash_contratos: Optional[str] = None
    hash_reproducciones: Optional[str] = None
    meta_verificacion: Dict[str, Any] = field(default_factory=dict)
    valores_paquete: Dict[str, Any] = field(default_factory=dict)
    valores_evidencia: Dict[str, Any] = field(default_factory=dict)
    contratos: List[Dict[str, Any]] = field(default_factory=list)
    reproducciones: List[Dict[str, Any]] = field(default_factory=list)
    transiciones: List[Dict[str, Any]] = field(default_factory=list)
    arbol_auditoria: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def a_dict(self) -> Dict[str, Any]:
        return asdict(self)


class _Estadisticas:
    def __init__(self) -> None:
        self.verificaciones = 0
        self.aprobadas = 0
        self.retenidas = 0
        self.parciales = 0
        self.estructurales = 0
        self.sin_auditable = 0
        self.advertencias = 0
        self.duraciones_s: List[float] = []
        self.modulos_vistos: set = set()
        self.capacidades_vistas: set = set()

    def registrar(
        self,
        estado: str,
        duracion_s: float,
        modulos: List[str],
        capacidades: List[str],
        n_adv: int,
    ) -> None:
        self.verificaciones += 1
        if estado == CS_ESTADO_APROBADO:
            self.aprobadas += 1
        elif estado == CS_ESTADO_RETENIDO:
            self.retenidas += 1
        elif estado == CS_ESTADO_PARCIAL:
            self.parciales += 1
        elif estado == CS_ESTADO_SOLO_ESTRUCTURAL:
            self.estructurales += 1
        elif estado == CS_ESTADO_SIN_PAQUETE_AUDITABLE:
            self.sin_auditable += 1
        self.duraciones_s.append(duracion_s)
        self.modulos_vistos.update(modulos)
        self.capacidades_vistas.update(capacidades)
        self.advertencias += n_adv

    def resumen(self) -> Dict[str, Any]:
        n = len(self.duraciones_s)
        avg = sum(self.duraciones_s) / n if n else 0.0
        return {
            "verificaciones": self.verificaciones,
            "aprobadas": self.aprobadas,
            "retenidas": self.retenidas,
            "parciales": self.parciales,
            "estructurales": self.estructurales,
            "sin_auditable": self.sin_auditable,
            "advertencias": self.advertencias,
            "tiempo_promedio_s": round(avg, 6),
            "modulos_vistos": sorted(self.modulos_vistos),
            "capacidades_vistas": sorted(self.capacidades_vistas),
        }


_STATS = _Estadisticas()


# ===============================================================
# COMPARACIÓN / HASH
# ===============================================================

def _normalizar(x: Any) -> Any:
    if isinstance(x, Fraction):
        return str(x)
    if isinstance(x, float):
        raise CentinelaError("float rechazado en centinela")
    if isinstance(x, dict):
        return {
            str(k): _normalizar(v)
            for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))
        }
    if isinstance(x, (list, tuple)):
        return [_normalizar(v) for v in x]
    if isinstance(x, set):
        return sorted(_normalizar(v) for v in x)
    return x


def _igual(a: Any, b: Any) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if isinstance(a, (int, Fraction)) or isinstance(b, (int, Fraction)):
        try:
            fa = a if isinstance(a, Fraction) else (
                Fraction(a) if isinstance(a, int) else Fraction(str(a))
            )
            fb = b if isinstance(b, Fraction) else (
                Fraction(b) if isinstance(b, int) else Fraction(str(b))
            )
            return fa == fb
        except Exception:
            pass
    try:
        return _normalizar(a) == _normalizar(b)
    except CentinelaError:
        raise
    except Exception:
        return a == b


def _hash_obj(obj: Any) -> str:
    try:
        raw = json.dumps(
            _normalizar(obj), sort_keys=True, default=str, ensure_ascii=True
        )
    except Exception:
        raw = str(obj)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ===============================================================
# EXPEDIENTE
# ===============================================================

def _payload(ev: Dict[str, Any]) -> Dict[str, Any]:
    p = ev.get("payload")
    return p if isinstance(p, dict) else {}


def _descubrir_campo(
    eventos: List[Dict[str, Any]], campo: str
) -> List[str]:
    hallados: set = set()
    for ev in eventos:
        v = ev.get(campo)
        if v is not None and str(v).strip():
            hallados.add(str(v))
        p = _payload(ev)
        v2 = p.get(campo)
        if v2 is not None and str(v2).strip():
            hallados.add(str(v2))
    return sorted(hallados)


def _recolectar_hojas(
    obj: Any,
    destino: Dict[str, List[Any]],
    ruta: str = "",
) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            ks = str(k)
            if ks in _CLAVES_FORMA and not isinstance(v, (dict, list, tuple)):
                continue
            r = "{0}.{1}".format(ruta, ks) if ruta else ks
            if isinstance(v, (dict, list, tuple, set)):
                _recolectar_hojas(v, destino, r)
            else:
                if v is not None and ks not in _CLAVES_FORMA:
                    destino.setdefault(ks, []).append(v)
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj):
            _recolectar_hojas(item, destino, "{0}[{1}]".format(ruta, i))


def _valores_desde(obj: Any) -> Dict[str, List[Any]]:
    destino: Dict[str, List[Any]] = {}
    _recolectar_hojas(obj, destino)
    return destino


def _sin_contradiccion(valores: List[Any]) -> bool:
    if len(valores) <= 1:
        return True
    base = valores[0]
    return all(_igual(base, v) for v in valores)


def _ultimo(valores: List[Any]) -> Any:
    return valores[-1] if valores else None


# ===============================================================
# CLASIFICACIÓN PROVISIONAL (solo paquete)
# ===============================================================

def _tiene_hojas_dominio(paquete: Dict[str, Any]) -> bool:
    """ciclo_id solo NO basta; hace falta al menos una hoja comparable."""
    if not isinstance(paquete, dict) or not paquete:
        return False
    return len(_valores_desde(paquete)) > 0


def _clasificar_paquete(paquete: Dict[str, Any]) -> str:
    """
    Solo mira el paquete. No consulta CACHE.

    CLASE_SIN_PAQUETE          — vacío / no dict
    CLASE_ESTRUCTURAL          — sin hojas y sin ciclo_id
    CLASE_CANDIDATO_OPERACIONAL — hay hojas y/o ciclo_id
                                  (confirmación después de CACHE)
    """
    if not isinstance(paquete, dict) or not paquete:
        return CLASE_SIN_PAQUETE
    tiene_hojas = _tiene_hojas_dominio(paquete)
    tiene_ciclo = bool(paquete.get(PKG_CICLO_ID))
    if not tiene_hojas and not tiene_ciclo:
        return CLASE_ESTRUCTURAL
    return CLASE_CANDIDATO_OPERACIONAL


# ===============================================================
# CONTRATOS
# ===============================================================

def _parece_contrato(d: Dict[str, Any]) -> bool:
    if not isinstance(d, dict):
        return False
    tiene_id = any(k in d for k in ("id", "nombre", "rol"))
    tiene_caps = "capacidades" in d or "capacidades_meta" in d
    tiene_meta = any(
        k in d for k in ("esquema", "version_contrato", "version", "requiere")
    )
    return bool(tiene_id and (tiene_caps or tiene_meta))


def _extraer_contratos(
    eventos: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    contratos: List[Dict[str, Any]] = []
    vistos: Set[str] = set()

    def _add(cont: Dict[str, Any]) -> None:
        cid = str(
            cont.get("id")
            or cont.get("nombre")
            or cont.get("rol")
            or _hash_obj(cont)[:12]
        )
        if cid not in vistos:
            vistos.add(cid)
            contratos.append(dict(cont))

    for ev in eventos:
        for c in (ev, _payload(ev)):
            if not isinstance(c, dict):
                continue
            for key in ("contrato", "CONTENEDOR", "contenedor"):
                cont = c.get(key)
                if isinstance(cont, dict) and _parece_contrato(cont):
                    _add(cont)
            if _parece_contrato(c):
                _add(c)
    return contratos


def _caps_declaradas(contrato: Dict[str, Any]) -> Dict[str, Any]:
    caps = contrato.get("capacidades")
    if isinstance(caps, dict):
        return dict(caps)
    if isinstance(caps, (list, tuple, set)):
        return {str(x): True for x in caps}
    return {}


def _caps_obligatorias(contrato: Dict[str, Any]) -> Set[str]:
    out: Set[str] = set()
    meta = contrato.get("capacidades_meta")
    if isinstance(meta, dict):
        for nombre, info in meta.items():
            if isinstance(info, dict):
                if info.get("obligatoria") is True or info.get("required") is True:
                    out.add(str(nombre))
    oblig = contrato.get("capacidades_obligatorias")
    if isinstance(oblig, (list, tuple, set)):
        out |= {str(x) for x in oblig}
    return out


def _requiere(contrato: Dict[str, Any]) -> List[str]:
    req = contrato.get("requiere") or contrato.get("dependencias")
    if isinstance(req, list):
        return [str(x) for x in req]
    return []


def _autoriza_ejecutar(contrato: Dict[str, Any]) -> Optional[bool]:
    for key in ("autoriza_engine", "autorizacion", "permisos"):
        auth = contrato.get(key)
        if isinstance(auth, dict) and "ejecutar" in auth:
            return bool(auth.get("ejecutar"))
        if isinstance(auth, bool):
            return auth
    return None


# ===============================================================
# SECUENCIA / DEPENDENCIAS / DAG / REPRODUCCIÓN
# ===============================================================

def _ejecuciones_registradas(
    eventos: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for ev in eventos:
        p = _payload(ev)
        modulo = ev.get("modulo") or p.get("modulo")
        capacidad = ev.get("capacidad") or p.get("capacidad")
        if not modulo and not capacidad:
            continue
        deps = p.get("requiere") or p.get("dependencias") or p.get("deps")
        if not isinstance(deps, list):
            deps = []
        out.append({
            "seq": ev.get("seq"),
            "timestamp": ev.get("timestamp"),
            "tipo": ev.get("tipo"),
            "modulo": str(modulo) if modulo is not None else None,
            "capacidad": str(capacidad) if capacidad is not None else None,
            "estado": ev.get("estado") or p.get("estado"),
            "payload": p,
            "resultado": p.get("resultado"),
            "entrada": p.get("entrada") or p.get("args") or p.get("kwargs"),
            "contexto": p.get("contexto") or p.get("O_context") or p.get("context"),
            "estado_previo": p.get("estado_previo") or p.get("prev"),
            "requiere": [str(x) for x in deps],
            "version_modulo": p.get("version_modulo") or p.get("version"),
            "esquema": p.get("esquema"),
            "version_contrato": p.get("version_contrato"),
        })
    out.sort(
        key=lambda e: (
            e["seq"] is None,
            e["seq"] if isinstance(e["seq"], int) else 0,
        )
    )
    return out


def _verificar_secuencia(
    ejecuciones: List[Dict[str, Any]],
) -> List[str]:
    motivos: List[str] = []
    prev: Optional[int] = None
    for ej in ejecuciones:
        seq = ej.get("seq")
        if not isinstance(seq, int):
            continue
        if prev is not None and seq < prev:
            motivos.append(
                "orden causal inválido: seq {0} después de {1}".format(
                    seq, prev
                )
            )
        prev = seq
    return motivos


def _verificar_dependencias(
    ejecuciones: List[Dict[str, Any]],
    contratos: List[Dict[str, Any]],
    modulos_presentes: Set[str],
) -> List[str]:
    motivos: List[str] = []
    for cont in contratos:
        nombre = str(
            cont.get("nombre") or cont.get("id") or cont.get("rol") or ""
        )
        for dep in _requiere(cont):
            if dep not in modulos_presentes and dep != nombre:
                motivos.append(
                    "dependencia no satisfecha: {0} requiere {1}".format(
                        nombre or "?", dep
                    )
                )
    for ej in ejecuciones:
        for dep in ej.get("requiere") or []:
            if str(dep) not in modulos_presentes:
                motivos.append(
                    "dependencia de ejecución no satisfecha: "
                    "{0}.{1} requiere {2}".format(
                        ej.get("modulo"), ej.get("capacidad"), dep
                    )
                )
    return motivos


def _verificar_autorizaciones(
    ejecuciones: List[Dict[str, Any]],
    contratos: List[Dict[str, Any]],
) -> List[str]:
    motivos: List[str] = []
    if not contratos:
        return motivos
    indice: Dict[str, Dict[str, Any]] = {}
    for cont in contratos:
        for key in ("nombre", "id", "rol"):
            val = cont.get(key)
            if val is not None:
                indice[str(val)] = cont
    for ej in ejecuciones:
        mod = ej.get("modulo")
        cap = ej.get("capacidad")
        if not mod or not cap:
            continue
        cont = indice.get(str(mod))
        if cont is None:
            continue
        caps = set(_caps_declaradas(cont).keys())
        if caps and str(cap) not in caps:
            motivos.append(
                "capacidad no declarada en contrato: {0}.{1}".format(mod, cap)
            )
        auth = _autoriza_ejecutar(cont)
        if auth is False:
            motivos.append(
                "capacidad ejecutada sin autorización: {0}.{1}".format(mod, cap)
            )
    return motivos


def _verificar_versiones(
    eventos: List[Dict[str, Any]],
    contratos: List[Dict[str, Any]],
) -> Tuple[List[str], List[str]]:
    motivos: List[str] = []
    advertencias: List[str] = []
    esquemas: Set[str] = set()
    versiones: Set[str] = set()
    for cont in contratos:
        if cont.get("esquema"):
            esquemas.add(str(cont["esquema"]))
        vc = cont.get("version_contrato") or cont.get("version")
        if vc:
            versiones.add(str(vc))
    for ev in eventos:
        p = _payload(ev)
        if p.get("esquema"):
            esquemas.add(str(p["esquema"]))
        if p.get("version_contrato"):
            versiones.add(str(p["version_contrato"]))
    if len(esquemas) > 1:
        motivos.append(
            "esquemas inconsistentes: {0}".format(sorted(esquemas))
        )
    if len(versiones) > 1:
        advertencias.append(
            "versiones de contrato mixtas: {0}".format(sorted(versiones))
        )
    return motivos, advertencias


def _construir_dag(
    ejecuciones: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    nodos: List[Dict[str, Any]] = []
    for i, ej in enumerate(ejecuciones):
        nodos.append({
            "idx": i,
            "seq": ej.get("seq"),
            "modulo": ej.get("modulo"),
            "capacidad": ej.get("capacidad"),
            "estado": ej.get("estado"),
            "requiere": list(ej.get("requiere") or []),
            "edges_to": [],
        })
    by_mod: Dict[str, List[int]] = {}
    for i, n in enumerate(nodos):
        m = n.get("modulo")
        if m:
            by_mod.setdefault(str(m), []).append(i)
    for i, n in enumerate(nodos):
        for dep in n.get("requiere") or []:
            for j in by_mod.get(str(dep), []):
                if j != i:
                    n["edges_to"].append(j)
        if i + 1 < len(nodos) and not n.get("requiere"):
            n["edges_to"].append(i + 1)
    return nodos


def _transiciones(
    ejecuciones: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for ej in ejecuciones:
        out.append({
            "seq": ej.get("seq"),
            "modulo": ej.get("modulo"),
            "capacidad": ej.get("capacidad"),
            "estado_previo": ej.get("estado_previo"),
            "entrada": ej.get("entrada"),
            "contexto": ej.get("contexto"),
            "resultado": ej.get("resultado"),
            "estado": ej.get("estado"),
        })
    return out


def _reproducir(
    invocador: InvocadorCapacidades,
    ejecuciones: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[str]]:
    reproducciones: List[Dict[str, Any]] = []
    motivos: List[str] = []

    for ej in ejecuciones:
        mod = ej.get("modulo")
        cap = ej.get("capacidad")
        if not mod or not cap:
            continue

        entrada = ej.get("entrada")
        contexto = ej.get("contexto")
        estado_previo = ej.get("estado_previo")
        resultado_reg = ej.get("resultado")

        kwargs: Dict[str, Any] = {}
        args: List[Any] = []

        if isinstance(entrada, dict):
            kwargs.update(entrada)
        elif isinstance(entrada, (list, tuple)):
            args.extend(entrada)
        elif entrada is not None:
            args.append(entrada)

        if contexto is not None and "contexto" not in kwargs:
            kwargs["contexto"] = contexto
        if estado_previo is not None and "estado_previo" not in kwargs:
            kwargs["estado_previo"] = estado_previo

        try:
            if kwargs and args:
                resultado_nuevo = invocador.invocar(mod, cap, *args, **kwargs)
            elif kwargs:
                resultado_nuevo = invocador.invocar(mod, cap, **kwargs)
            elif args:
                resultado_nuevo = invocador.invocar(mod, cap, *args)
            else:
                resultado_nuevo = invocador.invocar(mod, cap)
        except Exception as e:
            motivos.append(
                "reproduccion {0}.{1}: {2}: {3}".format(
                    mod, cap, type(e).__name__, e
                )
            )
            reproducciones.append({
                "modulo": mod,
                "capacidad": cap,
                "estado": "ERROR",
                "error": "{0}: {1}".format(type(e).__name__, e),
            })
            continue

        coincide = True
        if resultado_reg is not None:
            coincide = _igual(resultado_reg, resultado_nuevo)
            if not coincide:
                motivos.append(
                    "reproduccion diverge {0}.{1}".format(mod, cap)
                )

        reproducciones.append({
            "modulo": mod,
            "capacidad": cap,
            "estado": "OK" if coincide else "DIVERGE",
            "resultado_registrado": resultado_reg,
            "resultado_reproducido": resultado_nuevo,
        })

    return reproducciones, motivos


def _paquete_minimo_ok(paquete: Dict[str, Any]) -> List[str]:
    faltas: List[str] = []
    if not isinstance(paquete, dict):
        return ["paquete no es dict"]
    if not paquete.get(PKG_CICLO_ID):
        faltas.append("falta ciclo_id")
    if PKG_O_CONTEXT not in paquete and PKG_CONTEXTO not in paquete:
        faltas.append("falta O_context/contexto en paquete")
    estado = str(paquete.get(PKG_ESTADO) or "").upper()
    if estado not in PKG_ESTADOS_VALIDOS:
        faltas.append("estado desconocido: {0}".format(estado))
    return faltas


# ===============================================================
# NÚCLEO
# ===============================================================

class Centinela:
    def __init__(
        self,
        cache: Optional[CacheEvidencia] = None,
        invocador: Optional[InvocadorCapacidades] = None,
    ) -> None:
        self._cache: CacheEvidencia = _resolver_cache(cache)
        self._invocador: Optional[InvocadorCapacidades] = invocador
        self._ultimo_veredicto: Optional[Veredicto] = None

    def entrar_modulo(self, *args: Any, **kwargs: Any) -> None:
        raise CentinelaError(
            "Centinela no tiene agencia para entrar en módulos"
        )

    def modificar_factores(self, *args: Any, **kwargs: Any) -> None:
        raise CentinelaError(
            "Centinela no modifica factores ni contexto"
        )

    def orquestar(self, *args: Any, **kwargs: Any) -> None:
        raise CentinelaError(
            "Centinela no orquesta; solo certifica la salida"
        )

    def verificar(
        self,
        paquete: Dict[str, Any],
        *,
        depositar_salida: bool = True,
    ) -> Veredicto:
        t0 = time.perf_counter()
        ts_inicio = datetime.now(timezone.utc).isoformat()
        id_ver = str(uuid.uuid4())
        motivos: List[str] = []
        advertencias: List[str] = []
        reproducciones: List[Dict[str, Any]] = []

        if not isinstance(paquete, dict):
            return self._emitir(
                estado=CS_ESTADO_SIN_PAQUETE_AUDITABLE,
                ciclo_id="sin_ciclo",
                motivos=["paquete no es dict"],
                advertencias=[],
                id_verificacion=id_ver,
                t0=t0,
                ts_inicio=ts_inicio,
                paquete={},
                tipo_auditoria=TIPO_AUDITORIA_ESTRUCTURAL,
            )

        p = copy.deepcopy(paquete)
        ciclo_id = str(p.get(PKG_CICLO_ID) or "")

        # ----------------------------------------------------------
        # 1) Clasificación provisional (solo paquete)
        # ----------------------------------------------------------
        clase = _clasificar_paquete(p)

        if clase == CLASE_SIN_PAQUETE:
            return self._emitir(
                estado=CS_ESTADO_SIN_PAQUETE_AUDITABLE,
                ciclo_id=ciclo_id or "sin_ciclo",
                motivos=[
                    "sin expediente auditable: paquete vacío o inexistente"
                ],
                advertencias=advertencias,
                id_verificacion=id_ver,
                t0=t0,
                ts_inicio=ts_inicio,
                paquete=p,
                tipo_auditoria=TIPO_AUDITORIA_ESTRUCTURAL,
            )

        if clase == CLASE_ESTRUCTURAL:
            return self._emitir(
                estado=CS_ESTADO_SOLO_ESTRUCTURAL,
                ciclo_id=ciclo_id or "estructural",
                motivos=[
                    "paquete estructural: sin hojas de dominio ni ciclo_id"
                ],
                advertencias=advertencias,
                id_verificacion=id_ver,
                t0=t0,
                ts_inicio=ts_inicio,
                paquete=p,
                tipo_auditoria=TIPO_AUDITORIA_ESTRUCTURAL,
            )

        # CLASE_CANDIDATO_OPERACIONAL — aún no confirmado
        if depositar_salida and ciclo_id:
            try:
                self._cache.guardar({
                    "tipo": EN_TIPO_CICLO_FIN,
                    PKG_CICLO_ID: ciclo_id,
                    "origen": EN_MODULO,
                    "modulo": EN_MODULO,
                    "categoria": EN_CATEGORIA_SALIDA,
                    EN_CAMPO_PAQUETE: p,
                })
            except Exception as e:
                advertencias.append(
                    "cache_salida: {0}: {1}".format(type(e).__name__, e)
                )

        faltas = _paquete_minimo_ok(p)
        if faltas:
            return self._emitir(
                estado=CS_ESTADO_RETENIDO,
                ciclo_id=ciclo_id or "sin_ciclo",
                motivos=[
                    "paquete_incompleto: {0}".format(f) for f in faltas
                ],
                advertencias=advertencias,
                id_verificacion=id_ver,
                t0=t0,
                ts_inicio=ts_inicio,
                paquete=p,
                tipo_auditoria=TIPO_AUDITORIA_OPERACIONAL,
            )

        estado_eng = str(p.get(PKG_ESTADO) or "").upper()
        vals_p_lists = _valores_desde(p)
        valores_p = {k: _ultimo(v) for k, v in vals_p_lists.items()}

        # ----------------------------------------------------------
        # 2) Consulta CACHE — confirma u descarta operacional
        # ----------------------------------------------------------
        try:
            eventos = self._cache.leer_ciclo(ciclo_id)
        except Exception as e:
            return self._emitir(
                estado=CS_ESTADO_RETENIDO,
                ciclo_id=ciclo_id,
                motivos=motivos + [
                    "cache_lectura: {0}: {1}".format(type(e).__name__, e)
                ],
                advertencias=advertencias,
                id_verificacion=id_ver,
                t0=t0,
                ts_inicio=ts_inicio,
                paquete=p,
                valores_paquete=dict(valores_p),
                tipo_auditoria=TIPO_AUDITORIA_OPERACIONAL,
            )

        modulos = _descubrir_campo(eventos, "modulo")
        capacidades = _descubrir_campo(eventos, "capacidad")
        tipos = _descubrir_campo(eventos, "tipo")
        categorias = _descubrir_campo(eventos, "categoria")
        hash_exp = _hash_obj(eventos)
        contratos = _extraer_contratos(eventos)
        hash_contratos = _hash_obj(contratos) if contratos else None
        ejecuciones = _ejecuciones_registradas(eventos)
        hash_flujo = _hash_obj(ejecuciones) if ejecuciones else None
        dag = _construir_dag(ejecuciones)
        trans = _transiciones(ejecuciones)
        modulos_set: Set[str] = set(modulos)
        vals_e_lists = _valores_desde(eventos)
        valores_e = {k: _ultimo(v) for k, v in vals_e_lists.items()}

        hay_evidencia_cache = bool(eventos) and (
            bool(vals_e_lists) or bool(ejecuciones) or bool(contratos)
        )
        hay_evidencia_paquete = bool(valores_p)

        meta_exp = {
            "ciclo_id": ciclo_id,
            "clase_provisional": CLASE_CANDIDATO_OPERACIONAL,
            "total_eventos": len(eventos),
            "modulos": modulos,
            "capacidades": capacidades,
            "tipos": tipos,
            "categorias": categorias,
            "contratos_n": len(contratos),
            "ejecuciones_n": len(ejecuciones),
            "hash_expediente": hash_exp,
            "hash_flujo": hash_flujo,
            "hash_contratos": hash_contratos,
            "hojas_en_paquete": sorted(valores_p.keys()),
            "hojas_en_cache": sorted(valores_e.keys()),
        }

        # Confirmación: sin evidencia en paquete ni en CACHE
        if not eventos:
            motivos.append("expediente vacío en CACHE")
            if estado_eng == PKG_ESTADO_OK:
                return self._emitir(
                    estado=CS_ESTADO_RETENIDO,
                    ciclo_id=ciclo_id,
                    motivos=motivos + [
                        "estado OK sin expediente en CACHE"
                    ],
                    advertencias=advertencias,
                    id_verificacion=id_ver,
                    t0=t0,
                    ts_inicio=ts_inicio,
                    paquete=p,
                    valores_paquete=dict(valores_p),
                    hash_expediente=hash_exp,
                    meta_extra=meta_exp,
                    modulos=modulos,
                    capacidades=capacidades,
                    contratos=contratos,
                    arbol_auditoria=dag,
                    transiciones=trans,
                    tipo_auditoria=TIPO_AUDITORIA_OPERACIONAL,
                )
            if not hay_evidencia_paquete:
                return self._emitir(
                    estado=CS_ESTADO_SOLO_ESTRUCTURAL,
                    ciclo_id=ciclo_id,
                    motivos=motivos + [
                        "candidato operacional sin hojas en paquete "
                        "ni expediente en CACHE"
                    ],
                    advertencias=advertencias,
                    id_verificacion=id_ver,
                    t0=t0,
                    ts_inicio=ts_inicio,
                    paquete=p,
                    hash_expediente=hash_exp,
                    meta_extra=meta_exp,
                    tipo_auditoria=TIPO_AUDITORIA_ESTRUCTURAL,
                )

        if not hay_evidencia_cache and not hay_evidencia_paquete:
            return self._emitir(
                estado=CS_ESTADO_SOLO_ESTRUCTURAL,
                ciclo_id=ciclo_id,
                motivos=[
                    "candidato operacional sin evidencia confirmada "
                    "en paquete ni en CACHE"
                ],
                advertencias=advertencias,
                id_verificacion=id_ver,
                t0=t0,
                ts_inicio=ts_inicio,
                paquete=p,
                hash_expediente=hash_exp,
                meta_extra=meta_exp,
                tipo_auditoria=TIPO_AUDITORIA_ESTRUCTURAL,
            )

        # ----------------------------------------------------------
        # 3) Auditoría operacional confirmada
        # ----------------------------------------------------------
        for clave, lista in vals_e_lists.items():
            if not _sin_contradiccion(lista):
                motivos.append(
                    "evidencia contradictoria en '{0}'".format(clave)
                )
        if any(
            not _sin_contradiccion(lista)
            for lista in vals_e_lists.values()
        ):
            return self._emitir(
                estado=CS_ESTADO_RETENIDO,
                ciclo_id=ciclo_id,
                motivos=motivos,
                advertencias=advertencias,
                id_verificacion=id_ver,
                t0=t0,
                ts_inicio=ts_inicio,
                paquete=p,
                valores_paquete=dict(valores_p),
                valores_evidencia=dict(valores_e),
                hash_expediente=hash_exp,
                hash_flujo=hash_flujo,
                hash_contratos=hash_contratos,
                meta_extra=meta_exp,
                modulos=modulos,
                capacidades=capacidades,
                contratos=contratos,
                arbol_auditoria=dag,
                transiciones=trans,
                tipo_auditoria=TIPO_AUDITORIA_OPERACIONAL,
            )

        for clave in sorted(set(valores_p) & set(valores_e)):
            if not _igual(valores_p[clave], valores_e[clave]):
                motivos.append(
                    "divergencia '{0}': paquete≠evidencia".format(clave)
                )
        if motivos:
            return self._emitir(
                estado=CS_ESTADO_RETENIDO,
                ciclo_id=ciclo_id,
                motivos=motivos,
                advertencias=advertencias,
                id_verificacion=id_ver,
                t0=t0,
                ts_inicio=ts_inicio,
                paquete=p,
                valores_paquete=dict(valores_p),
                valores_evidencia=dict(valores_e),
                hash_expediente=hash_exp,
                hash_flujo=hash_flujo,
                hash_contratos=hash_contratos,
                meta_extra=meta_exp,
                modulos=modulos,
                capacidades=capacidades,
                contratos=contratos,
                arbol_auditoria=dag,
                transiciones=trans,
                tipo_auditoria=TIPO_AUDITORIA_OPERACIONAL,
            )

        motivos.extend(_verificar_secuencia(ejecuciones))
        motivos.extend(
            _verificar_dependencias(ejecuciones, contratos, modulos_set)
        )
        motivos.extend(_verificar_autorizaciones(ejecuciones, contratos))
        m_ver, a_ver = _verificar_versiones(eventos, contratos)
        motivos.extend(m_ver)
        advertencias.extend(a_ver)

        if motivos:
            return self._emitir(
                estado=CS_ESTADO_RETENIDO,
                ciclo_id=ciclo_id,
                motivos=motivos,
                advertencias=advertencias,
                id_verificacion=id_ver,
                t0=t0,
                ts_inicio=ts_inicio,
                paquete=p,
                valores_paquete=dict(valores_p),
                valores_evidencia=dict(valores_e),
                hash_expediente=hash_exp,
                hash_flujo=hash_flujo,
                hash_contratos=hash_contratos,
                meta_extra=meta_exp,
                modulos=modulos,
                capacidades=capacidades,
                contratos=contratos,
                arbol_auditoria=dag,
                transiciones=trans,
                tipo_auditoria=TIPO_AUDITORIA_OPERACIONAL,
            )

        hash_repro = None
        if self._invocador is not None and ejecuciones:
            reproducciones, m_repro = _reproducir(
                self._invocador, ejecuciones
            )
            motivos.extend(m_repro)
            hash_repro = _hash_obj(reproducciones)
            if any(
                r.get("estado") in ("ERROR", "DIVERGE")
                for r in reproducciones
            ):
                return self._emitir(
                    estado=CS_ESTADO_RETENIDO,
                    ciclo_id=ciclo_id,
                    motivos=motivos,
                    advertencias=advertencias,
                    id_verificacion=id_ver,
                    t0=t0,
                    ts_inicio=ts_inicio,
                    paquete=p,
                    valores_paquete=dict(valores_p),
                    valores_evidencia=dict(valores_e),
                    reproducciones=reproducciones,
                    hash_expediente=hash_exp,
                    hash_flujo=hash_flujo,
                    hash_contratos=hash_contratos,
                    hash_reproducciones=hash_repro,
                    meta_extra=meta_exp,
                    modulos=modulos,
                    capacidades=capacidades,
                    contratos=contratos,
                    arbol_auditoria=dag,
                    transiciones=trans,
                    tipo_auditoria=TIPO_AUDITORIA_OPERACIONAL,
                )
        elif ejecuciones and self._invocador is None:
            advertencias.append(
                "invocador no disponible; verificación por expediente"
            )

        if contratos:
            caps_ejecutadas = {
                str(e.get("capacidad"))
                for e in ejecuciones
                if e.get("capacidad")
            }
            for cont in contratos:
                nombre = str(
                    cont.get("nombre")
                    or cont.get("id")
                    or cont.get("rol")
                    or "?"
                )
                oblig = _caps_obligatorias(cont)
                faltan_oblig = oblig - caps_ejecutadas
                if faltan_oblig:
                    motivos.append(
                        "capacidades obligatorias no ejercidas en {0}: {1}".format(
                            nombre, sorted(faltan_oblig)
                        )
                    )
                declaradas = set(_caps_declaradas(cont).keys())
                no_usadas = declaradas - caps_ejecutadas - oblig
                if no_usadas:
                    advertencias.append(
                        "contrato {0}: capacidades opcionales no ejercidas: {1}".format(
                            nombre, sorted(no_usadas)
                        )
                    )
            if motivos:
                return self._emitir(
                    estado=CS_ESTADO_RETENIDO,
                    ciclo_id=ciclo_id,
                    motivos=motivos,
                    advertencias=advertencias,
                    id_verificacion=id_ver,
                    t0=t0,
                    ts_inicio=ts_inicio,
                    paquete=p,
                    valores_paquete=dict(valores_p),
                    valores_evidencia=dict(valores_e),
                    reproducciones=reproducciones,
                    hash_expediente=hash_exp,
                    hash_flujo=hash_flujo,
                    hash_contratos=hash_contratos,
                    hash_reproducciones=hash_repro,
                    meta_extra=meta_exp,
                    modulos=modulos,
                    capacidades=capacidades,
                    contratos=contratos,
                    arbol_auditoria=dag,
                    transiciones=trans,
                    tipo_auditoria=TIPO_AUDITORIA_OPERACIONAL,
                )

        if estado_eng in (PKG_ESTADO_UNDEFINED, PKG_ESTADO_PARCIAL):
            return self._emitir(
                estado=CS_ESTADO_PARCIAL,
                ciclo_id=ciclo_id,
                motivos=motivos + [
                    "estado de paquete no-OK: {0}".format(estado_eng)
                ],
                advertencias=advertencias,
                id_verificacion=id_ver,
                t0=t0,
                ts_inicio=ts_inicio,
                paquete=p,
                valores_paquete=dict(valores_p),
                valores_evidencia=dict(valores_e),
                reproducciones=reproducciones,
                hash_expediente=hash_exp,
                hash_flujo=hash_flujo,
                hash_contratos=hash_contratos,
                hash_reproducciones=hash_repro,
                meta_extra=meta_exp,
                modulos=modulos,
                capacidades=capacidades,
                contratos=contratos,
                arbol_auditoria=dag,
                transiciones=trans,
                tipo_auditoria=TIPO_AUDITORIA_OPERACIONAL,
            )

        return self._emitir(
            estado=CS_ESTADO_APROBADO,
            ciclo_id=ciclo_id,
            motivos=motivos or [
                "expediente coherente; proceso auditado; paquete respaldado"
            ],
            advertencias=advertencias,
            id_verificacion=id_ver,
            t0=t0,
            ts_inicio=ts_inicio,
            paquete=p,
            valores_paquete=dict(valores_p),
            valores_evidencia=dict(valores_e),
            reproducciones=reproducciones,
            hash_expediente=hash_exp,
            hash_flujo=hash_flujo,
            hash_contratos=hash_contratos,
            hash_reproducciones=hash_repro,
            meta_extra=meta_exp,
            modulos=modulos,
            capacidades=capacidades,
            contratos=contratos,
            arbol_auditoria=dag,
            transiciones=trans,
            tipo_auditoria=TIPO_AUDITORIA_OPERACIONAL,
        )

    def _emitir(
        self,
        *,
        estado: str,
        ciclo_id: str,
        motivos: List[str],
        advertencias: List[str],
        id_verificacion: str,
        t0: float,
        ts_inicio: str,
        paquete: Dict[str, Any],
        valores_paquete: Optional[Dict[str, Any]] = None,
        valores_evidencia: Optional[Dict[str, Any]] = None,
        reproducciones: Optional[List[Dict[str, Any]]] = None,
        hash_expediente: Optional[str] = None,
        hash_flujo: Optional[str] = None,
        hash_contratos: Optional[str] = None,
        hash_reproducciones: Optional[str] = None,
        meta_extra: Optional[Dict[str, Any]] = None,
        modulos: Optional[List[str]] = None,
        capacidades: Optional[List[str]] = None,
        contratos: Optional[List[Dict[str, Any]]] = None,
        arbol_auditoria: Optional[List[Dict[str, Any]]] = None,
        transiciones: Optional[List[Dict[str, Any]]] = None,
        tipo_auditoria: str = TIPO_AUDITORIA_OPERACIONAL,
    ) -> Veredicto:
        ts_fin = datetime.now(timezone.utc).isoformat()
        duracion = round(time.perf_counter() - t0, 6)
        mods = list(modulos or [])
        caps = list(capacidades or [])
        conts = list(contratos or [])
        arbol = list(arbol_auditoria or [])
        trans = list(transiciones or [])
        repro = list(reproducciones or [])

        meta = {
            "id_verificacion": id_verificacion,
            "version_centinela": CS_VERSION,
            "version_contrato": CS_VERSION_CONTRATO,
            "esquema": CS_ESQUEMA,
            "version_eventos_cs": CS_VERSION_EVENTOS,
            "tipo_auditoria": tipo_auditoria,
            "modulos_en_expediente": mods,
            "capacidades_en_expediente": caps,
            "contratos_n": len(conts),
            "timestamp_inicio": ts_inicio,
            "timestamp_fin": ts_fin,
            "duracion_s": duracion,
            "hash_expediente": hash_expediente,
            "hash_flujo": hash_flujo,
            "hash_contratos": hash_contratos,
            "hash_reproducciones": hash_reproducciones,
            "invocador_disponible": self._invocador is not None,
        }
        if meta_extra:
            meta["expediente"] = meta_extra

        v = Veredicto(
            estado=estado,
            ciclo_id=ciclo_id,
            motivos=list(motivos),
            advertencias=list(advertencias),
            tipo_auditoria=tipo_auditoria,
            id_verificacion=id_verificacion,
            hash_expediente=hash_expediente,
            hash_flujo=hash_flujo,
            hash_contratos=hash_contratos,
            hash_reproducciones=hash_reproducciones,
            meta_verificacion=meta,
            valores_paquete=dict(valores_paquete or {}),
            valores_evidencia=dict(valores_evidencia or {}),
            contratos=conts,
            reproducciones=repro,
            transiciones=trans,
            arbol_auditoria=arbol,
            timestamp=ts_fin,
        )
        self._depositar_veredicto(v, paquete)
        self._ultimo_veredicto = v
        _STATS.registrar(estado, duracion, mods, caps, len(advertencias))
        return v

    def _depositar_veredicto(
        self, v: Veredicto, paquete: Dict[str, Any]
    ) -> None:
        try:
            self._cache.guardar({
                "tipo": CS_TIPO_VEREDICTO,
                PKG_CICLO_ID: v.ciclo_id,
                "origen": CS_MODULO,
                "modulo": CS_MODULO,
                "categoria": CS_CATEGORIA_VEREDICTO,
                "estado": v.estado,
                CS_CAMPO_VEREDICTO: v.a_dict(),
                CS_CAMPO_CICLO_ID: v.ciclo_id,
                CS_CAMPO_ESTADO: v.estado,
                CS_CAMPO_MOTIVOS: list(v.motivos),
                CS_CAMPO_PAQUETE_REF: {
                    PKG_ESTADO: paquete.get(PKG_ESTADO),
                    PKG_O_CONTEXT: paquete.get(
                        PKG_O_CONTEXT, paquete.get(PKG_CONTEXTO)
                    ),
                },
            })
        except Exception:
            pass

    def estado(self) -> Dict[str, Any]:
        return {
            "id": CS_ID,
            "nombre": CS_NOMBRE,
            "rol": CS_ROL,
            "version": CS_VERSION,
            "esquema": CS_ESQUEMA,
            "operativo": True,
        }

    def salud(self) -> Dict[str, Any]:
        s = _STATS.resumen()
        return {
            "id": CS_ID,
            "coherente": True,
            "verificaciones": s["verificaciones"],
            "aprobadas": s["aprobadas"],
            "retenidas": s["retenidas"],
            "parciales": s["parciales"],
            "estructurales": s["estructurales"],
            "sin_auditable": s["sin_auditable"],
        }

    def inventario(self) -> Dict[str, Any]:
        return {
            "id": CS_ID,
            "nombre": CS_NOMBRE,
            "rol": CS_ROL,
            "version": CS_VERSION,
            "funcion": CS_FUNCION,
            "no_hace": list(CS_NO_HACE),
            "autoridad": list(CS_AUTORIDAD),
            "capacidades": [
                "verificar", "reporte", "inventario",
                "diagnostico", "estado", "salud", "estadisticas",
            ],
        }

    def reporte(self) -> Dict[str, Any]:
        return {
            "id": CS_ID,
            "nombre": CS_NOMBRE,
            "version": CS_VERSION,
            "estado": self.estado(),
            "salud": self.salud(),
            "estadisticas": _STATS.resumen(),
            "ultimo_veredicto": (
                self._ultimo_veredicto.a_dict()
                if self._ultimo_veredicto
                else None
            ),
        }

    def diagnostico(self) -> Dict[str, Any]:
        s = _STATS.resumen()
        advertencias: List[str] = []
        if s["retenidas"] > 0:
            advertencias.append(
                "ciclos retenidos: {0}".format(s["retenidas"])
            )
        return {
            "id": CS_ID,
            "estado": "OPERATIVO",
            "problemas": [],
            "advertencias": advertencias,
            "estadisticas": s,
        }

    def estadisticas(self) -> Dict[str, Any]:
        return _STATS.resumen()


def verificar_salida_paquete(
    paquete: Dict[str, Any],
    cache: Optional[CacheEvidencia] = None,
    invocador: Optional[InvocadorCapacidades] = None,
) -> Veredicto:
    return Centinela(cache=cache, invocador=invocador).verificar(paquete)


def verificar_salida(salida: Any) -> bool:
    if not isinstance(salida, dict):
        return False
    if PKG_ESTADO in salida and salida[PKG_ESTADO] in CS_ESTADOS:
        return salida[PKG_ESTADO] == CS_ESTADO_APROBADO
    return False


__all__ = [
    "Centinela",
    "Veredicto",
    "CentinelaError",
    "CacheEvidencia",
    "InvocadorCapacidades",
    "CS_ID",
    "CS_NOMBRE",
    "CS_ROL",
    "CS_VERSION",
    "CS_ESTADO_APROBADO",
    "CS_ESTADO_RETENIDO",
    "CS_ESTADO_PARCIAL",
    "CS_ESTADO_SOLO_ESTRUCTURAL",
    "CS_ESTADO_SIN_PAQUETE_AUDITABLE",
    "CS_ESTADOS",
    "CLASE_SIN_PAQUETE",
    "CLASE_ESTRUCTURAL",
    "CLASE_CANDIDATO_OPERACIONAL",
    "TIPO_AUDITORIA_ESTRUCTURAL",
    "TIPO_AUDITORIA_OPERACIONAL",
    "verificar_salida_paquete",
    "verificar_salida",
]

# ===============================================================
# FIN DEL ARCHIVO
# ===============================================================
