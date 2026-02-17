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
    return random.choice(werte) + random.choice(farben)


def karte_wert(karte):
    return karten_wert[karte[:-1]]


def deck_erstellen(decks):
    deck = [neue_karte() for _ in range(decks * 52)]
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


def simulation(
        haende=1000,
        decks=6,
        penetration=0.75,
        count_aktiv=False,
        seed=None):

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    deck = deck_erstellen(decks)

    kapital = 1000
    running_count = 0

    ergebnisse = []
    kapital_verlauf = []

    for _ in range(haende):

        if len(deck) < int(52 * decks * (1 - penetration)):
            deck = deck_erstellen(decks)
            running_count = 0

        verbleibende_decks = max(len(deck) / 52, 1)
        true_count = running_count / verbleibende_decks

        einsatz = 1

        if count_aktiv:
            if true_count > 2:
                einsatz = 4
            if true_count > 4:
                einsatz = 8

        spieler = [deck.pop(), deck.pop()]
        dealer = [deck.pop(), deck.pop()]

        for k in spieler + dealer:
            running_count += hi_lo_wert(k)

        spieler_wert = hand_wert(spieler)
        dealer_wert = hand_wert(dealer)

        # Blackjack Auszahlung 3:2
        if spieler_wert == 21 and len(spieler) == 2:
            if dealer_wert == 21:
                gewinn = 0
            else:
                gewinn = 1.5 * einsatz

        else:

            while einfache_strategie(spieler):
                karte = deck.pop()
                spieler.append(karte)
                running_count += hi_lo_wert(karte)

            spieler_wert = hand_wert(spieler)

            while dealer_wert < 17:
                karte = deck.pop()
                dealer.append(karte)
                running_count += hi_lo_wert(karte)
                dealer_wert = hand_wert(dealer)

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

    ergebnisse = np.array(ergebnisse)

    return {
        "mittelwert": float(np.mean(ergebnisse)),
        "std": float(np.std(ergebnisse)),
        "endkapital": float(kapital),
        "kapital_verlauf": kapital_verlauf,
        "ergebnisse": ergebnisse.tolist()
    }
