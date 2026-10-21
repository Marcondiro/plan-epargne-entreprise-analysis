"""Constants related to taxes and fiscal rules for 2026"""

# Each bracket starts where the previous one ends, so that no part of the income is left out
BAREME_IMPOT_REVENU: list[tuple[int, int, float]] = [
    (0, 11497, 0.00),
    (11497, 29315, 0.11),
    (29315, 83823, 0.30),
    (83823, 180294, 0.41),
    (180294, pow(2, 64) - 1, 0.45)
]

CRDS = 0.5 / 100
CSG = 9.2 / 100
CSG_DEDUCTIBLE = 6.8 / 100

PRIME_TAX_EXEMPTION_LIMIT = 36045

PRELEVEMENT_SOCIAUX = 18.6 / 100
