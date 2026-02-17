import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from simulation import simulation

st.title("Blackjack Simulation — Einfluss von Kartenzählen")

st.write("""
Diese Simulation zeigt:

• durchschnittlichen Gewinn oder Verlust  
• Risiko durch Schwankungen  
• Unterschied zwischen Spielen mit und ohne Kartenzählen  

Ziel: Verstehen, ob Kartenzählen wirklich einen Vorteil bringt.
""")

st.sidebar.header("Einstellungen")

haende = st.sidebar.number_input(
    "Anzahl Hände",
    100, 100000, 1000, 100
)

decks = st.sidebar.slider("Anzahl Decks", 1, 8, 6)

penetration = st.sidebar.slider(
    "Penetration (wie tief gespielt wird)",
    0.5, 0.95, 0.75
)

seed = st.sidebar.number_input(
    "Zufalls-Seed (optional)",
    0, 100000, 42
)

if st.button("Simulation starten"):

    ohne = simulation(haende, decks, penetration, False, seed)
    mit = simulation(haende, decks, penetration, True, seed)

    st.subheader("Ergebnisse")

    vorteil = mit["mittelwert"] - ohne["mittelwert"]

    col1, col2 = st.columns(2)

    with col1:
        st.write("Ohne Kartenzählen")
        st.write(f"Durchschnitt: {ohne['mittelwert']:.4f}")
        st.write(f"Endkapital: {ohne['endkapital']:.2f}")

    with col2:
        st.write("Mit Kartenzählen")
        st.write(f"Durchschnitt: {mit['mittelwert']:.4f}")
        st.write(f"Endkapital: {mit['endkapital']:.2f}")

    st.subheader("Vorteil durch Kartenzählen")

    st.write(f"Unterschied Erwartungswert: {vorteil:.4f} pro Hand")

    # Kapitalverlauf
    st.subheader("Kapitalverlauf")

    fig, ax = plt.subplots()

    ax.plot(ohne["kapital_verlauf"], label="Ohne Kartenzählen")
    ax.plot(mit["kapital_verlauf"], label="Mit Kartenzählen")

    ax.set_xlabel("Gespielte Hände")
    ax.set_ylabel("Kapital")
    ax.legend()

    st.pyplot(fig)

    # Histogramm
    st.subheader("Verteilung der Gewinne")

    fig2, ax2 = plt.subplots()

    ax2.hist(ohne["ergebnisse"], bins=30, alpha=0.5, label="Ohne")
    ax2.hist(mit["ergebnisse"], bins=30, alpha=0.5, label="Mit")

    ax2.legend()

    st.pyplot(fig2)

    # CSV Export
    df = pd.DataFrame({
        "ohne_kartenzählen": ohne["ergebnisse"],
        "mit_kartenzählen": mit["ergebnisse"]
    })

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Ergebnisse als CSV herunterladen",
        csv,
        "simulation.csv",
        "text/csv"
    )

    st.info("""
Interpretation:

Negativer Durchschnitt → Casino hat Vorteil  
Positiver Durchschnitt → Spieler hat Vorteil  

Kartenzählen verändert Wahrscheinlichkeiten,
aber kurzfristige Schwankungen bleiben groß.
""")
