# sbb-trains-per-route

**Datascience FS26 - Project 03**: A reporting tool for the average number of trains per day for each section of the route network and month.

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
poetry run streamlit run src/home.py
```

## Example usage

(To be updated, this is how the final version could look like)
1. Select "Zurich" as departure
2. Select "Bern" as arrival
3. View the number of trains per route displayed in the dashboard

## Data

Data source: SBB Infrastruktur – "Züge pro Streckenabschnitt und Monat"  
Available at: https://data.sbb.ch/explore/dataset/zugzahlen_pro_monat/information/  
License: Open use, source must be provided  
Data status: April 2026

## Group Members

* Lino Bucher
* Nora Lüthi
* Elias Schafer
* Jasmin Studer