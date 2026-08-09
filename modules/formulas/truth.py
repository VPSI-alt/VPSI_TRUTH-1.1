"""
Fórmula de la Verdad (VPSI v9.4).

Definiciones canónicas:
    Tru_Ri(D)    = C(D) * L(D) * K(D)
    Tru_total(D) = (Tru_Ri(D) * ALPHA) + BETA

Donde:
    - ALPHA = 26/27 (fracción observable del cubo 3×3×3)
    - BETA  = 1/27  (fracción interior irreducible del cubo 3×3×3)
    - Tru_Ri: Contribución del observador (R_i).
    - Tru_total: Verdad total, incluyendo el piso estructural β.

Fuente: Teorema de la Verdad, VPSI v9.4 (Sección 2.14, Definición 2.14).
"""

from fractions import Fraction
from modules.constante import ALPHA, BETA

# Metadatos de la fórmula
FORMULA = {
    "nombre": "verdad",
    "expresion": "Tru_total(D) = (C(D) * L(D) * K(D) * ALPHA) + BETA",
    "fuente": "Teorema de la Verdad, VPSI v9.4",
    "nota": "Tru_Ri(D) = C(D) * L(D) * K(D) (sin límites artificiales).",
}


def _exigir_fraction(valor, nombre: str) -> Fraction:
    """Exige que el valor sea Fraction. Rechaza float y otros tipos."""
    if not isinstance(valor, Fraction):
        raise TypeError(
            f"{nombre} debe ser Fraction, se recibió {type(valor).__name__}"
        )
    return valor


def tru_ri(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    """
    Calcula la contribución del observador (Tru_Ri).

    Fórmula:
        Tru_Ri(D) = C(D) * L(D) * K(D)

    Parámetros:
        C (Fraction): Coherencia interna de la descripción D.
        L (Fraction): Lógica estructural de la descripción D.
        K (Fraction): Correlación con el dominio observado O.

    Retorna:
        Fraction: Valor de Tru_Ri(D) en el rango [0, 1].
    """
    C = _exigir_fraction(C, "C")
    L = _exigir_fraction(L, "L")
    K = _exigir_fraction(K, "K")
    return C * L * K


def tru_total(C: Fraction, L: Fraction, K: Fraction) -> Fraction:
    """
    Calcula la verdad total (Tru_total) según la fórmula canónica del framework VPSI.

    Fórmula:
        Tru_total(D) = (Tru_Ri(D) * ALPHA) + BETA
                     = (C(D) * L(D) * K(D) * ALPHA) + BETA

    Parámetros:
        C (Fraction): Coherencia interna de la descripción D.
        L (Fraction): Lógica estructural de la descripción D.
        K (Fraction): Correlación con el dominio observado O.

    Retorna:
        Fraction: Valor de Tru_total(D) en el rango [β, 1], donde β = 1/27.
    """
    C = _exigir_fraction(C, "C")
    L = _exigir_fraction(L, "L")
    K = _exigir_fraction(K, "K")
    return (C * L * K * ALPHA) + BETA
