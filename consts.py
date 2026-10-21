"""Constants related to taxes and fiscal rules for 2026"""

# Each bracket starts where the previous one ends, so that no part of the income is left out
BAREME_IMPOT_REVENU: list[tuple[int, int, float]] = [
    (0, 11600, 0.00),
    (11600, 29579, 0.11),
    (29579, 84577, 0.30),
    (84577, 181917, 0.41),
    (181917, pow(2, 64) - 1, 0.45)
]

CRDS = 0.5 / 100
CSG = 9.2 / 100
CSG_DEDUCTIBLE = 6.8 / 100

PRIME_TAX_EXEMPTION_LIMIT = 36045

PRELEVEMENT_SOCIAUX = 18.6 / 100
