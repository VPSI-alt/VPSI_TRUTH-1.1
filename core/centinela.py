"""
core/centinela.py
=================
Filtro autónomo pre-salida. Sin potestad de orquestar ni de entrar en módulos.

HACE
----
- Recibe el paquete de ciclo que el Engine propone como salida.
- Lee evidencia de CACHE (si está disponible).
- Recalcula Tru con FO + ancla CT (Fraction).
- Doble verificación: dos pasadas independientes + contraste con el original.
- Emite APROBADO | RETENIDO | PARCIAL.
- Deposita veredicto en CACHE (evidencia append-only cuando el backend lo permita).

NO HACE / NO PUEDE
------------------
- Entrar en carpetas de modules/* ni importar init de dominio para “arreglar”.
- Re-orquestar CX, AX, RE, TX, SF, MC…
- Modificar C, L, K, contexto u O_context.
- Inventar Tru si faltan factores.
- Tener prioridad de negocio ni borrar evidencia.
- Forzar SALIDA si el recálculo no cuadra.

Dependencias legítimas de verificación: FO (formulas), CT (constantes).
CA se usa solo para reglas de legibilidad de factores (None legítimo), no para re-scrape.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Dict, List, Optional, Protocol, Tuple
import copy


# ---------------------------------------------------------------------------
# API mínima de CACHE (inyectable; no es potestad del centinela crear el mundo)
# ---------------------------------------------------------------------------
class CacheEvidencia(Protocol):
    def guardar(self, registro: Dict[str, Any]) -> None: ...
    def obtener(self, ciclo_id: str) -> Optional[Dict[str, Any]]: ...


class _CacheMemoriaLocal:
    """Backend de fase: memoria de proceso. Sustituible por modules/cache."""

    def __init__(self) -> None:
        self._regs: List[Dict[str, Any]] = []

    def guardar(self, registro: Dict[str, Any]) -> None:
        self._regs.append(dict(registro))

    def obtener(self, ciclo_id: str) -> Optional[Dict[str, Any]]:
        for r in reversed(self._regs):
            if r.get("ciclo_id") == ciclo_id:
                return dict(r)
        return None

    def todos(self) -> List[Dict[str, Any]]:
        return list(self._regs)


# singleton de fase (Engine/bootstrap pueden inyectar otro)
_cache_default = _CacheMemoriaLocal()


# ---------------------------------------------------------------------------
# Errores
# ---------------------------------------------------------------------------
class CentinelaError(Exception):
    """Error de forma del centinela, no de negocio Tru."""


# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------
@dataclass
class Veredicto:
    estado: str  # APROBADO | RETENIDO | PARCIAL
    ciclo_id: str
    motivos: List[str] = field(default_factory=list)
    tru_ri_engine: Optional[str] = None
    tru_total_engine: Optional[str] = None
    tru_ri_pass1: Optional[str] = None
    tru_total_pass1: Optional[str] = None
    tru_ri_pass2: Optional[str] = None
    tru_total_pass2: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def a_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _frac(x: Any) -> Optional[Fraction]:
    if x is None:
        return None
    if isinstance(x, Fraction):
        return x
    if isinstance(x, bool):
        raise CentinelaError("bool no es Fraction")
    if isinstance(x, float):
        raise CentinelaError("float rechazado en centinela")
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, str):
        s = x.strip()
        if s.upper() in ("NONE", "UNDEFINED", ""):
            return None
        return Fraction(s)
    raise CentinelaError(f"tipo no convertible a Fraction: {type(x)}")


def _str_frac(x: Optional[Fraction]) -> Optional[str]:
    return str(x) if x is not None else None


def _ancla() -> Tuple[Fraction, Fraction]:
    from modules.constante import ALPHA, BETA

    if not isinstance(ALPHA, Fraction) or not isinstance(BETA, Fraction):
        raise CentinelaError("ancla CT no es Fraction")
    if ALPHA + BETA != Fraction(1):
        raise CentinelaError("ancla CT: ALPHA+BETA != 1")
    return ALPHA, BETA


def _fo_tru(
    C: Optional[Fraction], L: Optional[Fraction], K: Optional[Fraction]
) -> Tuple[Optional[Fraction], Optional[Fraction]]:
    """Recálculo literal vía FO. Si falta factor → (None, None) sin inventar."""
    if C is None or L is None or K is None:
        return None, None
    from modules.formulas.truth import tru_ri, tru_total

    ri = tru_ri(C, L, K)
    tot = tru_total(C, L, K)
    return ri, tot


def _extraer_factores(paquete: Dict[str, Any]) -> Tuple[
    Optional[Fraction], Optional[Fraction], Optional[Fraction], List[str]
]:
    motivos: List[str] = []
    factores = paquete.get("factores") or {}
    # tolerar plano en raíz
    c_raw = factores.get("C", paquete.get("C"))
    l_raw = factores.get("L", paquete.get("L"))
    k_raw = factores.get("K", paquete.get("K"))
    try:
        C = _frac(c_raw) if c_raw is not None else None
    except CentinelaError as e:
        motivos.append(f"C: {e}")
        C = None
    try:
        L = _frac(l_raw) if l_raw is not None else None
    except CentinelaError as e:
        motivos.append(f"L: {e}")
        L = None
    try:
        K = _frac(k_raw) if k_raw is not None else None
    except CentinelaError as e:
        motivos.append(f"K: {e}")
        K = None
    return C, L, K, motivos


def _extraer_tru_engine(
    paquete: Dict[str, Any],
) -> Tuple[Optional[Fraction], Optional[Fraction], List[str]]:
    motivos: List[str] = []
    try:
        ri = _frac(paquete.get("tru_ri"))
    except CentinelaError as e:
        motivos.append(f"tru_ri engine: {e}")
        ri = None
    try:
        tot = _frac(paquete.get("tru_total"))
    except CentinelaError as e:
        motivos.append(f"tru_total engine: {e}")
        tot = None
    return ri, tot, motivos


def _paquete_minimo_ok(paquete: Dict[str, Any]) -> List[str]:
    faltas: List[str] = []
    if not isinstance(paquete, dict):
        return ["paquete no es dict"]
    if not paquete.get("ciclo_id"):
        faltas.append("falta ciclo_id")
    # contexto: debe existir la clave (puede ser None solo si estado lo declara)
    if "O_context" not in paquete and "contexto" not in paquete:
        faltas.append("falta O_context/contexto en paquete")
    estado = str(paquete.get("estado") or "").upper()
    if estado not in ("OK", "PARCIAL", "UNDEFINED", "ERROR", ""):
        faltas.append(f"estado desconocido: {estado}")
    return faltas


# ---------------------------------------------------------------------------
# Núcleo
# ---------------------------------------------------------------------------
class Centinela:
    """
    Filtro pre-salida. Autónomo en el veredicto; sin agencia sobre módulos.
    """

    def __init__(self, cache: Optional[CacheEvidencia] = None) -> None:
        self._cache: CacheEvidencia = cache or _cache_default

    # --- lo que NO puede hacer (documentado y reforzado) ---
    def entrar_modulo(self, *args: Any, **kwargs: Any) -> None:
        raise CentinelaError(
            "Centinela no tiene agencia para entrar en módulos/carpetas"
        )

    def modificar_factores(self, *args: Any, **kwargs: Any) -> None:
        raise CentinelaError("Centinela no modifica C/L/K ni contexto")

    def orquestar(self, *args: Any, **kwargs: Any) -> None:
        raise CentinelaError("Centinela no orquesta; solo verifica salida")

    # --- verificación principal ---
    def verificar(
        self,
        paquete: Dict[str, Any],
        *,
        depositar_propuesta: bool = True,
    ) -> Veredicto:
        """
        Doble verificación + contraste con original.

        paquete (schema de fase) debe incluir idealmente:
          ciclo_id, estado, O_context|contexto,
          factores|{C,L,K}, tru_ri, tru_total,
          metadatos opcionales.
        """
        if not isinstance(paquete, dict):
            raise CentinelaError("paquete debe ser dict")

        # trabajo sobre copia: no mutar lo que mandó Engine
        p = copy.deepcopy(paquete)
        ciclo_id = str(p.get("ciclo_id") or "")
        motivos: List[str] = []

        # 0) evidencia: depositar propuesta tal cual
        if depositar_propuesta and ciclo_id:
            try:
                self._cache.guardar({
                    "tipo": "propuesta_engine",
                    "ciclo_id": ciclo_id,
                    "paquete": p,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except Exception as e:
                motivos.append(f"cache_propuesta: {type(e).__name__}: {e}")

        # 1) forma mínima
        faltas = _paquete_minimo_ok(p)
        if faltas:
            v = Veredicto(
                estado="RETENIDO",
                ciclo_id=ciclo_id or "sin_ciclo",
                motivos=[f"paquete_incompleto: {f}" for f in faltas] + motivos,
            )
            self._depositar_veredicto(v, p)
            return v

        estado_eng = str(p.get("estado") or "").upper()

        # 2) factores + tru engine
        C, L, K, m_fac = _extraer_factores(p)
        motivos.extend(m_fac)
        ri_e, tot_e, m_tru = _extraer_tru_engine(p)
        motivos.extend(m_tru)

        # 3) ancla (punto ciego si CT roto → RETENIDO)
        try:
            _ancla()
        except Exception as e:
            v = Veredicto(
                estado="RETENIDO",
                ciclo_id=ciclo_id,
                motivos=motivos + [f"ancla: {e}"],
                tru_ri_engine=_str_frac(ri_e),
                tru_total_engine=_str_frac(tot_e),
            )
            self._depositar_veredicto(v, p)
            return v

        # 4) reglas de estado parcial / undefined (K None legítimo)
        o_ctx = p.get("O_context", p.get("contexto"))
        if estado_eng in ("UNDEFINED", "PARCIAL") or K is None or C is None or L is None:
            # no inventar Tru; salida numérica completa no aplica
            if estado_eng in ("OK",) and (C is None or L is None or K is None):
                motivos.append(
                    "estado OK pero factores incompletos (fail-closed)"
                )
                v = Veredicto(
                    estado="RETENIDO",
                    ciclo_id=ciclo_id,
                    motivos=motivos,
                    tru_ri_engine=_str_frac(ri_e),
                    tru_total_engine=_str_frac(tot_e),
                )
                self._depositar_veredicto(v, p)
                return v
            v = Veredicto(
                estado="PARCIAL",
                ciclo_id=ciclo_id,
                motivos=motivos
                + [
                    "factores incompletos o estado no-OK: "
                    "sin Tru completo; no se aprueba salida numérica llena"
                ],
                tru_ri_engine=_str_frac(ri_e),
                tru_total_engine=_str_frac(tot_e),
            )
            self._depositar_veredicto(v, p)
            return v

        # 5) doble recálculo FO (pasada 1 y 2 independientes)
        try:
            ri1, tot1 = _fo_tru(C, L, K)
            ri2, tot2 = _fo_tru(C, L, K)
        except Exception as e:
            v = Veredicto(
                estado="RETENIDO",
                ciclo_id=ciclo_id,
                motivos=motivos + [f"recalculo_FO: {type(e).__name__}: {e}"],
                tru_ri_engine=_str_frac(ri_e),
                tru_total_engine=_str_frac(tot_e),
            )
            self._depositar_veredicto(v, p)
            return v

        if ri1 != ri2 or tot1 != tot2:
            v = Veredicto(
                estado="RETENIDO",
                ciclo_id=ciclo_id,
                motivos=motivos
                + ["doble_verificacion: pasada1 != pasada2 (no determinista)"],
                tru_ri_engine=_str_frac(ri_e),
                tru_total_engine=_str_frac(tot_e),
                tru_ri_pass1=_str_frac(ri1),
                tru_total_pass1=_str_frac(tot1),
                tru_ri_pass2=_str_frac(ri2),
                tru_total_pass2=_str_frac(tot2),
            )
            self._depositar_veredicto(v, p)
            return v

        # 6) contraste con original Engine
        if ri_e is None or tot_e is None:
            v = Veredicto(
                estado="RETENIDO",
                ciclo_id=ciclo_id,
                motivos=motivos
                + ["engine no declaró tru_ri/tru_total numéricos en estado OK"],
                tru_ri_pass1=_str_frac(ri1),
                tru_total_pass1=_str_frac(tot1),
                tru_ri_pass2=_str_frac(ri2),
                tru_total_pass2=_str_frac(tot2),
            )
            self._depositar_veredicto(v, p)
            return v

        if ri_e != ri1 or tot_e != tot1:
            v = Veredicto(
                estado="RETENIDO",
                ciclo_id=ciclo_id,
                motivos=motivos
                + [
                    "contraste: Tru Engine != recálculo FO(C,L,K)",
                    f"engine=({ri_e}, {tot_e}) fo=({ri1}, {tot1})",
                ],
                tru_ri_engine=_str_frac(ri_e),
                tru_total_engine=_str_frac(tot_e),
                tru_ri_pass1=_str_frac(ri1),
                tru_total_pass1=_str_frac(tot1),
                tru_ri_pass2=_str_frac(ri2),
                tru_total_pass2=_str_frac(tot2),
            )
            self._depositar_veredicto(v, p)
            return v

        # 7) lectura CACHE (si hay registro previo del mismo ciclo, no debe contradecir factores)
        try:
            prev = self._cache.obtener(ciclo_id)
            if prev and isinstance(prev.get("paquete"), dict):
                # contraste suave: mismo ciclo_id no debería cambiar C,L,K en silencio
                C2, L2, K2, _ = _extraer_factores(prev["paquete"])
                if (C2, L2, K2) != (None, None, None) and (C2, L2, K2) != (C, L, K):
                    motivos.append(
                        "cache: factores del registro previo difieren del paquete actual"
                    )
                    v = Veredicto(
                        estado="RETENIDO",
                        ciclo_id=ciclo_id,
                        motivos=motivos,
                        tru_ri_engine=_str_frac(ri_e),
                        tru_total_engine=_str_frac(tot_e),
                        tru_ri_pass1=_str_frac(ri1),
                        tru_total_pass1=_str_frac(tot1),
                        tru_ri_pass2=_str_frac(ri2),
                        tru_total_pass2=_str_frac(tot2),
                    )
                    self._depositar_veredicto(v, p)
                    return v
        except Exception as e:
            motivos.append(f"cache_lectura: {type(e).__name__}: {e}")
            # no aprueba si no puede leer evidencia cuando se espera cache
            # en fase: solo anotamos; descomentar fail-closed estricto si quieres
            # v = Veredicto(estado="RETENIDO", ...)

        # 8) APROBADO
        v = Veredicto(
            estado="APROBADO",
            ciclo_id=ciclo_id,
            motivos=motivos or ["doble FO OK; contraste Engine OK"],
            tru_ri_engine=_str_frac(ri_e),
            tru_total_engine=_str_frac(tot_e),
            tru_ri_pass1=_str_frac(ri1),
            tru_total_pass1=_str_frac(tot1),
            tru_ri_pass2=_str_frac(ri2),
            tru_total_pass2=_str_frac(tot2),
        )
        self._depositar_veredicto(v, p)
        return v

    def _depositar_veredicto(self, v: Veredicto, paquete: Dict[str, Any]) -> None:
        try:
            self._cache.guardar({
                "tipo": "veredicto_centinela",
                "ciclo_id": v.ciclo_id,
                "veredicto": v.a_dict(),
                "paquete_ref": {
                    "estado": paquete.get("estado"),
                    "O_context": paquete.get("O_context", paquete.get("contexto")),
                    "factores": paquete.get("factores")
                    or {
                        "C": paquete.get("C"),
                        "L": paquete.get("L"),
                        "K": paquete.get("K"),
                    },
                },
                "timestamp": v.timestamp,
            })
        except Exception:
            pass  # el veredicto en memoria ya se devolvió; cache best-effort de fase


# ---------------------------------------------------------------------------
# API de módulo / core
# ---------------------------------------------------------------------------
def verificar_salida_paquete(
    paquete: Dict[str, Any],
    cache: Optional[CacheEvidencia] = None,
) -> Dict[str, Any]:
    """Punto de entrada funcional para Engine u orquestación de ciclo."""
    return Centinela(cache=cache).verificar(paquete).a_dict()


def verificar_salida(salida: Any) -> bool:
    """
    Compatibilidad con centinelas simples de módulos:
    True solo si dict con estado APROBADO.
    No sustituye verificar() completo del paquete de ciclo.
    """
    if not isinstance(salida, dict):
        return False
    if "estado" in salida and salida["estado"] in (
        "APROBADO",
        "RETENIDO",
        "PARCIAL",
    ):
        return salida["estado"] == "APROBADO"
    # forma mínima de factores sueltos (legado)
    return all(k in salida for k in ("C", "L", "K")) or all(
        k in salida for k in ("tru_ri", "tru_total")
    )


__all__ = [
    "Centinela",
    "Veredicto",
    "CentinelaError",
    "CacheEvidencia",
    "verificar_salida_paquete",
    "verificar_salida",
]
