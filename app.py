import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from simulation import simulation


st.set_page_config(page_title="Blackjack Simulation", layout="centered")
st.title("Blackjack Simulation — Kartenzählen")

st.sidebar.header("Einstellungen")

haende = st.sidebar.number_input("Anzahl Hände", min_value=100, max_value=100000, value=1000, step=100)
decks = st.sidebar.slider("Anzahl Decks", min_value=1, max_value=8, value=6)
penetration = st.sidebar.slider("Penetration", min_value=0.50, max_value=0.95, value=0.75, step=0.01)
seed = st.sidebar.number_input("Zufalls-Seed", min_value=0, max_value=100000, value=42, step=1)

if st.button("Simulation starten"):
    ohne = simulation(haende=haende, decks=decks, penetration=penetration, count_aktiv=False, seed=seed)
    mit = simulation(haende=haende, decks=decks, penetration=penetration, count_aktiv=True, seed=seed)

    vorteil = mit["mittelwert"] - ohne["mittelwert"]

    st.subheader("Ergebnisse")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Ohne Kartenzählen**")
        st.write(f"Ø Gewinn pro Hand: `{ohne['mittelwert']:.4f}`")
        st.write(f"Standardabweichung: `{ohne['std']:.4f}`")
        st.write(f"Endkapital: `{ohne['endkapital']:.2f}`")

    with col2:
        st.write("**Mit Kartenzählen (Hi-Lo)**")
        st.write(f"Ø Gewinn pro Hand: `{mit['mittelwert']:.4f}`")
        st.write(f"Standardabweichung: `{mit['std']:.4f}`")
        st.write(f"Endkapital: `{mit['endkapital']:.2f}`")

    st.write(f"**Vorteil (Differenz Ø):** `{vorteil:.4f}` pro Hand")

    st.subheader("Kapitalverlauf")
    fig, ax = plt.subplots()
    ax.plot(ohne["kapital_verlauf"], label="Ohne Kartenzählen")
    ax.plot(mit["kapital_verlauf"], label="Mit Kartenzählen")
    ax.set_xlabel("Gespielte Hände")
    ax.set_ylabel("Kapital")
    ax.legend()
    st.pyplot(fig)

    st.subheader("Verteilung der Gewinne pro Hand")
    fig2, ax2 = plt.subplots()
    ax2.hist(ohne["ergebnisse"], bins=30, alpha=0.5, label="Ohne")
    ax2.hist(mit["ergebnisse"], bins=30, alpha=0.5, label="Mit")
    ax2.set_xlabel("Gewinn pro Hand (in Einsatz-Einheiten)")
    ax2.set_ylabel("Häufigkeit")
    ax2.legend()
    st.pyplot(fig2)

    df = pd.DataFrame({
        "ohne_kartenzaehlen": ohne["ergebnisse"],
        "mit_kartenzaehlen": mit["ergebnisse"]
    })

    st.download_button(
        "CSV herunterladen",
        df.to_csv(index=False).encode("utf-8"),
        file_name="simulation.csv",
        mime="text/csv"
    )
