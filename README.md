# Intéressement and Plan Epargne Entreprise (PEE) analysis

[Python notebook](./pee.ipynb) to simulate the placement of a "prime d'intéressement" in different PEE funds or in other saving forms.

## Setup

```sh
python3.14 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

## Update the data

The PEE fund prices (from the Crédit Mutuel AM website) and the Livret A rates (Banque de France
series, through [DBnomics](https://db.nomics.world/BDF/MIR1/M.FR.B.L23FRLA.D.R.A.2230U6.EUR.O)) in
`data/` can be refreshed with:

```sh
./.venv/bin/python update_data.py
```

The ETF prices are still updated manually.
