"""Constants related to taxes and fiscal rules for 2026"""

BAREME_IMPOT_REVENU: list[tuple[int, int, float]] = [
    (0, 11497, 0.00),
    (11498, 29315, 0.11),
    (29316, 83823, 0.30),
    (83824, 180294, 0.41),
    (180295, pow(2, 64) - 1, 0.45)
]

CRDS = 0.5 / 100
CSG = 9.2 / 100
CSG_DEDUCTIBLE = 6.8 / 100

PRIME_TAX_EXEMPTION_LIMIT = 36045

PRELEVEMENT_SOCIAUX = 18.6 / 100
