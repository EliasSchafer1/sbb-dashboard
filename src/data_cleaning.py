import pandas as pd
import matplotlib.pyplot as plt

def load_data():
    return pd.read_csv("data/zugzahlen_pro_monat.csv", sep=";")

def clean_data(df):
    # Make all columns lower case and remove any spaces
    df.columns = df.columns.str.strip().str.lower()
    
    # Drop column "isb", since it has always the value "SBB"
    df = df.drop(columns=["isb"])
    # Drop column "geo_point_2d", since it has an unknown meaning
    df = df.drop(columns=["geo_point_2d"])
    # Drop column "reihung", since it has no importance for our project
    df = df.drop(columns=["reihung"])
    
    # Convert to pandas datatypes
    df = df.convert_dtypes()

    # Change column "Bemerkung" to a boolean column "Hat_Vorjahresangaben",
    # because the only comment that exists is "Keine Angaben zum Vorjahr vorhanden. Mögliche Gründe: Baustellen, Unterbrüche oder Änderungen an der Streckentopologie."
    # or else it has a NaN-value
    df["hat_vorjahresmonat"] = df["bemerkung"].isna()
    df = df.drop(columns=["bemerkung"])

    # Splitting months into two different columns and converting to date_time
    df[["bezugsmonat", "vorjahresmonat"]] = df["bezugsmonat_vorjahresmonat"].str.split(" :: ", expand=True)
    df["bezugsmonat"] = pd.to_datetime(df["bezugsmonat"]).dt.to_period("M")
    df["vorjahresmonat"] = pd.to_datetime(df["vorjahresmonat"]).dt.to_period("M")
    df = df.drop(columns=["bezugsmonat_vorjahresmonat"])
    
    # Reorder the columns to get a meaningful order
    cols = [
        # Identification
        "strecke_bezeichnung",
        "abschnitt",
        "abschnitt_von",
        "abschnitt_bis",
        # Time
        "bezugsmonat",
        "vorjahresmonat",
        # Metrics
        "dtv_bezugsmonat",
        "dtv_vorjahresmonat",
        "dtv_p_bezugsmonat",
        "dtv_p_vorjahresmonat",
        "dtv_g_bezugsmonat",
        "dtv_g_vorjahresmonat",
        # Additional information
        "hat_vorjahresmonat",
        # Geo data
        "verbindung",
    ]
    df = df[cols]

    return df

if __name__ == "__main__":
    df = load_data()
    df_clean = clean_data(df)
    print(df_clean.head(5))