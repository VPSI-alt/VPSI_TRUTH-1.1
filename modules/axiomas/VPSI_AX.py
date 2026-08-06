"""
VPSI-TRUTH / VPSI_AX.py

Contenedor de axiomas. Rol AX.

QUE ES ESTE MÓDULO:
  La definición de lo que es un axioma, un lema, un teorema y un
  corolario, y la vigilancia sobre ellos. No pertenece a ninguna teoría
  y no conoce ninguna. Vela por lo que se deje caer dentro.

QUE VIGILA:
  Una regla: no se contradicen entre sí.
    - contradiccion_directa: misma tripleta, polaridad opuesta.
    - contradiccion_de_cota: mismo sujeto y relación, dos cotas distintas.

  Si hay contradicción, barrer() devuelve coherente=False y el sistema no arranca.

FORMA DE UNA DECLARACIÓN:
    {
      "id": str,
      "tipo": "axioma" | "lema" | "teorema" | "corolario",
      "sujeto": str,
      "relacion": str,
      "objeto": str,
      "polaridad": bool,
      "cota": str | None,
      "depende_de": [id, ...],
      "gobierna": [nombre_de_modulo, ...],
      "enunciado": str,
    }

FORMA DE UN CUERPO:
  Un subdirectorio con __init__.py que expone:
      CUERPO = {"nombre": str, "version": str}
      def declaraciones() -> lista
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Any

CONTENEDOR = {
    "nombre": "VPSI",
    "rol": "AX",
    "version": "9.4",
    "requiere": [],
}

_DIR = Path(__file__).parent

# Tipos de declaraciones
AXIOMA = "axioma"
LEMA = "lema"
TEOREMA = "teorema"
COROLARIO = "corolario"
TIPOS = (AXIOMA, LEMA, TEOREMA, COROLARIO)
OBLIGATORIOS = ("id", "tipo", "sujeto", "relacion", "objeto", "polaridad")

# ===============================================================
# FUNCIONES DE NORMALIZACIÓN Y VALIDACIÓN
# ===============================================================

def normalizar(decl: Dict, cuerpo: str) -> Dict:
    if not isinstance(decl, dict):
        raise ValueError(f"{cuerpo}: declaración no es dict")
    for k in OBLIGATORIOS:
        if k not in decl:
            raise ValueError(f"{cuerpo}:{decl.get('id', '?')} sin clave '{k}'")
    tipo = str(decl["tipo"]).lower()
    if tipo not in TIPOS:
        raise ValueError(f"{cuerpo}:{decl['id']} tipo '{tipo}' no válido. Admitidos: {TIPOS}")
    if not isinstance(decl["polaridad"], bool):
        raise ValueError(f"{cuerpo}:{decl['id']} polaridad debe ser bool")
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

def clave(d: Dict) -> tuple:
    return (
        d["sujeto"].lower().strip(),
        d["relacion"].lower().strip(),
        d["objeto"].lower().strip(),
    )

def ref(d: Dict) -> str:
    return f"{d['cuerpo']}:{d['id']}"

# ===============================================================
# DECLARACIONES DEL CUERPO AXIOMÁTICO VPSI (24 TEOREMAS, 10 AXIOMAS, etc.)
# ===============================================================

def declaraciones():
    return [
        # ==========================================================
        # AXIOMAS ONTOLÓGICO-FÍSICOS (A1-A11)
        # ==========================================================
        {
            "id": "A1",
            "tipo": "axioma",
            "sujeto": "S",
            "relacion": "tiene_sustrato_fisico",
            "objeto": "material_energetico_causal",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia"],
            "enunciado": "Todo sistema S capaz de procesar información tiene un sustrato físico (material, energético y causal) que lo soporta (Axioma A1).",
        },
        {
            "id": "A2",
            "tipo": "axioma",
            "sujeto": "S_t",
            "relacion": "es_funcion_de",
            "objeto": "S_{t-1} y E_{t-1}",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia", "temporal"],
            "enunciado": "Todo estado informacional S_t: S_t = f(S_{t-1}, E_{t-1}) (Axioma A2: Continuidad Informacional).",
        },
        {
            "id": "A3",
            "tipo": "axioma",
            "sujeto": "I",
            "relacion": "no_existe_sin_causa",
            "objeto": "informacion_previa",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia", "informacion"],
            "enunciado": "No existe información I generada por S que sea causalmente independiente de toda la información previamente accesible a S (Axioma A3: No Ex Nihilo).",
        },
        {
            "id": "A4",
            "tipo": "axioma",
            "sujeto": "I_new",
            "relacion": "es_recombinacion_de",
            "objeto": "I_prev",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia", "meta"],
            "enunciado": "Toda estructura informacional nueva I_new es el resultado de una función física g: I_new = g(I_prev) (Axioma A4: Recombinación Universal).",
        },
        {
            "id": "A5",
            "tipo": "axioma",
            "sujeto": "I_accessible(S, t)",
            "relacion": "es_subconjunto_de",
            "objeto": "C(S, t)",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia", "informacion"],
            "enunciado": "La información accesible I_accessible(S, t) es un subconjunto del cono causal C(S, t) (Axioma A5: Restricción Causal).",
        },
        {
            "id": "A6",
            "tipo": "axioma",
            "sujeto": "psi",
            "relacion": "equivalente_a",
            "objeto": "Phi_physical",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia"],
            "enunciado": "Todo proceso cognitivo psi es equivalente a un proceso físico Phi_physical (Axioma A6: Equivalencia Física de la Cognición).",
        },
        {
            "id": "A7",
            "tipo": "axioma",
            "sujeto": "C",
            "relacion": "depende_de",
            "objeto": "Phi_1, ..., Phi_n",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia"],
            "enunciado": "Toda construcción conceptual C depende de estados físicos previos Phi_1, ..., Phi_n (Axioma A7: Dependencia Representacional).",
        },
        {
            "id": "A8",
            "tipo": "axioma",
            "sujeto": "O",
            "relacion": "pertenece_a",
            "objeto": "span(H_phys(S))",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia"],
            "enunciado": "Toda salida O de S pertenece al espacio generado por su historia física H_phys(S) (Axioma A8: No Escape Ontológico).",
        },
        {
            "id": "A9",
            "tipo": "axioma",
            "sujeto": "I_1, I_2",
            "relacion": "pertenece_a",
            "objeto": "espacio_causalmente_accesible",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia"],
            "enunciado": "Toda nueva configuración I_1, I_2 pertenece al espacio causalmente accesible (Axioma A9: Cierre Reconfiguracional).",
        },
        {
            "id": "A10",
            "tipo": "axioma",
            "sujeto": "A",
            "relacion": "es_inmutable_en_R",
            "objeto": "t",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia", "temporal"],
            "enunciado": "Toda acción A ejecutada en el tiempo t es un evento causal inmutable en R (Axioma A10: Irreversibilidad Causal de la Acción).",
        },
        {
            "id": "A11",
            "tipo": "axioma",
            "sujeto": "a",
            "relacion": "induce_transicion_en",
            "objeto": "R",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia", "temporal"],
            "enunciado": "Toda acción a induce una transición T_a: R_t → R_{t+1} dentro de R (Axioma A11: Transformación de Estado en la Realidad).",
        },
        {
            "id": "beta",
            "tipo": "axioma",
            "sujeto": "BETA",
            "relacion": "igual_a",
            "objeto": "1/27",
            "polaridad": True,
            "cota": "1/27",
            "depende_de": [],
            "gobierna": ["constantes"],
            "enunciado": "BETA = 1/27 (Axioma β: Mínimo Estructural Irreducible, Sección 2.3).",
        },

        # ==========================================================
        # AXIOMAS INFORMACIONALES-FORMALES (F1-F9)
        # ==========================================================
        {
            "id": "F1",
            "tipo": "axioma",
            "sujeto": "R, X, Y, U",
            "relacion": "estan_definidos_conjuntamente_sobre",
            "objeto": "(Omega, F, P)",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["informacion"],
            "enunciado": "(R, X, Y, U) están definidos conjuntamente sobre (Ω, F, P). Las entropías y la información mutua son finitas (Axioma F1).",
        },
        {
            "id": "F2",
            "tipo": "axioma",
            "sujeto": "R",
            "relacion": "es_referente_externo_absoluto",
            "objeto": "1",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["informacion"],
            "enunciado": "R es el referente externo absoluto que el sistema intenta describir (Axioma F2).",
        },
        {
            "id": "F3",
            "tipo": "axioma",
            "sujeto": "X",
            "relacion": "es_evidencia_observable_de",
            "objeto": "R",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["informacion"],
            "enunciado": "X es la evidencia observable producida a partir de R: R → X es un mapeo estocástico, posiblemente ruidoso (Axioma F3).",
        },
        {
            "id": "F4",
            "tipo": "axioma",
            "sujeto": "Y",
            "relacion": "igual_a",
            "objeto": "g(X, U)",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["informacion"],
            "enunciado": "Y = g(X, U), donde U ⊥ R | X. El sistema opera sobre la evidencia X, no directamente sobre R (Axioma F4: Cadena de Markov R → X → Y).",
        },
        {
            "id": "F5",
            "tipo": "axioma",
            "sujeto": "K(Z, R)",
            "relacion": "igual_a",
            "objeto": "I(R; Z)",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["informacion"],
            "enunciado": "K(Z, R) := I(R; Z) es el conocimiento verificable de Z respecto a R (Axioma F5).",
        },
        {
            "id": "F6",
            "tipo": "axioma",
            "sujeto": "Y",
            "relacion": "es_deduccion_si",
            "objeto": "se_deriva_necesariamente_de_X",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["informacion"],
            "enunciado": "Y es una deducción si sigue necesariamente de X más los axiomas declarados. K(Y) = 1.0 (Axioma F6).",
        },
        {
            "id": "F7",
            "tipo": "axioma",
            "sujeto": "Y",
            "relacion": "es_hipotesis_si",
            "objeto": "es_plausible_dado_X_pero_no_implicado",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["informacion"],
            "enunciado": "Y es una hipótesis si es plausible dado X pero no implicado por X. Debe etiquetarse explícitamente como una suposición. K(Y) = 0.5 (Axioma F7).",
        },
        {
            "id": "F8",
            "tipo": "axioma",
            "sujeto": "Y",
            "relacion": "es_invencion_si",
            "objeto": "afirma_hechos_sobre_R_sin_soporte_en_X",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["informacion"],
            "enunciado": "Y es una invención si afirma hechos sobre R sin soporte en X. Debe señalarse o rechazarse. K(Y) = 0.0 (Axioma F8).",
        },
        {
            "id": "F9",
            "tipo": "axioma",
            "sujeto": "A",
            "relacion": "igual_a",
            "objeto": "1 - (#aserciones_sin_soporte_en_X / #aserciones_que_describen_R)",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["informacion"],
            "enunciado": "A (Puntuación de Anclaje) = 1 - (#aserciones sin soporte en X / #aserciones que describen R) (Axioma F9).",
        },

        # ==========================================================
        # AXIOMAS EPISTEMOLÓGICOS (E1-E3)
        # ==========================================================
        {
            "id": "E1",
            "tipo": "axioma",
            "sujeto": "A ⊨ φ",
            "relacion": "depende_de",
            "objeto": "relacion_de_satisfaccion_sobre_modelos",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["epistemologia"],
            "enunciado": "A ⊨ φ depende únicamente de la relación de satisfacción sobre modelos. No depende de la ejecución de ningún verificador (Axioma E1: Independencia Semántica).",
        },
        {
            "id": "E2",
            "tipo": "axioma",
            "sujeto": "A ⊢ φ",
            "relacion": "depende_de",
            "objeto": "existencia_de_π_finito",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["epistemologia"],
            "enunciado": "A ⊢ φ depende de la existencia del objeto finito π. No depende de la aprobación externa (Axioma E2: Independencia Sintáctica).",
        },
        {
            "id": "E3",
            "tipo": "axioma",
            "sujeto": "φ",
            "relacion": "no_implica",
            "objeto": "K_a(φ)",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["epistemologia"],
            "enunciado": "Para todo agente a: φ ⇏ K_a(φ) y K_a(φ) ⇏ φ como leyes universales (Axioma E3: No Identificación Epistémica Universal).",
        },

        # ==========================================================
        # AXIOMAS DE VERDAD (TA1-TA8)
        # ==========================================================
        {
            "id": "TA1",
            "tipo": "axioma",
            "sujeto": "C(D)",
            "relacion": "igual_a_1_si",
            "objeto": "¬∃P: (D ⊢ P) ∧ (D ⊢ ¬P)",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["logica"],
            "enunciado": "C(D) = 1 ⇔ ¬∃P: (D ⊢ P) ∧ (D ⊢ ¬P) (Axioma TA1: No Contradicción de la Coherencia).",
        },
        {
            "id": "TA2",
            "tipo": "axioma",
            "sujeto": "L(D)",
            "relacion": "igual_a_1_si",
            "objeto": "∀z, T(z) es_unico_e_invariante",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["logica"],
            "enunciado": "L(D) = 1 ⇔ ∃ espacio Z y transformación T: ∀z ∈ Z, T(z) es único e invariante (Axioma TA2: Objetividad de la Lógica).",
        },
        {
            "id": "TA3",
            "tipo": "axioma",
            "sujeto": "K(D)",
            "relacion": "igual_a_1_si",
            "objeto": "||D(z) - O(z)|| ≤ ε",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["logica"],
            "enunciado": "K(D) = 1 ⇔ ||D(z) - O(z)|| ≤ ε, donde O es el dominio observado (Axioma TA3: Dependencia Externa de la Correlación).",
        },
        {
            "id": "TA4",
            "tipo": "axioma",
            "sujeto": "R",
            "relacion": "es_independiente_de",
            "objeto": "observador",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia", "logica"],
            "enunciado": "R ⊥ observador: R existe independientemente de cualquier R_i (Axioma TA4: Independencia de la Realidad).",
        },
        {
            "id": "TA5",
            "tipo": "axioma",
            "sujeto": "Tru(D)",
            "relacion": "igual_a",
            "objeto": "C(D) * L(D) * K(D)",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["logica"],
            "enunciado": "Tru(D) = C(D) * L(D) * K(D). Un factor en 0 anula todo Tru(D). No hay compensación posible (Axioma TA5: Multiplicatividad de la Verdad).",
        },
        {
            "id": "TA6",
            "tipo": "axioma",
            "sujeto": "w_C + w_L + w_K + w_R",
            "relacion": "igual_a",
            "objeto": "1",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["logica"],
            "enunciado": "w_C + w_L + w_K + w_R = 1, donde R → w_R = β = 1/27, R_i → w_C + w_L + w_K = α = 26/27 (Axioma TA6: Distribución de Pesos con β Geométrico).",
        },
        {
            "id": "TA7",
            "tipo": "axioma",
            "sujeto": "Y",
            "relacion": "igual_a",
            "objeto": "g(X, U)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["F4"],
            "gobierna": ["logica"],
            "enunciado": "Y = g(X, U), donde U ⊥ R | X. El sistema procesa X de R, no R directamente (Axioma TA7: Sin Acceso Directo).",
        },
        {
            "id": "TA8",
            "tipo": "axioma",
            "sujeto": "R",
            "relacion": "es_invariante_bajo",
            "objeto": "variacion_en_C_L_K",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4"],
            "gobierna": ["logica"],
            "enunciado": "∀ variación en C, L, K: R permanece invariante. El fallo en Tru(D) ocurre en R_i, nunca en R (Axioma TA8: Invariancia de R bajo Variación de Capacidad).",
        },

        # ==========================================================
        # TEOREMAS (T1-T17, U0, U1, M1, M.1, TT.6.1, B-Canonical, TR1)
        # ==========================================================
        {
            "id": "T1",
            "tipo": "teorema",
            "sujeto": "R",
            "relacion": "no_tiene_correlacion_con",
            "objeto": "X",
            "polaridad": True,
            "cota": None,
            "depende_de": ["A3", "F4"],
            "gobierna": ["ontologia", "informacion"],
            "enunciado": "No hay correlación entre R y X si X no está anclado en R (Teorema 1: Imposibilidad de Creación Ex Nihilo).",
        },
        {
            "id": "T2",
            "tipo": "teorema",
            "sujeto": "I(R;Y)",
            "relacion": "es_menor_o_igual_a",
            "objeto": "I(R;X)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["F4", "F5"],
            "gobierna": ["informacion"],
            "enunciado": "I(R;Y) ≤ I(R;X) (Teorema 2: Límite Informacional VPSI).",
        },
        {
            "id": "T3",
            "tipo": "teorema",
            "sujeto": "H(R)",
            "relacion": "es_mayor_que",
            "objeto": "I(R;X)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["F2", "F3"],
            "gobierna": ["informacion", "temporal"],
            "enunciado": "H(R) > I(R;X): R es informacionalmente más rico que cualquier observador (Teorema 3: Ausencia de Conocimiento sin Evidencia).",
        },
        {
            "id": "T4",
            "tipo": "teorema",
            "sujeto": "I(R;Y)",
            "relacion": "no_aumenta_sin_nueva_evidencia",
            "objeto": "X",
            "polaridad": True,
            "cota": None,
            "depende_de": ["F4", "T2"],
            "gobierna": ["informacion", "epistemologia"],
            "enunciado": "Sin nueva evidencia más allá de X, ningún procesamiento interno causa que I(R;Y) exceda I(R;X) (Teorema 4: Irreversibilidad Epistémica).",
        },
        {
            "id": "T5",
            "tipo": "teorema",
            "sujeto": "I",
            "relacion": "es_equivalente_fisicamente_a",
            "objeto": "F(I_prev)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["A4", "A6"],
            "gobierna": ["ontologia", "epistemologia"],
            "enunciado": "Toda producción I de S es físicamente equivalente a una función F aplicada al estado físico previo de S (Teorema 5: Equivalencia Física de la Invención).",
        },
        {
            "id": "T6",
            "tipo": "teorema",
            "sujeto": "Tru(T)",
            "relacion": "es_estructuralmente_distinto_de",
            "objeto": "T",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA1", "TA2", "TA3"],
            "gobierna": ["logica", "ontologia"],
            "enunciado": "Para toda teoría T y su valor de verdad Tru(T): Tru(T) es estructuralmente distinto de T. La verdad, la verificación y la confusión son independientes (Teorema 6: Separación Estructural).",
        },
        {
            "id": "T7",
            "tipo": "teorema",
            "sujeto": "S",
            "relacion": "no_modifica",
            "objeto": "R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4", "TA7"],
            "gobierna": ["logica", "ontologia"],
            "enunciado": "El verificador (observador S) no crea ni modifica R (Teorema 7: El Verificador no Crea Verdad).",
        },
        {
            "id": "T8",
            "tipo": "teorema",
            "sujeto": "Tru_Ri(D)",
            "relacion": "igual_a_1_si",
            "objeto": "C(D) = L(D) = K(D) = 1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA5"],
            "gobierna": ["logica"],
            "enunciado": "Tru_Ri(D) = 1 ⇔ C(D) = L(D) = K(D) = 1 (Teorema 8: La Sincronización es Condición Necesaria y Suficiente de Verdad Completa).",
        },
        {
            "id": "T9",
            "tipo": "teorema",
            "sujeto": "Tru_total(D)",
            "relacion": "igual_a",
            "objeto": "BETA",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA5", "beta"],
            "gobierna": ["logica"],
            "enunciado": "Si I(R;X) = 0, entonces Tru_Ri(D) = 0 y Tru_total(D) = β (Teorema 9: Imposibilidad de Verdad sin Evidencia).",
        },
        {
            "id": "T10",
            "tipo": "teorema",
            "sujeto": "R",
            "relacion": "es_invariante_bajo",
            "objeto": "procesamiento_interno_de_S",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4", "TA8"],
            "gobierna": ["ontologia", "logica"],
            "enunciado": "R es invariante bajo cualquier procesamiento interno de S (Teorema 10: Invariancia de R bajo Procesamiento Interno).",
        },
        {
            "id": "T11",
            "tipo": "teorema",
            "sujeto": "BETA",
            "relacion": "garantiza",
            "objeto": "R > 0",
            "polaridad": True,
            "cota": None,
            "depende_de": ["beta"],
            "gobierna": ["constantes", "ontologia"],
            "enunciado": "β garantiza que R > 0 en todo momento y para todo sistema en ℝ³ (Teorema 11: β como Garantía de Existencia de R).",
        },
        {
            "id": "T12",
            "tipo": "teorema",
            "sujeto": "Tru_total(D)",
            "relacion": "disminuye_con",
            "objeto": "confusion_Ri_equiv_R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T6", "T7"],
            "gobierna": ["logica", "semantica"],
            "enunciado": "La confusión de R_i con R es la única fuente de colapso en Tru_total(D) (Teorema 12: Conflación de R_i con R como Fuente de Colapso).",
        },
        {
            "id": "T13",
            "tipo": "teorema",
            "sujeto": "observadores_independientes",
            "relacion": "convergen_a",
            "objeto": "R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T8", "T11"],
            "gobierna": ["epistemologia", "semantica"],
            "enunciado": "La convergencia de observadores independientes con Tru(D) = 1 para el mismo hecho D prueba la independencia de R (Teorema 13: Convergencia de Observadores como Prueba de R).",
        },
        {
            "id": "T14",
            "tipo": "teorema",
            "sujeto": "R",
            "relacion": "posee",
            "objeto": "verdad",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4", "T7"],
            "gobierna": ["logica", "epistemologia"],
            "enunciado": "La verdad pertenece a R, no a S. El error pertenece a S (Teorema 14: Pertenencia de la Verdad y Distribución del Error).",
        },
        {
            "id": "T15",
            "tipo": "teorema",
            "sujeto": "P",
            "relacion": "es_valido_si",
            "objeto": "Di ∩ Dj ≠ ∅ y Di ∪ Dj ⊃ Di y Di ∪ Dj ⊃ Dj",
            "polaridad": True,
            "cota": None,
            "depende_de": ["A4", "TA5"],
            "gobierna": ["ontologia", "meta"],
            "enunciado": "Una nueva proposición P = g(Ti, Tj) es válida si Di ∩ Dj ≠ ∅ y Di ∪ Dj es estrictamente mayor que Di y Dj (Teorema 15: Emergencia Estructural vía Recombinación Invariante).",
        },
        {
            "id": "T16",
            "tipo": "teorema",
            "sujeto": "Tru_total(D)",
            "relacion": "es_menor_o_igual_a",
            "objeto": "ALPHA",
            "polaridad": True,
            "cota": "26/27",
            "depende_de": ["TA6", "beta"],
            "gobierna": ["logica", "meta"],
            "enunciado": "Tru_total(D) ≤ α = 26/27 para cualquier descripción D (Teorema 16: Techo Estructural α).",
        },
        {
            "id": "T17",
            "tipo": "teorema",
            "sujeto": "Tru_total(D)",
            "relacion": "es_mayor_o_igual_a",
            "objeto": "BETA",
            "polaridad": True,
            "cota": "1/27",
            "depende_de": ["beta", "TA6"],
            "gobierna": ["constantes", "logica"],
            "enunciado": "Tru_total(D) ≥ β = 1/27. Tru_total(D) = 0 es formalmente imposible (Teorema 17: Imposibilidad Absoluta de Colapso Total).",
        },
        {
            "id": "U0",
            "tipo": "teorema",
            "sujeto": "forma_multiplicativa",
            "relacion": "satisface_8_axiomas",
            "objeto": "AX1-AX8",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA5"],
            "gobierna": ["logica", "informacion"],
            "enunciado": "La forma multiplicativa Tru(D) = C·L·K·α + β satisface los 8 axiomas AX1-AX8 (Teorema U0: Validez Estructural de la Forma Multiplicativa).",
        },
        {
            "id": "U1",
            "tipo": "teorema",
            "sujeto": "BETA",
            "relacion": "es_una_necesidad_estructural",
            "objeto": "BETA > 0",
            "polaridad": True,
            "cota": None,
            "depende_de": ["beta", "A4"],
            "gobierna": ["constantes", "meta"],
            "enunciado": "β > 0 es una necesidad estructural. Si β = 0, el sistema entra en estancamiento (Teorema U1: Principio de No Estancamiento).",
        },
        {
            "id": "M1",
            "tipo": "teorema",
            "sujeto": "protocolo_de_medicion",
            "relacion": "es_objetivo_e_invariante",
            "objeto": "P1-P4",
            "polaridad": True,
            "cota": None,
            "depende_de": ["F4", "F5"],
            "gobierna": ["meta", "logica"],
            "enunciado": "El protocolo de medición es objetivo e invariante (Teorema M1: Protocolo de Medición Objetiva).",
        },
        {
            "id": "M.1",
            "tipo": "teorema",
            "sujeto": "descripcion_meta",
            "relacion": "esta_acotada_por",
            "objeto": "ALPHA_y_BETA",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA6", "T16", "T17"],
            "gobierna": ["meta", "ontologia"],
            "enunciado": "Toda descripción a nivel meta está acotada por ALPHA y BETA (Teorema M.1: Cierre Meta-Ontológico).",
        },
        {
            "id": "TT.6.1",
            "tipo": "teorema",
            "sujeto": "C ∧ L ∧ K ∧ R",
            "relacion": "debe_cumplirse_simultaneamente",
            "objeto": "1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA5", "TA4"],
            "gobierna": ["logica", "semantica", "epistemologia"],
            "enunciado": "C, L, K y R deben cumplirse simultáneamente para Tru(D) = 1 (Teorema TT.6.1: Restricción de Verdad).",
        },
        {
            "id": "B-Canonical",
            "tipo": "teorema",
            "sujeto": "BETA",
            "relacion": "tiene_5_propiedades_convergentes",
            "objeto": "1/27",
            "polaridad": True,
            "cota": None,
            "depende_de": ["beta", "A1", "A4"],
            "gobierna": ["constantes", "meta", "ontologia", "logica"],
            "enunciado": "β = 1/27 emerge de 5 propiedades convergentes: 1) Teselación de ℝ³, 2) N=3 como umbral mínimo, 3) β>0 vía medida de Lebesgue, 4) Multiplicatividad por ortogonalidad, 5) Imposibilidad del modelo aditivo (Teorema B-Canonical).",
        },
        {
            "id": "TR1",
            "tipo": "teorema",
            "sujeto": "|Im(⊕)|",
            "relacion": "es_mayor_que",
            "objeto": "|Θ|",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T15", "A4"],
            "gobierna": ["meta", "informacion", "logica"],
            "enunciado": "|Im(⊕)| = 153 > 24 = |Θ|. El framework genera más verdades de las que postula (Teorema TR1: Generatividad Estructural).",
        },

        # ==========================================================
        # LEMAS (TT.5.1 - TT.13.1)
        # ==========================================================
        {
            "id": "TT.5.1",
            "tipo": "lema",
            "sujeto": "C(D)",
            "relacion": "es_necesario_para",
            "objeto": "Tru(D) = 1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA1"],
            "gobierna": ["logica"],
            "enunciado": "Tru(D) = 1 ⇒ C(D) = 1 (Lemma TT.5.1: Coherencia es Necesaria para la Verdad).",
        },
        {
            "id": "TT.5.2",
            "tipo": "lema",
            "sujeto": "L(D)",
            "relacion": "es_necesario_para",
            "objeto": "Tru(D) = 1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA2"],
            "gobierna": ["logica"],
            "enunciado": "Tru(D) = 1 ⇒ L(D) = 1 (Lemma TT.5.2: Lógica es Necesaria para la Verdad).",
        },
        {
            "id": "TT.5.3",
            "tipo": "lema",
            "sujeto": "K(D)",
            "relacion": "es_necesario_para",
            "objeto": "Tru(D) = 1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA3"],
            "gobierna": ["logica"],
            "enunciado": "Tru(D) = 1 ⇒ K(D) = 1 (Lemma TT.5.3: Correlación es Necesaria para la Verdad).",
        },
        {
            "id": "TT.5.4",
            "tipo": "lema",
            "sujeto": "Real(D)",
            "relacion": "es_necesario_para",
            "objeto": "Tru(D) = 1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4"],
            "gobierna": ["logica"],
            "enunciado": "Tru(D) = 1 ⇒ Real(D) = 1 (Lemma TT.5.4: Realidad es Necesaria para la Verdad).",
        },
        {
            "id": "TT.5.5",
            "tipo": "lema",
            "sujeto": "I(R;Y)",
            "relacion": "es_menor_o_igual_a",
            "objeto": "I(R;X)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["F4", "F5"],
            "gobierna": ["informacion"],
            "enunciado": "I(R;Y) ≤ I(R;X) (Lemma TT.5.5: Límite Informacional VPSI).",
        },
        {
            "id": "TT.7.1",
            "tipo": "corolario",
            "sujeto": "X",
            "relacion": "en",
            "objeto": "{C, L, K, Real}",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TT.5.1", "TT.5.4"],
            "gobierna": ["logica"],
            "enunciado": "∃X ∈ {C, L, K, Real} : X(D) = 0 ⇒ Tru(D) = 0 (Corolario TT.7.1: Un Solo Fallo Anula la Verdad).",
        },
        {
            "id": "TT.7.2",
            "tipo": "corolario",
            "sujeto": "C(D)",
            "relacion": "no_implica",
            "objeto": "Tru(D) = 1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TT.5.1"],
            "gobierna": ["logica"],
            "enunciado": "C(D) = 1 ⇏ Tru(D) = 1. Ninguna condición aislada es suficiente (Corolario TT.7.2).",
        },
        {
            "id": "TT.7.3",
            "tipo": "corolario",
            "sujeto": "C(D) ∧ L(D) ∧ K(D) ∧ Real(D)",
            "relacion": "implica",
            "objeto": "Tru(D) = 1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TT.5.1", "TT.5.4"],
            "gobierna": ["logica"],
            "enunciado": "C(D) = L(D) = K(D) = Real(D) = 1 ⇒ Tru(D) = 1 (Corolario TT.7.3: Las Cuatro Juntas son Suficientes).",
        },
        {
            "id": "TT.7.4",
            "tipo": "corolario",
            "sujeto": "Conf_n(φ)",
            "relacion": "no_implica",
            "objeto": "¬(A ⊨ φ)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["E3"],
            "gobierna": ["epistemologia"],
            "enunciado": "Conf_n(φ) ≠ ¬(A ⊨ φ). La confusión de un agente no constituye evidencia formal de la falsedad de la aserción (Corolario TT.7.4: Confusión no Implica Falsedad).",
        },
        {
            "id": "TT.7.5",
            "tipo": "corolario",
            "sujeto": "BETA",
            "relacion": "es_inevitable_en_sistemas_reales",
            "objeto": "ruido > 0",
            "polaridad": True,
            "cota": None,
            "depende_de": ["beta"],
            "gobierna": ["constantes"],
            "enunciado": "En cualquier sistema de observación real donde ruido > 0: β > 0 (Corolario TT.7.5: β es Inevitable en Sistemas Reales).",
        },
        {
            "id": "TT.11.1",
            "tipo": "teorema",
            "sujeto": "C(D)",
            "relacion": "no_implica",
            "objeto": "Real(D) = 1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TT.5.1", "TT.5.4"],
            "gobierna": ["logica"],
            "enunciado": "C(D) = 1 ⇏ Real(D) = 1. Una narrativa ficticia puede ser internamente consistente y sin embargo no referirse a nada real (Teorema TT.11.1: Independencia Parcial de Coherencia y Realidad).",
        },
        {
            "id": "TT.11.2",
            "tipo": "teorema",
            "sujeto": "C(D)",
            "relacion": "no_implica",
            "objeto": "K(D) = 1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TT.5.1", "TT.5.3"],
            "gobierna": ["logica"],
            "enunciado": "C(D) = 1 ⇏ K(D) = 1. Una descripción imaginaria puede no contener contradicciones y sin embargo no corresponder a ningún hecho observado (Teorema TT.11.2).",
        },
        {
            "id": "TT.11.3",
            "tipo": "teorema",
            "sujeto": "L(D)",
            "relacion": "no_implica",
            "objeto": "Real(D) = 1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TT.5.2", "TT.5.4"],
            "gobierna": ["logica"],
            "enunciado": "L(D) = 1 ⇏ Real(D) = 1. Un proceso completamente especificado puede no referirse a una entidad real (Teorema TT.11.3).",
        },
        {
            "id": "TT.11.4",
            "tipo": "teorema",
            "sujeto": "K(D)",
            "relacion": "no_implica",
            "objeto": "Tru(D) = 1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TT.5.3"],
            "gobierna": ["logica"],
            "enunciado": "K(D) = 1 ⇏ Tru(D) = 1. Una descripción puede alinearse con ciertos datos y sin embargo fallar en coherencia, lógica o realidad (Teorema TT.11.4).",
        },
        {
            "id": "TT.11.5",
            "tipo": "teorema",
            "sujeto": "R_i",
            "relacion": "no_es_igual_a",
            "objeto": "R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4"],
            "gobierna": ["ontologia", "logica"],
            "enunciado": "I(R; R_i) ≤ I(R; X) < I(R; R) = H(R). La lectura de R nunca recupera toda la información de R (Teorema TT.11.5: R_i ≠ R en General).",
        },
        {
            "id": "TT.12.1",
            "tipo": "teorema",
            "sujeto": "a * b * c * d",
            "relacion": "es_menor_o_igual_a",
            "objeto": "min{a, b, c, d}",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA5"],
            "gobierna": ["logica"],
            "enunciado": "a·b·c·d ≤ min{a, b, c, d} para a, b, c, d ∈ [0,1]. La verdad está dominada por la condición más débil (Teorema TT.12.1: Dominancia Mínima).",
        },
        {
            "id": "TT.13.1",
            "tipo": "teorema",
            "sujeto": "ruido",
            "relacion": "es_irreversible_a_partir_de",
            "objeto": "n* = 11",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T4"],
            "gobierna": ["epistemologia"],
            "enunciado": "Cuando C, L y K retroalimentan sus propios errores previos, existe un paso n* = 11 tal que para todo n ≥ n*, β es irreversible (Teorema TT.13.1: Irreversibilidad del Error).",
        },

        # ==========================================================
        # COROLARIOS (Def-5.3.1, β-Gödel, β-Private)
        # ==========================================================
        {
            "id": "Def-5.3.1",
            "tipo": "corolario",
            "sujeto": "K(D)",
            "relacion": "es_indefinido_sin",
            "objeto": "O_context",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA3"],
            "gobierna": ["logica", "epistemologia"],
            "enunciado": "K(D) es indefinido sin un O_context explícito. Sin O_context, K(D) = ∅ (no cero) (Corolario Def-5.3.1: Especificidad de Dominio).",
        },
        {
            "id": "beta-Godel",
            "tipo": "corolario",
            "sujeto": "BETA",
            "relacion": "explica",
            "objeto": "incompletud_de_Godel",
            "polaridad": True,
            "cota": None,
            "depende_de": ["beta", "E3"],
            "gobierna": ["epistemologia", "constantes"],
            "enunciado": "La incompletud de Gödel es una instancia de β en el dominio formal-lógico (Corolario β-Gödel).",
        },
        {
            "id": "beta-Private-1",
            "tipo": "corolario",
            "sujeto": "Tru(A1)|self",
            "relacion": "igual_a",
            "objeto": "1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T14"],
            "gobierna": ["epistemologia"],
            "enunciado": "Tru(A1)|self = 1. La experiencia privada de uno mismo es total (Corolario β-Private, Parte 1).",
        },
        {
            "id": "beta-Private-2",
            "tipo": "corolario",
            "sujeto": "Tru(A1)|other",
            "relacion": "es_menor_que",
            "objeto": "0.5",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T14"],
            "gobierna": ["epistemologia"],
            "enunciado": "Tru(A1)|other < 0.5. La experiencia privada de otros es parcial (Corolario β-Private, Parte 2).",
        },
        {
            "id": "beta-Private-3",
            "tipo": "corolario",
            "sujeto": "A2_indeterminado",
            "relacion": "es_mayor_que",
            "objeto": "A2_determinado",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T14"],
            "gobierna": ["epistemologia"],
            "enunciado": "El número de casos indeterminados (A2) es mayor que el de determinados (Corolario β-Private, Parte 3).",
        },
        {
            "id": "beta-Private-4",
            "tipo": "corolario",
            "sujeto": "invalid_implications",
            "relacion": "igual_a",
            "objeto": "total",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T14"],
            "gobierna": ["epistemologia"],
            "enunciado": "Todas las implicaciones son inválidas en algún contexto (Corolario β-Private, Parte 4).",
        },

        # ==========================================================
        # PRINCIPIOS GLOBALES (I-X)
        # ==========================================================
        {
            "id": "I",
            "tipo": "axioma",
            "sujeto": "Output(S, t)",
            "relacion": "es_subconjunto_de",
            "objeto": "S",
            "polaridad": True,
            "cota": None,
            "depende_de": [],
            "gobierna": ["ontologia"],
            "enunciado": "∀S, ∀t: Output(S, t) ⊆ S (Principio I: Cierre Causal).",
        },
        {
            "id": "II",
            "tipo": "axioma",
            "sujeto": "I(R;Y)",
            "relacion": "es_menor_o_igual_a",
            "objeto": "I(R;X)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T2"],
            "gobierna": ["informacion"],
            "enunciado": "I(R;Y) ≤ I(R;X). Ningún procesamiento interno excede la información contenida en la evidencia recibida (Principio II: Límite Informacional).",
        },
        {
            "id": "III",
            "tipo": "axioma",
            "sujeto": "Tru_Ri(D)",
            "relacion": "igual_a",
            "objeto": "C(D) * L(D) * K(D)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA5"],
            "gobierna": ["logica"],
            "enunciado": "Tru_Ri(D) = C(D) * L(D) * K(D) y Tru_total(D) = Tru_Ri(D) * α + β (Principio III: Multiplicatividad Estructural de la Verdad).",
        },
        {
            "id": "IV",
            "tipo": "axioma",
            "sujeto": "R",
            "relacion": "es_invariante_respecto_a",
            "objeto": "cualquier_observador_Ri",
            "polaridad": True,
            "cota": None,
            "depende_de": ["TA4"],
            "gobierna": ["ontologia"],
            "enunciado": "R no varía con ningún observador, R_i o consenso. El fallo siempre está en R_i, nunca en R (Principio IV: Invariancia de R).",
        },
        {
            "id": "V",
            "tipo": "axioma",
            "sujeto": "BETA",
            "relacion": "garantiza",
            "objeto": "R > 0",
            "polaridad": True,
            "cota": None,
            "depende_de": ["beta"],
            "gobierna": ["constantes"],
            "enunciado": "β = 1/27 garantiza que R > 0 en todo momento y para todo sistema en ℝ³ (Principio V: β como Ancla Estructural).",
        },
        {
            "id": "VI",
            "tipo": "axioma",
            "sujeto": "verdad",
            "relacion": "es_independiente_de",
            "objeto": "verificacion_y_confusion",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T6", "T7"],
            "gobierna": ["logica"],
            "enunciado": "Verdad, demostrabilidad y confusión epistémica son formalmente independientes (Principio VI: Separación Estructural).",
        },
        {
            "id": "VII",
            "tipo": "axioma",
            "sujeto": "Tru(D)",
            "relacion": "igual_a_1_si",
            "objeto": "C(D) = L(D) = K(D) = 1",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T8"],
            "gobierna": ["logica"],
            "enunciado": "Tru(D) = 1 ⇔ C(D) = L(D) = K(D) = 1. La sincronización es alcanzable (Principio VII: Sincronización como Acceso a la Verdad).",
        },
        {
            "id": "VIII",
            "tipo": "axioma",
            "sujeto": "observadores_independientes",
            "relacion": "prueban",
            "objeto": "R",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T13"],
            "gobierna": ["epistemologia"],
            "enunciado": "Múltiples observadores con R_i distintos que producen Tru(D) = 1 para el mismo hecho D constituyen prueba formal de la independencia de R (Principio VIII: Convergencia como Prueba de R).",
        },
        {
            "id": "IX",
            "tipo": "axioma",
            "sujeto": "S_new",
            "relacion": "igual_a",
            "objeto": "g(I_prev)",
            "polaridad": True,
            "cota": None,
            "depende_de": ["T15"],
            "gobierna": ["meta"],
            "enunciado": "Todo conocimiento verificable es S_new = g(I_prev) aplicado con C(g) = 1 y K(g) > 0. La novedad es siempre epistémica, nunca ontológica (Principio IX: Emergencia Estructural como Mecanismo de Conocimiento).",
        },
        {
            "id": "X",
            "tipo": "axioma",
            "sujeto": "BETA",
            "relacion": "es_la_raiz_estructural_de",
            "objeto": "incompletud_formal",
            "polaridad": True,
            "cota": None,
            "depende_de": ["beta-Godel"],
            "gobierna": ["epistemologia", "constantes"],
            "enunciado": "β es la raíz estructural de la incompletud formal (Principio X: β como Raíz de la Incompletud de Gödel).",
        },
    ]

# ===============================================================
# FUNCIONES DE CARGA Y VALIDACIÓN
# ===============================================================

def _cargar(directorio: Path):
    init = directorio / "__init__.py"
    if not init.exists():
        return None, "sin __init__.py"
    nombre_mod = f"vpsi_{directorio.name}"
    spec = importlib.util.spec_from_file_location(nombre_mod, init)
    if spec is None or spec.loader is None:
        return None, "spec no construible"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre_mod] = mod
    spec.loader.exec_module(mod)
    meta = getattr(mod, "CUERPO", None)
    if not isinstance(meta, dict):
        return None, "falta el diccionario CUERPO"
    for k in ("nombre", "version"):
        if k not in meta:
            return None, f"CUERPO sin clave '{k}'"
    if not callable(getattr(mod, "declaraciones", None)):
        return None, "no expone declaraciones()"
    return mod, None

def cuerpos() -> Dict:
    cargados = {}
    rechazados = []
    for d in sorted(p for p in _DIR.iterdir() if p.is_dir()):
        if d.name.startswith(("_", ".")):
            continue
        try:
            mod, razon = _cargar(d)
        except Exception as e:
            rechazados.append({"cuerpo": d.name, "razon": f"{type(e).__name__}: {e}"})
            continue
        if mod is None:
            rechazados.append({"cuerpo": d.name, "razon": razon})
            continue
        n = mod.CUERPO["nombre"]
        if n in cargados:
            rechazados.append({"cuerpo": d.name, "razon": f"nombre duplicado: {n}"})
            continue
        cargados[n] = mod
    return cargados, rechazados

def recolectar() -> List[Dict]:
    decls = []
    errores = []
    # Cargar declaraciones internas (este mismo módulo)
    try:
        decls.extend(declaraciones())
    except Exception as e:
        errores.append({"cuerpo": "VPSI", "razon": f"declaraciones() levantó {type(e).__name__}: {e}"})
    # Cargar declaraciones de cuerpos externos (si los hay)
    cargados, rechazados = cuerpos()
    for n, mod in cargados.items():
        try:
            lista = mod.declaraciones()
        except Exception as e:
            errores.append({"cuerpo": n, "razon": f"declaraciones() levantó {type(e).__name__}: {e}"})
            continue
        if not isinstance(lista, list):
            errores.append({"cuerpo": n, "razon": "declaraciones() no devolvió lista"})
            continue
        for d in lista:
            try:
                decls.append(normalizar(d, n))
            except ValueError as e:
                errores.append({"cuerpo": n, "razon": str(e)})
    return decls, errores

def contradiccion_directa(decls: List[Dict]) -> List[Dict]:
    grupos = {}
    for d in decls:
        grupos.setdefault(clave(d), []).append(d)
    choques = []
    for k, grupo in grupos.items():
        afirman = [d for d in grupo if d["polaridad"]]
        niegan = [d for d in grupo if not d["polaridad"]]
        for a in afirman:
            for n in niegan:
                choques.append({
                    "tipo": "contradiccion_directa",
                    "tripleta": " ".join(k),
                    "afirma": ref(a),
                    "afirma_tipo": a["tipo"],
                    "niega": ref(n),
                    "niega_tipo": n["tipo"],
                    "enunciado_afirma": a["enunciado"],
                    "enunciado_niega": n["enunciado"],
                })
    return choques

def contradiccion_de_cota(decls: List[Dict]) -> List[Dict]:
    grupos = {}
    for d in decls:
        if d["cota"] is None:
            continue
        grupos.setdefault(
            (d["sujeto"].lower().strip(), d["relacion"].lower().strip()), []
        ).append(d)
    choques = []
    for (suj, rel), grupo in grupos.items():
        porcota = {}
        for d in grupo:
            porcota.setdefault(d["cota"], []).append(ref(d))
        if len(porcota) > 1:
            choques.append({
                "tipo": "contradiccion_de_cota",
                "sujeto": suj,
                "relacion": rel,
                "cotas": porcota,
            })
    return choques

def sin_gobernar(decls: List[Dict], modulos_presentes: List[str]) -> List[Dict]:
    presentes = set(modulos_presentes or ())
    huerfanos = []
    for d in decls:
        if not d["gobierna"]:
            continue
        ausentes = [m for m in d["gobierna"] if m not in presentes]
        if ausentes:
            huerfanos.append({
                "declaracion": ref(d),
                "tipo": d["tipo"],
                "gobernantes_ausentes": ausentes,
            })
    return huerfanos

def barrer(declaraciones_externas: Dict[str, List[Dict]] = None) -> Dict:
    decls, errores = recolectar()
    modulos = ["VPSI"]  # Este módulo siempre está presente
    if declaraciones_externas:
        for nombre, lista in declaraciones_externas.items():
            modulos.append(nombre)
            if not isinstance(lista, list):
                errores.append({"cuerpo": nombre, "razon": "declaración externa no es lista"})
                continue
            for d in lista:
                try:
                    decls.append(normalizar(d, nombre))
                except ValueError as e:
                    errores.append({"cuerpo": nombre, "razon": str(e)})
    choques = contradiccion_directa(decls) + contradiccion_de_cota(decls)
    return {
        "coherente": not (choques or errores),
        "choques": choques,
        "errores": errores,
        "aplicacion": sin_gobernar(decls, modulos),
        "declaraciones": len(decls),
        "cuerpos": sorted({d["cuerpo"] for d in decls}),
        "por_tipo": {t: sum(1 for d in decls if d["tipo"] == t) for t in TIPOS},
    }

def inventario() -> Dict:
    cargados, rechazados = cuerpos()
    decls, errores = recolectar()
    return {
        "contenedor": CONTENEDOR["nombre"],
        "version": CONTENEDOR["version"],
        "tipos": list(TIPOS),
        "cuerpos": {
            "VPSI": {
                "version": CONTENEDOR["version"],
                "por_tipo": {t: sum(1 for d in decls if d["cuerpo"] == "VPSI" and d["tipo"] == t) for t in TIPOS},
            },
            **{
                n: {
                    "version": m.CUERPO["version"],
                    "por_tipo": {t: sum(1 for d in decls if d["cuerpo"] == n and d["tipo"] == t) for t in TIPOS},
                }
                for n, m in cargados.items()
            }
        },
        "rechazados": rechazados,
        "errores": errores,
        "vigila": ["contradiccion_directa", "contradiccion_de_cota"],
    }

__all__ = [
    "CONTENEDOR", "AXIOMA", "LEMA", "TEOREMA", "COROLARIO", "TIPOS",
    "normalizar", "clave", "ref",
    "declaraciones", "cuerpos", "recolectar",
    "contradiccion_directa", "contradiccion_de_cota",
    "sin_gobernar", "barrer", "inventario",
]
