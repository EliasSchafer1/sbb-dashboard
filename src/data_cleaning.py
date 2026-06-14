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
    # Drop column "strecke_bezeichnung", because it also represents regional clusters (e.g. "Bern")
    # rather than only point-to-point connections, which could mislead users
    df = df.drop(columns=["strecke_bezeichnung"])
    
    # Convert to pandas datatypes
    df = df.convert_dtypes()

    # Change column "Bemerkung" to a boolean column "Hat_Vorjahresangaben",
    # because the only comment that exists is "Keine Angaben zum Vorjahr vorhanden. Mögliche Gründe: Baustellen, Unterbrüche oder Änderungen an der Streckentopologie."
    # or else it has a NaN-value
    df["hat_vorjahresmonat"] = df["bemerkung"].isna()
    df = df.drop(columns=["bemerkung"])

    # Splitting months into two different columns and converting to datetime
    df["bezugsmonat"] = pd.to_datetime(
        df["bezugsmonat_vorjahresmonat"].str.split(" :: ", expand=True)[0]
    )

    df["month_num"] = df["bezugsmonat"].dt.month

    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    df["bezugsmonat"] = pd.Categorical(
        df["bezugsmonat"].dt.month_name(),
        categories=month_order,
        ordered=True
    )

    df = df.drop(columns=["bezugsmonat_vorjahresmonat"])
    
    # Reorder the columns to get a meaningful order
    df = df[[
        # Identification
        "abschnitt",
        "abschnitt_von",
        "abschnitt_bis",
        # Time
        "bezugsmonat",
        "month_num",
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
    ]]

    # Rename columns to English
    df = df.rename(columns={
        "abschnitt": "section",
        "abschnitt_von": "section_from",
        "abschnitt_bis": "section_to",
        "bezugsmonat": "reference_month",
        "dtv_bezugsmonat": "dtv_reference_month",
        "dtv_vorjahresmonat": "dtv_previous_year_month",
        "dtv_p_bezugsmonat": "dtv_p_reference_month",
        "dtv_p_vorjahresmonat": "dtv_p_previous_year_month",
        "dtv_g_bezugsmonat": "dtv_g_reference_month",
        "dtv_g_vorjahresmonat": "dtv_g_previous_year_month",
        "hat_vorjahresmonat": "has_previous_year_month",
        "verbindung": "connection",
    })

    return df

if __name__ == "__main__":
    df = load_data()
    df_clean = clean_data(df)
    print(df_clean.head(5))