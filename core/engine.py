# ===============================================================
# VPSI-TRUTH — core/engine.py
# ===============================================================
#
# ENGINE
# Versión:            18.3
# Esquema contrato:   VPSI-CONTRACT-1.0
# API Engine:         1.0
#
# Función:
#   Agente ejecutor del sistema.
#   Descubre, valida contrato (completo), registra, resuelve
#   dependencias, ejecuta capacidades autorizadas, consolida
#   reportes y entrega paquete_omega().
#
# Qué NO hace:
#   No inventa capacidades. No adivina campos.
#   No calcula Tru. No explora código fuente.
#   No interpreta reportes (eso es Omega).
#
# Principio:
#   Agencia limitada por la unión coherente de los contratos.
#
# ===============================================================


# ===============================================================
# IMPORTACIONES
# ===============================================================

from __future__ import annotations

import importlib.util
import re
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ===============================================================
# FIN IMPORTACIONES
# ===============================================================


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
ESTADOS_CANONICOS = (
    ESTADO_NO_INICIADO,
    ESTADO_OPERATIVO,
    ESTADO_DEGRADADO,
    ESTADO_RECHAZADO,
)

CLAVES_OBLIGATORIAS_CONTRATO = (
    "esquema",
    "version_contrato",
    "version_modulo",
    "id",
    "nombre",
    "rol",
    "descripcion",
    "funcion",
    "no_hace",
    "autoridad",
    "conocimiento_exportable",
    "requiere",
    "autoriza_engine",
    "consultas_soportadas",
    "capacidades",
    "capacidades_meta",
    "reporting",
    "estados_validos",
    "invariantes",
    "estabilidad",
    "compatible_desde",
    "api_engine",
)

PERMISOS_AUTORIZA_ENGINE = (
    "leer",
    "ejecutar",
    "consultar",
    "recombinar",
    "reportar",
    "auditar",
    "inventariar",
    "modificar",
    "alterar",
    "reescribir",
)

BANDERAS_REPORTING = (
    "estado",
    "salud",
    "inventario",
    "capacidades",
    "errores",
    "advertencias",
    "dependencias",
    "version",
    "contrato",
    "conocimiento",
    "metricas",
    "diagnostico",
)

CLAVES_META_CAPACIDAD = ("descripcion", "entrada", "salida")

LISTAS_STR_OBLIGATORIAS = (
    "no_hace",
    "autoridad",
    "conocimiento_exportable",
    "consultas_soportadas",
    "invariantes",
)

# ===============================================================
# FIN CONSTANTES
# ===============================================================


# ===============================================================
# DEFINICIONES
# ===============================================================

class ArranqueError(Exception):
    """Fallo estructural durante el arranque del Engine."""
    pass


class Contenedor:
    """Materialización de un CONTENEDOR. Engine no completa campos."""

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
        self.descripcion: str = str(meta.get("descripcion", ""))
        self.compatible_desde: str = str(meta.get("compatible_desde", ""))
        self.api_engine: str = str(meta.get("api_engine", ""))

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
        ref = self.capacidades.get(clave)
        return ref if callable(ref) else None


class RegistroModulos:
    def __init__(self) -> None:
        self.contenedores: Dict[str, Contenedor] = {}
        self.por_id: Dict[str, Contenedor] = {}
        self.por_rol: Dict[str, List[Contenedor]] = {}

    def registrar(self, cont: Contenedor) -> List[str]:
        errores = []
        if cont.nombre in self.contenedores:
            errores.append(f"duplicado de nombre: '{cont.nombre}' ya registrado")
        if cont.id and cont.id in self.por_id:
            errores.append(
                f"duplicado de id: '{cont.id}' ya registrado "
                f"(módulo {self.por_id[cont.id].nombre})"
            )
        if cont.rol in self.por_rol and self.por_rol[cont.rol]:
            existente = self.por_rol[cont.rol][0].nombre
            errores.append(
                f"duplicado de rol: '{cont.rol}' ya ocupado por '{existente}'"
            )
        if errores:
            return errores
        self.contenedores[cont.nombre] = cont
        if cont.id:
            self.por_id[cont.id] = cont
        self.por_rol.setdefault(cont.rol, []).append(cont)
        return []

    def primero(self, clave: str) -> Optional[Contenedor]:
        if clave in self.contenedores:
            return self.contenedores[clave]
        if clave in self.por_id:
            return self.por_id[clave]
        lista = self.por_rol.get(clave)
        return lista[0] if lista else None

    def total(self) -> int:
        return len(self.contenedores)

# ===============================================================
# FIN DEFINICIONES
# ===============================================================


# ===============================================================
# ENGINE
# ===============================================================

class Engine:
    VERSION = VERSION_ENGINE

    def __init__(
        self,
        raiz_modulos: str | Path,
        invocador_id: str = "core",
        strict: bool = True,
    ) -> None:
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
                raise ArranqueError(
                    "Engine no pudo arrancar:\n  - "
                    + "\n  - ".join(self.errores_arranque)
                )
        else:
            self.estado = ESTADO_OPERATIVO

    # ----------------------------------------------------------
    # DESCUBRIMIENTO
    # ----------------------------------------------------------
    def _descubrir_modulos(self) -> List[Path]:
        if not self.raiz.is_dir():
            return []
        return [
            p for p in sorted(self.raiz.iterdir())
            if p.is_dir() and (p / "__init__.py").is_file()
        ]

    # ----------------------------------------------------------
    # LECTURA
    # ----------------------------------------------------------
    def _leer_contrato(self, path_dir: Path) -> Optional[Dict[str, Any]]:
        init_path = path_dir / "__init__.py"
        nombre_mod = f"vpsi_dinamico_{path_dir.name}"
        try:
            spec = importlib.util.spec_from_file_location(
                nombre_mod, init_path, submodule_search_locations=[str(path_dir)]
            )
            if spec is None or spec.loader is None:
                return None
            mod = importlib.util.module_from_spec(spec)
            sys.modules[nombre_mod] = mod
            spec.loader.exec_module(mod)
            meta = getattr(mod, "CONTENEDOR", None)
            if not isinstance(meta, dict):
                self.errores_arranque.append(
                    f"{path_dir.name}: CONTENEDOR ausente o no es dict"
                )
                return None
            return {
                "meta": meta,
                "modulo": mod,
                "ruta": init_path,
                "nombre_carpeta": path_dir.name,
            }
        except Exception as e:
            self.errores_arranque.append(
                f"{path_dir.name}: error al cargar → {type(e).__name__}: {e}"
            )
            return None

    # ----------------------------------------------------------
    # VERSIONES
    # ----------------------------------------------------------
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
        """
        ">=X.Y" → Engine API debe ser >= X.Y
        "X.Y"   → Engine API debe ser exactamente X.Y
        """
        raw = str(declarado).strip()
        if not raw:
            return "api_engine vacío"

        exacto = False
        if raw.startswith(">="):
            ver_str = raw[2:].strip()
        else:
            exacto = True
            ver_str = raw

        requerida = self._parse_version(ver_str)
        if requerida is None:
            return f"api_engine no parseable: '{declarado}'"

        actual = self._parse_version(API_ENGINE_ACTUAL)
        if actual is None:
            return f"API_ENGINE_ACTUAL inválida: '{API_ENGINE_ACTUAL}'"

        n = max(len(requerida), len(actual))
        requerida = requerida + (0,) * (n - len(requerida))
        actual = actual + (0,) * (n - len(actual))

        if exacto:
            if actual != requerida:
                return (
                    f"api_engine exige exactamente {ver_str}, "
                    f"Engine es {API_ENGINE_ACTUAL}"
                )
        else:
            if actual < requerida:
                return (
                    f"api_engine exige >={ver_str}, "
                    f"Engine es {API_ENGINE_ACTUAL}"
                )
        return None

    def _comparar_compatible_desde(self, declarado: str, nombre: str) -> Optional[str]:
        raw = str(declarado).strip()
        if not raw:
            return f"{nombre}: compatible_desde vacío"
        requerida = self._parse_version(raw)
        if requerida is None:
            return f"{nombre}: compatible_desde no parseable: '{declarado}'"
        actual = self._parse_version(VERSION_ENGINE)
        if actual is None:
            return None
        n = max(len(requerida), len(actual))
        requerida = requerida + (0,) * (n - len(requerida))
        actual = actual + (0,) * (n - len(actual))
        if actual < requerida:
            return (
                f"{nombre}: compatible_desde={raw} pero Engine es {VERSION_ENGINE}"
            )
        return None

    # ----------------------------------------------------------
    # VALIDACIÓN COMPLETA DEL CONTRATO
    # ----------------------------------------------------------
    def _validar_lista_str(self, meta: Dict[str, Any], clave: str, nombre: str) -> List[str]:
        errores = []
        val = meta.get(clave)
        if not isinstance(val, list):
            errores.append(f"{nombre}: '{clave}' debe ser list")
            return errores
        for i, item in enumerate(val):
            if not isinstance(item, str):
                errores.append(
                    f"{nombre}: '{clave}[{i}]' debe ser str, "
                    f"es {type(item).__name__}"
                )
        return errores

    def _validar_esquema(self, meta: Dict[str, Any], nombre: str) -> List[str]:
        errores: List[str] = []

        # Esquema
        if meta.get("esquema") != ESQUEMA_CONTRATO_REQUERIDO:
            errores.append(
                f"{nombre}: esquema '{meta.get('esquema')}' "
                f"!= '{ESQUEMA_CONTRATO_REQUERIDO}'"
            )

        # version_contrato exacta
        vc = meta.get("version_contrato")
        if str(vc) != VERSION_CONTRATO_REQUERIDA:
            errores.append(
                f"{nombre}: version_contrato '{vc}' "
                f"!= '{VERSION_CONTRATO_REQUERIDA}'"
            )

        # version_modulo: str no vacío
        vm = meta.get("version_modulo")
        if not isinstance(vm, str) or not vm.strip():
            errores.append(
                f"{nombre}: version_modulo debe ser str no vacío, "
                f"es {type(vm).__name__}"
            )

        # Claves obligatorias
        for clave in CLAVES_OBLIGATORIAS_CONTRATO:
            if clave not in meta:
                errores.append(f"{nombre}: falta clave obligatoria '{clave}'")

        # Listas de str
        for clave in LISTAS_STR_OBLIGATORIAS:
            if clave in meta:
                errores.extend(self._validar_lista_str(meta, clave, nombre))

        # requiere: list (elementos str preferible)
        requiere = meta.get("requiere")
        if not isinstance(requiere, list):
            errores.append(f"{nombre}: 'requiere' debe ser list")
        else:
            for i, item in enumerate(requiere):
                if not isinstance(item, str):
                    errores.append(
                        f"{nombre}: 'requiere[{i}]' debe ser str, "
                        f"es {type(item).__name__}"
                    )

        # Capacidades callables
        caps = meta.get("capacidades")
        if not isinstance(caps, dict):
            errores.append(f"{nombre}: 'capacidades' debe ser dict")
            caps = {}
        else:
            for k, v in caps.items():
                if not callable(v):
                    errores.append(
                        f"{nombre}: capacidad '{k}' no es callable "
                        f"(tipo={type(v).__name__})"
                    )

        # capacidades_meta: cada capacidad → dict con descripcion, entrada, salida
        meta_caps = meta.get("capacidades_meta")
        if not isinstance(meta_caps, dict):
            errores.append(f"{nombre}: 'capacidades_meta' debe ser dict")
        else:
            for k in caps:
                if k not in meta_caps:
                    errores.append(
                        f"{nombre}: capacidad '{k}' sin entrada en capacidades_meta"
                    )
                    continue
                entrada_meta = meta_caps[k]
                if not isinstance(entrada_meta, dict):
                    errores.append(
                        f"{nombre}: capacidades_meta['{k}'] debe ser dict, "
                        f"es {type(entrada_meta).__name__}"
                    )
                    continue
                for campo in CLAVES_META_CAPACIDAD:
                    if campo not in entrada_meta:
                        errores.append(
                            f"{nombre}: capacidades_meta['{k}'] falta '{campo}'"
                        )
                    elif not isinstance(entrada_meta[campo], str):
                        errores.append(
                            f"{nombre}: capacidades_meta['{k}']['{campo}'] "
                            f"debe ser str"
                        )

        # autoriza_engine: claves exactas + bool
        auth = meta.get("autoriza_engine")
        if not isinstance(auth, dict):
            errores.append(f"{nombre}: 'autoriza_engine' debe ser dict")
        else:
            for permiso in PERMISOS_AUTORIZA_ENGINE:
                if permiso not in auth:
                    errores.append(
                        f"{nombre}: autoriza_engine falta permiso '{permiso}'"
                    )
                elif not isinstance(auth[permiso], bool):
                    errores.append(
                        f"{nombre}: autoriza_engine['{permiso}'] debe ser bool, "
                        f"es {type(auth[permiso]).__name__}"
                    )
            extras = set(auth.keys()) - set(PERMISOS_AUTORIZA_ENGINE)
            if extras:
                errores.append(
                    f"{nombre}: autoriza_engine permisos desconocidos: {sorted(extras)}"
                )

        # reporting: banderas + bool
        reporting = meta.get("reporting")
        if not isinstance(reporting, dict):
            errores.append(f"{nombre}: 'reporting' debe ser dict")
        else:
            for bandera in BANDERAS_REPORTING:
                if bandera not in reporting:
                    errores.append(
                        f"{nombre}: reporting falta bandera '{bandera}'"
                    )
                elif not isinstance(reporting[bandera], bool):
                    errores.append(
                        f"{nombre}: reporting['{bandera}'] debe ser bool, "
                        f"es {type(reporting[bandera]).__name__}"
                    )

        # estados_validos: list no vacía, solo canónicos
        ev = meta.get("estados_validos")
        if not isinstance(ev, list):
            errores.append(f"{nombre}: 'estados_validos' debe ser list")
        elif not ev:
            errores.append(f"{nombre}: 'estados_validos' no puede estar vacío")
        else:
            for i, est in enumerate(ev):
                if not isinstance(est, str):
                    errores.append(
                        f"{nombre}: estados_validos[{i}] debe ser str"
                    )
                elif est not in ESTADOS_CANONICOS:
                    errores.append(
                        f"{nombre}: estados_validos[{i}]='{est}' no es canónico. "
                        f"Admitidos: {ESTADOS_CANONICOS}"
                    )

        # api_engine
        err_api = self._comparar_api(str(meta.get("api_engine", "")))
        if err_api:
            errores.append(f"{nombre}: {err_api}")

        # compatible_desde
        err_cd = self._comparar_compatible_desde(
            str(meta.get("compatible_desde", "")), nombre
        )
        if err_cd:
            errores.append(err_cd)

        return errores

    def _cargar_y_validar(self) -> None:
        for path_dir in self._modulos_descubiertos:
            leido = self._leer_contrato(path_dir)
            if leido is None:
                continue

            meta = leido["meta"]
            nombre = meta.get("nombre") or leido["nombre_carpeta"]

            errores = self._validar_esquema(meta, nombre)
            if errores:
                self.errores_arranque.extend(errores)
                continue

            cont = Contenedor(meta=meta, modulo=leido["modulo"], ruta=leido["ruta"])
            errores_dup = self.registro.registrar(cont)
            if errores_dup:
                for e in errores_dup:
                    self.errores_arranque.append(f"{nombre}: {e}")

    # ----------------------------------------------------------
    # DEPENDENCIAS
    # ----------------------------------------------------------
    def _resolver_dependencias(self) -> None:
        presentes = (
            set(self.registro.por_rol.keys())
            | set(self.registro.por_id.keys())
            | set(self.registro.contenedores.keys())
        )
        faltantes: Dict[str, List[str]] = defaultdict(list)
        grafo_dep: Dict[str, List[str]] = defaultdict(list)

        for nombre, cont in self.registro.contenedores.items():
            for dep in cont.requiere:
                grafo_dep[nombre].append(dep)
                if dep not in presentes:
                    faltantes[nombre].append(dep)
                    self.errores_arranque.append(
                        f"{cont.rol}/{nombre}: dependencia inexistente → '{dep}'"
                    )

        in_degree = {n: 0 for n in self.registro.contenedores}
        for src, dests in grafo_dep.items():
            for d in dests:
                if d in in_degree:
                    in_degree[d] += 1

        cola = deque([n for n, deg in in_degree.items() if deg == 0])
        orden: List[str] = []
        while cola:
            n = cola.popleft()
            orden.append(n)
            for d in grafo_dep.get(n, []):
                if d in in_degree:
                    in_degree[d] -= 1
                    if in_degree[d] == 0:
                        cola.append(d)

        ciclos = [n for n, deg in in_degree.items() if deg > 0]
        if ciclos:
            self.errores_arranque.append(f"Ciclos de dependencia detectados: {ciclos}")

        self._dependencias = {
            "grafo": dict(grafo_dep),
            "faltantes": dict(faltantes),
            "orden_topologico": orden,
            "ciclos": ciclos,
        }

    # ----------------------------------------------------------
    # GRAFO
    # ----------------------------------------------------------
    def _construir_grafo(self) -> None:
        nodos, aristas = [], []
        for nombre, cont in self.registro.contenedores.items():
            nodos.append({
                "id": cont.id or nombre,
                "nombre": nombre,
                "rol": cont.rol,
                "tipo": "modulo",
            })
            for dep in cont.requiere:
                aristas.append({"from": nombre, "to": dep, "tipo": "requiere"})
            for cap in cont.capacidades:
                cap_id = f"{nombre}.{cap}"
                nodos.append({
                    "id": cap_id,
                    "nombre": cap,
                    "tipo": "capacidad",
                    "modulo": nombre,
                })
                aristas.append({
                    "from": nombre,
                    "to": cap_id,
                    "tipo": "declara_capacidad",
                })
        self._grafo = {"nodos": nodos, "aristas": aristas}

    # ----------------------------------------------------------
    # TRAZA
    # ----------------------------------------------------------
    def _registrar_traza(
        self,
        modulo: str,
        capacidad: str,
        estado: str,
        duracion_s: float,
        error: Optional[str] = None,
    ) -> None:
        self._traza_seq += 1
        entrada: Dict[str, Any] = {
            "id_traza": self._traza_seq,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modulo": modulo,
            "capacidad": capacidad,
            "estado": estado,
            "duracion_s": duracion_s,
        }
        if error:
            entrada["error"] = error
        self._trazas.append(entrada)

    # ----------------------------------------------------------
    # EJECUCIÓN
    # ----------------------------------------------------------
    def ejecutar_capacidad(
        self, modulo_o_rol: str, capacidad: str, *args, **kwargs
    ) -> Dict[str, Any]:
        cont = self.registro.primero(modulo_o_rol)
        if cont is None:
            return {"error": f"Módulo/rol no encontrado: {modulo_o_rol}"}

        if cont.autoriza_engine.get("ejecutar") is False:
            return {"error": f"{cont.nombre}: contrato no autoriza ejecutar"}

        fn = cont.fn(capacidad)
        if not callable(fn):
            return {
                "error": f"Capacidad '{capacidad}' no es ejecutable en {cont.nombre}"
            }

        inicio = time.perf_counter()
        try:
            resultado = fn(*args, **kwargs)
            duracion = round(time.perf_counter() - inicio, 6)
            self._registrar_traza(cont.nombre, capacidad, "EXITO", duracion)
            salida = {
                "estado": "EXITO",
                "modulo": cont.nombre,
                "capacidad": capacidad,
                "resultado": resultado,
                "duracion_s": duracion,
            }
            self.resultados_evaluacion.append(salida)
            return salida
        except Exception as e:
            duracion = round(time.perf_counter() - inicio, 6)
            err = f"{type(e).__name__}: {e}"
            self._registrar_traza(
                cont.nombre, capacidad, "ERROR_EJECUCION", duracion, err
            )
            salida = {
                "estado": "ERROR_EJECUCION",
                "modulo": cont.nombre,
                "capacidad": capacidad,
                "error": err,
                "duracion_s": duracion,
            }
            self.resultados_evaluacion.append(salida)
            return salida

    def ejecutar_reporte(self, modulo_o_rol: str) -> Dict[str, Any]:
        return self.ejecutar_capacidad(modulo_o_rol, "reporte")

    def ejecutar_diagnostico(self, modulo_o_rol: str) -> Dict[str, Any]:
        return self.ejecutar_capacidad(modulo_o_rol, "diagnostico")

    def ejecutar_inventario(self, modulo_o_rol: str) -> Dict[str, Any]:
        return self.ejecutar_capacidad(modulo_o_rol, "inventario")

    # ----------------------------------------------------------
    # CONSOLIDACIÓN
    # ----------------------------------------------------------
    def consolidar_reportes(self) -> Dict[str, Any]:
        for nombre, cont in self.registro.contenedores.items():
            if "reporte" in cont.capacidades:
                r = self.ejecutar_capacidad(nombre, "reporte")
                self._reportes_modulos[nombre] = (
                    r.get("resultado")
                    if r.get("estado") == "EXITO"
                    else {"error": r.get("error"), "estado": "NO ENTREGADO POR MODULO"}
                )
            if "diagnostico" in cont.capacidades:
                d = self.ejecutar_capacidad(nombre, "diagnostico")
                if d.get("estado") == "EXITO":
                    self._diagnosticos[nombre] = d.get("resultado")
            if "inventario" in cont.capacidades:
                inv = self.ejecutar_capacidad(nombre, "inventario")
                if inv.get("estado") == "EXITO":
                    self._inventarios[nombre] = inv.get("resultado")
        return {
            "reportes": self._reportes_modulos,
            "diagnosticos": self._diagnosticos,
            "inventarios": self._inventarios,
        }

    # ----------------------------------------------------------
    # PAQUETE OMEGA
    # ----------------------------------------------------------
    def paquete_omega(self) -> Dict[str, Any]:
        if not self._reportes_modulos:
            self.consolidar_reportes()

        reportes_lista: List[Dict[str, Any]] = []

        reportes_lista.append({
            "id": "metadata",
            "titulo": "INFORMACIÓN DEL RUN",
            "orden": 0,
            "contenido": {
                "version_engine": self.VERSION,
                "esquema_contrato": ESQUEMA_CONTRATO_REQUERIDO,
                "version_contrato_requerida": VERSION_CONTRATO_REQUERIDA,
                "api_engine": API_ENGINE_ACTUAL,
                "estado_engine": self.estado,
                "invocador_id": self.invocador_id,
                "total_modulos": self.registro.total(),
                "errores_arranque": list(self.errores_arranque),
                "advertencias": list(self.advertencias),
                "trazas_n": len(self._trazas),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        })

        orden = 1
        for nombre in sorted(self.registro.contenedores.keys()):
            cont = self.registro.contenedores[nombre]
            reportes_lista.append({
                "id": cont.id or nombre,
                "titulo": f"MÓDULO {cont.rol}/{nombre}",
                "orden": orden,
                "contenido": {
                    "id": cont.id,
                    "nombre": cont.nombre,
                    "rol": cont.rol,
                    "version": cont.version,
                    "version_contrato": cont.version_contrato,
                    "esquema": cont.esquema,
                    "estabilidad": cont.estabilidad,
                    "compatible_desde": cont.compatible_desde,
                    "api_engine": cont.api_engine,
                    "descripcion": cont.descripcion,
                    "funcion": cont.funcion,
                    "no_hace": cont.no_hace,
                    "autoridad": cont.autoridad,
                    "conocimiento_exportable": cont.conocimiento_exportable,
                    "consultas_soportadas": cont.consultas_soportadas,
                    "requiere": cont.requiere,
                    "autoriza_engine": cont.autoriza_engine,
                    "capacidades": list(cont.capacidades.keys()),
                    "capacidades_meta": cont.capacidades_meta,
                    "estados_validos": cont.estados_validos,
                    "invariantes": cont.invariantes,
                    "reporte": self._reportes_modulos.get(nombre),
                    "diagnostico": self._diagnosticos.get(nombre),
                    "inventario": self._inventarios.get(nombre),
                },
            })
            orden += 1

        reportes_lista.append({
            "id": "dependencias",
            "titulo": "DEPENDENCIAS",
            "orden": orden,
            "contenido": self._dependencias,
        })
        orden += 1
        reportes_lista.append({
            "id": "grafo",
            "titulo": "GRAFO ESTRUCTURAL",
            "orden": orden,
            "contenido": self._grafo,
        })
        orden += 1
        reportes_lista.append({
            "id": "trazas",
            "titulo": "TRAZAS DE EJECUCIÓN",
            "orden": orden,
            "contenido": list(self._trazas),
        })

        return {
            "metadata": {
                "version_engine": self.VERSION,
                "estado_engine": self.estado,
                "esquema_contrato": ESQUEMA_CONTRATO_REQUERIDO,
                "total_modulos": self.registro.total(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "reportes": reportes_lista,
        }

    # ----------------------------------------------------------
    # CONSULTA
    # ----------------------------------------------------------
    def censar(self) -> dict:
        return {
            "total": self.registro.total(),
            "roles": {
                rol: [c.nombre for c in lista]
                for rol, lista in self.registro.por_rol.items()
            },
            "roles_vacios": [],
            "rechazados": list(self.errores_arranque),
            "cargados": [
                {
                    "id": c.id,
                    "nombre": c.nombre,
                    "rol": c.rol,
                    "version": c.version,
                    "esquema": c.esquema,
                    "estabilidad": c.estabilidad,
                    "capacidades": list(c.capacidades.keys()),
                }
                for c in self.registro.contenedores.values()
            ],
        }

    def estado_global(self) -> Dict[str, Any]:
        return {
            "tipo": "estado_global",
            "version_engine": self.VERSION,
            "esquema_contrato": ESQUEMA_CONTRATO_REQUERIDO,
            "estado": self.estado,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_contenedores": self.registro.total(),
            "errores_arranque": list(self.errores_arranque),
            "advertencias": list(self.advertencias),
            "trazas_n": len(self._trazas),
            "dependencias": self._dependencias,
            "grafo": self._grafo,
        }

    def obtener_trazas(self) -> Tuple[Dict[str, Any], ...]:
        """Copia inmutable de la evidencia de ejecución."""
        return tuple(dict(t) for t in self._trazas)

# ===============================================================
# FIN ENGINE
# ===============================================================

# ===============================================================
# COMIENZA: CENTINELA
# ===============================================================
# Ubicación: core/engine.py
#
# 1) IMPORTACIONES — añadir:
#       from core.centinela import Centinela, Veredicto
#       from core.paquete_contrato import PKG_CICLO_ID
#
# 2) Engine.__init__ — solo el atributo (NO instanciar aún):
#       self._centinela: Optional[Centinela] = None
#
# 3) Sustituir _registrar_traza completo.
#
# 4) Añadir property centinela + invocar + verificar_con_centinela
#    (después de obtener_trazas / antes de FIN ENGINE).
# ===============================================================

    def _registrar_traza(
        self,
        modulo: str,
        capacidad: str,
        estado: str,
        duracion_s: float,
        error: Optional[str] = None,
        **extras: Any,
    ) -> None:
        self._traza_seq += 1
        entrada: Dict[str, Any] = {
            "id_traza": self._traza_seq,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modulo": modulo,
            "capacidad": capacidad,
            "estado": estado,
            "duracion_s": duracion_s,
        }
        if error:
            entrada["error"] = error
        for clave, valor in extras.items():
            if valor is not None:
                entrada[clave] = valor
        self._trazas.append(entrada)

    @property
    def centinela(self) -> Centinela:
        """
        Auditor perezoso: se crea solo cuando el Engine ya terminó
        de construirse. Evita que Centinela vea un Engine parcial.
        """
        if self._centinela is None:
            self._centinela = Centinela(invocador=self)
        return self._centinela

    def invocar(
        self,
        modulo: str,
        capacidad: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Puente InvocadorCapacidades para core/centinela.py.
        Centinela no importa módulos de dominio: reproduce
        capacidades autorizadas solo a través de este método.
        """
        salida = self.ejecutar_capacidad(modulo, capacidad, *args, **kwargs)
        if isinstance(salida, dict) and salida.get("estado") == "EXITO":
            return salida.get("resultado")
        if isinstance(salida, dict) and "error" in salida:
            raise RuntimeError(str(salida.get("error")))
        return salida

    def verificar_con_centinela(
        self,
        paquete: Dict[str, Any],
        *,
        depositar_salida: bool = True,
    ) -> Veredicto:
        """
        Cierre oficial del ciclo.

        Engine ejecuta → consolida → genera paquete →
        verificar_con_centinela() → Veredicto.

        Usa self.centinela (instancia única, creación diferida).
        Traza con ciclo_id para correlacionar expediente.
        """
        inicio = time.perf_counter()
        ciclo_id = None
        if isinstance(paquete, dict):
            ciclo_id = paquete.get(PKG_CICLO_ID)
        try:
            veredicto = self.centinela.verificar(
                paquete,
                depositar_salida=depositar_salida,
            )
            duracion = round(time.perf_counter() - inicio, 6)
            self._registrar_traza(
                modulo="ENGINE",
                capacidad="verificar_con_centinela",
                estado=str(veredicto.estado),
                duracion_s=duracion,
                ciclo_id=ciclo_id,
            )
            return veredicto
        except Exception as e:
            duracion = round(time.perf_counter() - inicio, 6)
            err = "{0}: {1}".format(type(e).__name__, e)
            self._registrar_traza(
                modulo="ENGINE",
                capacidad="verificar_con_centinela",
                estado="ERROR_AUDITORIA",
                duracion_s=duracion,
                error=err,
                ciclo_id=ciclo_id,
            )
            raise

# ===============================================================
# FIN: CENTINELA
# ===============================================================

# ===============================================================
# EXPORTACIONES
# ===============================================================

__all__ = [
    "Engine",
    "ArranqueError",
    "Contenedor",
    "RegistroModulos",
    "VERSION_ENGINE",
    "ESQUEMA_CONTRATO_REQUERIDO",
    "VERSION_CONTRATO_REQUERIDA",
]

# ===============================================================
# FIN DEL MÓDULO ENGINE
# ===============================================================
