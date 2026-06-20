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

1. Open the Explore tab.
2. In the "Monthly train traffic" view:
   - Select the route sections:
     • Gotthard Nord (Spw) – Airolo
     • Rynächt (Abzw) – Sedrun SMF
   - Set Train type to "Passenger trains"
   - Keep Year, Aggregation and Smoothing at their default settings
3. Compare the monthly traffic patterns of the selected route sections.

You will observe that the traffic patterns of these two sections are strongly complementary, with a clear shift around late summer 2024.

This is due to the reopening of the Gotthard Base Tunnel, which restored the normal routing between Rynächt and Sedrun and shifted traffic away from the alternative route via Airolo.


## Data

Data source: SBB Infrastruktur – "Züge pro Streckenabschnitt und Monat"  
Available at: https://data.sbb.ch/explore/dataset/zugzahlen_pro_monat/information/  
License: Open use, source must be provided  
Data status: April 2026

## Group Members

* Nora Lüthi
* Elias Schafer
* Jasmin Studer