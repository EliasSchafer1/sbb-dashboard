import streamlit as st
import pandas as pd
import json
from main import trains_df, stations_df
from layout import sbb_header

#display sbb header
sbb_header("Modify the Dataframe")

#-------------------------
#   helper methods
#-------------------------

#return true if it is a valid name for a line
def validate_strecke_bezeichnung(strecke_bezeichnung):
    if(len(strecke_bezeichnung)<2):
        return False, "Streckenbezeichnung muss mindestens 2 Buchstaben haben."
    if('.' in strecke_bezeichnung):
        return False, "Streckenbezeichnung darf keine Sonderzeichen enthalten." 
    return True, ""

#return true if it is a valid abschnitt
def validate_abschnitt(station_from, station_to):
    if station_from == station_to:
        return False, "Anfangs- und Endstation müssen verschieden sein."
    return True, ""

#display a success dialog when the new data was entered into the df
@st.dialog("New Train Line Added")
def success_dialog():
    st.write("Success! The new row was added to the dataframe.")
    last_row = trains_df.tail(1).copy()
    last_row["verbindung"] = last_row["verbindung"].astype(str)
    st.dataframe(last_row)
    if st.button('OK'):
        st.rerun()



#---------------------------------------
# display the fields to enter the data
#---------------------------------------

#header
st.subheader("Here you can input additional data into the dataframe.")

#specify the name of the line
strecke_bezeichnung = st.text_input('Strecke Bezeichnung', placeholder = "Solothurn - Olten")
if strecke_bezeichnung: 
    is_valid, message = validate_strecke_bezeichnung(strecke_bezeichnung=strecke_bezeichnung)
    if not is_valid:
        st.error(message)

#first row in the form: specify the line start and endpoints
col11, col12 = st.columns(2)
with col11:
    station_from = st.selectbox("Abschnitt von", stations_df)
    station_from_row = stations_df[stations_df["station"] == station_from]

with col12:
    station_to = st.selectbox("Abschnitt bis", stations_df)
    station_to_row = stations_df[stations_df["station"] == station_to]

if station_from and station_to:
    is_valid, message = validate_abschnitt(station_from, station_to)
    if not is_valid:
        st.error(message)

#second row in the form: month
monat = int(st.selectbox("Monat", list(range(1, 13))))

col31, col32 = st.columns(2)
#third row in the form: number of trains
with col31:
    dtv_p = st.number_input('Anzahl Personenverkehrszüge', min_value = 0)
with col32:
    dtv_g = st.number_input('Anzahl Güterverkehrszüge', min_value = 0)

#fourth row in the form: number of trains in the year before
hat_vorjahresmonat = st.checkbox("Vorjahresdaten vorhanden")
col41, col42 = st.columns(2)
with col41:
    dtv_p_vorjahr = st.number_input('Anzahl Personenerkehrszüge im Vorjahresmonat', min_value = 0, disabled = not hat_vorjahresmonat)
with col42:
    dtv_g_vorjahr = st.number_input('Anzahl Güterverkehrszüge im Vorjahresmonat', min_value = 0, disabled = not hat_vorjahresmonat)


#-------------------------------------------------------------------
# submit process + add to dataframe (should be split up probably)
#--------------------------------------------------------------------

if st.button("Submit"):
    #validate all fields
    validations = [
        validate_strecke_bezeichnung(strecke_bezeichnung),
        validate_abschnitt(station_from, station_to),
    ]
    if all(v[0] for v in validations):

        bezugsmonat = monat

        if(hat_vorjahresmonat):
            dtv_vorjahr = dtv_p_vorjahr + dtv_g_vorjahr
        else:
            dtv_p_vorjahr = pd.NA
            dtv_g_vorjahr = pd.NA
            dtv_vorjahr = pd.NA

        #arrays with the coordinates
        station_to_coordinates = [float(station_to_row.iloc[0]["longitude"]), float(station_to_row.iloc[0]["latitude"])]
        station_from_coordinates = [float(station_from_row.iloc[0]["longitude"]), float(station_from_row.iloc[0]["latitude"])]

        new_row = {"strecke_bezeichnung": strecke_bezeichnung,
                "abschnitt": "{} – {}".format(station_from, station_to),
                "abschnitt_von": station_from_row.iloc[0]["label"],
                "abschnitt_bis": station_to_row.iloc[0]["label"],
                "bezugsmonat": bezugsmonat,
                "dtv_bezugsmonat": dtv_p + dtv_g,
                "dtv_p_bezugsmonat": dtv_p,
                "dtv_g_bezugsmonat": dtv_g,
                "dtv_vorjahresmonat": dtv_vorjahr,
                "dtv_p_vorjahresmonat": dtv_p_vorjahr,
                "dtv_g_vorjahresmonat": dtv_g_vorjahr,
                "hat_vorjahresmonat": hat_vorjahresmonat,
                "verbindung": json.dumps({
                    "coordinates": [station_from_coordinates, station_to_coordinates], 
                    "type": "LineString"
                    })
                }
        
        trains_df = pd.concat([trains_df, pd.DataFrame([new_row])], ignore_index = True)
        trains_df = trains_df.convert_dtypes()
        st.session_state.trains_df = trains_df
        success_dialog()
    else:
        #show all error messages
        for valid, message in validations:
            if not valid:
                st.error(message)