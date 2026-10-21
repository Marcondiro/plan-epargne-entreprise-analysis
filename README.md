# Intéressement and Plan Epargne Entreprise (PEE) analysis

[Python notebook](./pee.ipynb) to simulate the placement of a "prime d'intéressement" in different PEE funds or in other saving forms.

## Setup

```sh
python3.14 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

## Update the data

The PEE fund prices in `data/` can be refreshed from the Crédit Mutuel AM website:

```sh
./.venv/bin/python update_data.py
```

The Livret A rates and the ETF prices are still updated manually.
