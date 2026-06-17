# sbb-trains-per-route

Interactive EDA dashboard for average daily train frequencies across SBB route sections by month (2024–2025)

## Requirements

- Python 3.11+
- Poetry

## Setup

### 1. Set up the python version (e.g. via pyenv): 
```
pyenv install 3.11.8
pyenv local 3.11.8
```

### 2. Clone repository:
```
git clone https://github.com/python-data-science-2026/sbb-trains-per-route.git
cd sbb-trains-per-route
```

### 3. Install dependencies:
```
poetry install
```

### 4. Run the project:
```
poetry run streamlit run src/main.py
```

## Example usage

1. Go to the Explore tab.
2. Scroll to the graph “Comparison of Train Traffic in 2024 and 2025”.
3. Select the route sections:
   * Gotthard Nord (Spw) – Airolo
   * Rynächt (Abzw) – Sedrun SMF
4. Compare the traffic patterns of both route sections.

You will observe that the traffic patterns of these two sections are strongly complementary, with a clear shift around late summer 2024.

This is due to the reopening of the Gotthard Base Tunnel, which restored the normal routing between Rynächt and Sedrun and shifted traffic away from the alternative corridor via Airolo.


## Data

Data source: SBB Infrastruktur – "Züge pro Streckenabschnitt und Monat"  
Available at: https://data.sbb.ch/explore/dataset/zugzahlen_pro_monat/information/  
License: Open use, source must be provided  
Data status: April 2026

## Group Members

* Nora Lüthi
* Elias Schafer
* Jasmin Studer