import random
import numpy as np


def deck_erstellen(anzahl_decks):
    karten = []

    werte = [2,3,4,5,6,7,8,9,10,10,10,10,11]

    for _ in range(anzahl_decks * 4):
        karten.extend(werte)

    random.shuffle(karten)
    return karten


def hand_wert(hand):

    wert = sum(hand)

    asse = hand.count(11)

    while wert > 21 and asse > 0:
        wert -= 10
        asse -= 1

    return wert


def karte_ziehen(deck):
    return deck.pop()


def einfache_strategie(hand):
    return hand_wert(hand) < 17


def simulation_starten(haende, decks, penetration, count_aktiv):

    deck = deck_erstellen(decks)

    startkapital = 1000
    kapital = startkapital

    ergebnisse = []

    laufender_count = 0

    for _ in range(haende):

        if len(deck) < int(52 * decks * (1 - penetration)):
            deck = deck_erstellen(decks)
            laufender_count = 0

        # Einsatz
        einsatz = 1

        if count_aktiv:
            true_count = laufender_count / max(len(deck)/52, 1)
            if true_count > 2:
                einsatz = 4

        spieler = [karte_ziehen(deck), karte_ziehen(deck)]
        dealer = [karte_ziehen(deck), karte_ziehen(deck)]

        # Spieler spielt
        while einfache_strategie(spieler):
            spieler.append(karte_ziehen(deck))

        spieler_wert = hand_wert(spieler)
        dealer_wert = hand_wert(dealer)

        # Dealer spielt
        while dealer_wert < 17:
            dealer.append(karte_ziehen(deck))
            dealer_wert = hand_wert(dealer)

        gewinn = 0

        if spieler_wert > 21:
            gewinn = -einsatz
        elif dealer_wert > 21 or spieler_wert > dealer_wert:
            gewinn = einsatz
        elif spieler_wert < dealer_wert:
            gewinn = -einsatz

        kapital += gewinn
        ergebnisse.append(gewinn)

    mittelwert = np.mean(ergebnisse)
    std = np.std(ergebnisse)

    return {
        "mittelwert": mittelwert,
        "std": std,
        "endkapital": kapital
    }
