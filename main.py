import sys
from collections import deque
from random import shuffle

class Card:
    def __init__(self, color: str, num: str) -> None:
        self.color: str = color
        self.num: str = num
        self.card = self.color + self.num

        self.value: int = int(self.num) if self.num not in "JQKA" else 10

    def __str__(self):
        return f"{self.card}"

    def __repr__(self):
        return f"Card({self.color}, {self.num})"



class Deck:
    def __init__(self):
        self.deck = deque()

    def populate(self, num_of_decks: int) -> None:

        deck = [Card(color, str(num)) for color in "hcds" for num in range(2, 11)] \
                + [Card(color, num) for color in "hcds" for num in "JQKA"]

        deck = deck * num_of_decks

        shuffle(deck)

        for card in deck:
            self.deck.append(card)

    def pop(self):
        return self.deck.pop()

class Game:
    def __init__(self):
        self.cash = 1000
        self.bet_value = 10
        self.num_of_decks = 1
        self.split = True
        self.insurance = True
        self.double = True

    def main_loop(self):
        welcome_msg = """Welcome to BlackJack!
        N - New Game
        L - Load Game
        S - Settings
        Q - Quit
        """

        menu_choices = {
            "N": self.new_game,
            "L": self.load_game,
            "S": self.settings,
            "Q": sys.exit
        }

        while True:
            print(welcome_msg)
            usr_input = input("Type a letter: ").capitalize()

            choice = menu_choices.get(usr_input)
            if choice:
                choice()
            else:
                print("Wrong input")

    def new_game(self):
        deck = Deck()
        deck.populate(self.num_of_decks)

        dealer_cards = [deck.pop(), deck.pop()]
        player_cards = [deck.pop(), deck.pop()]

        dealer_string = f"{dealer_cards[0]} **"
        player_string = f"{player_cards[0]} {player_cards[1]}"

        self.cash -= self.bet_value

        cash_string = f"Cash: {self.cash}"
        bet_string = f"Bet: {self.bet_value}"

        print("New game!")

        while True:

            print(dealer_string)
            print(bet_string)
            print(player_string)
            print(cash_string)
            decision = input("Decision: H - hit; K - keep; D - double; S - split; SAVE - save; BACK - menu\n").upper()

            if decision == "BACK":
                break
            elif decision == "H":
                player_cards.append(deck.pop())
                player_string += f" {player_cards[-1]}"
            elif decision == "K":
                ...
            elif decision == "D":
                self.cash -= self.bet_value
                cash_string = f"Cash: {self.cash}"
                bet_string = f"Bet: {self.bet * 2}"
            elif decision == "S":
                ...
            elif decision == "SAVE":
                ...
            else:
                print("wrong input!")

    def load_game(self):
        print("Load game!")
    def settings(self):
        settings_msg = f"""Settings
        C - cash (current: {self.cash})
        B - bet (current: {self.bet})
        N - num_of_decks (current: {self.num_of_decks})
        S - split (current: {self.split})
        I - insurance (current: {self.insurance})
        D - double (current: {self.double})
        Enter - go back
        """
        print(settings_msg)


game = Game()
game.main_loop()
