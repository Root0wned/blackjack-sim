import random
import numpy as np

farben = ["♠", "♥", "♦", "♣"]
werte = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "B", "D", "K", "A"]

karten_wert = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10,
    "B": 10, "D": 10, "K": 10, "A": 11
}


def neue_karte():
    wert = random.choice(werte)
    farbe = random.choice(farben)
    return wert + farbe


def karte_wert(karte):
    return karten_wert[karte[:-1]]


def deck_erstellen(anzahl_decks):
    deck = []
    for _ in range(anzahl_decks * 52):
        deck.append(neue_karte())
    random.shuffle(deck)
    return deck


def hand_wert(hand):

    wert = sum(karte_wert(k) for k in hand)
    asse = sum(1 for k in hand if k.startswith("A"))

    while wert > 21 and asse > 0:
        wert -= 10
        asse -= 1

    return wert


def hi_lo_wert(karte):
    rang = karte[:-1]

    if rang in ["2", "3", "4", "5", "6"]:
        return 1
    elif rang in ["10", "B", "D", "K", "A"]:
        return -1
    return 0


def einfache_strategie(hand):
    return hand_wert(hand) < 17


def simulation_starten(
        haende=50000,
        decks=6,
        penetration=0.75,
        count_aktiv=False):

    deck = deck_erstellen(decks)

    startkapital = 1000
    kapital = startkapital

    ergebnisse = []
    kapital_verlauf = []

    running_count = 0

    for _ in range(haende):

        if len(deck) < int(52 * decks * (1 - penetration)):
            deck = deck_erstellen(decks)
            running_count = 0

        # True Count
        verbleibende_decks = max(len(deck) / 52, 1)
        true_count = running_count / verbleibende_decks

        einsatz = 1

        if count_aktiv:
            if true_count > 2:
                einsatz = 4
            if true_count > 4:
                einsatz = 8

        # Karten austeilen
        spieler = [deck.pop(), deck.pop()]
        dealer = [deck.pop(), deck.pop()]

        for k in spieler + dealer:
            running_count += hi_lo_wert(k)

        # Blackjack prüfen
        spieler_wert = hand_wert(spieler)
        dealer_wert = hand_wert(dealer)

        if spieler_wert == 21 and len(spieler) == 2:
            if dealer_wert == 21:
                gewinn = 0
            else:
                gewinn = 1.5 * einsatz
        else:

            # Spieler spielt
            while einfache_strategie(spieler):
                karte = deck.pop()
                spieler.append(karte)
                running_count += hi_lo_wert(karte)

            spieler_wert = hand_wert(spieler)

            # Dealer spielt
            while dealer_wert < 17:
                karte = deck.pop()
                dealer.append(karte)
                running_count += hi_lo_wert(karte)
                dealer_wert = hand_wert(dealer)

            # Ergebnis
            if spieler_wert > 21:
                gewinn = -einsatz
            elif dealer_wert > 21 or spieler_wert > dealer_wert:
                gewinn = einsatz
            elif spieler_wert < dealer_wert:
                gewinn = -einsatz
            else:
                gewinn = 0

        kapital += gewinn

        ergebnisse.append(gewinn)
        kapital_verlauf.append(kapital)

    mittelwert = np.mean(ergebnisse)
    std = np.std(ergebnisse)

    return {
        "mittelwert": mittelwert,
        "std": std,
        "endkapital": kapital,
        "kapital_verlauf": kapital_verlauf
    }
