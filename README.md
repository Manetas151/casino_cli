# 🎲 Ultimate Pygame Casino & Multiplayer Poker

Ένα ολοκληρωμένο project ψηφιακού καζίνο φτιαγμένο με Python και Pygame. Το project ξεκίνησε ως ένα τοπικό παιχνίδι ενάντια στον Dealer, αλλά πλέον υποστηρίζει **πλήρες Multiplayer Texas Hold'em** μέσω αυτόνομου TCP Server, επιτρέποντας σε φίλους να συνδέονται και να παίζουν μαζί στο ίδιο τραπέζι.

## 🌟 Δυνατότητες Παιχνιδιού

*   **Multiplayer Texas Hold'em (Online/LAN):**
    *   Σύνδεση πολλών παικτών σε πραγματικό χρόνο (Client-Server αρχιτεκτονική).
    *   Πλήρες σύστημα γύρων (Preflop, Flop, Turn, River, Showdown).
    *   Μηχανισμοί για Fold, Check, Call και δυναμικά Raise.
    *   Υποστήριξη **All-In** και αυτόματου Fast-Forward αν τελειώσουν τα χρήματα των παικτών.
    *   Αυτόματη ανάδειξη νικητή στο Showdown, διάσπαση του Pot (Split Pot) στις ισοπαλίες και απομόνωση αποσυνδεδεμένων παικτών.
*   **Local Blackjack:** Παίξε κόντρα στον υπολογιστή με μηχανισμούς Hit, Stand, Double Down, Split και Insurance.
*   **Local Ultimate Texas Hold'em:** Γρήγορο παιχνίδι πόκερ ενάντια στον Dealer με Ante, Blind και Play bets.
*   **Γραφικά Pygame:** Προσαρμόσιμο παράθυρο (Resizable), ομαλά animations μοιράσματος καρτών και αυτοματοποιημένο UI.

## 🛠️ Απαιτήσεις και Εγκατάσταση

Για να τρέξεις το παιχνίδι, χρειάζεσαι την Python 3.x και τη βιβλιοθήκη `pygame`.

1. Κατέβασε ή κάνε clone το repository.
2. Τρέξε το αρχείο `run.bat` (στα Windows). Αυτό το script θα ελέγξει αυτόματα αν υπάρχει το `pygame` και θα το εγκαταστήσει αν λείπει, πριν ξεκινήσει το παιχνίδι.

Εναλλακτικά, από το τερματικό:
```bash
pip install pygame
python gui_main.py
