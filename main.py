import sys
from collections import deque
from random import shuffle
from typing import List


class Card:
    def __init__(self, color: str, num: str) -> None:
        self.color: str = color
        self.num: str = num
        self.card: str = self.color + self.num

        self.value: int = int(self.num) if self.num not in "JQKA" else 11 if self.num == "A" else 10

    def __str__(self) -> str:
        return f"{self.card}"

    def __repr__(self) -> str:
        return f"Card({self.color}, {self.num})"


class Hand:
    def __init__(self, game: "Game", player_cards: List) -> None:
        self.game = game

        self.player_cards = player_cards

        self.current_bet = self.game.bet_value  # current bet might be doubled
        self.game.cash -= self.current_bet

        self.blocked = False  # in order to deal with split

    def add_card(self, deck: "Deck") -> None:
        self.player_cards.append(deck.pop())

    def print_hand(self) -> None:

        print(f"Bet: {self.current_bet}")
        print(" ".join([str(c) for c in self.player_cards]))
        print(f"Cash: {self.game.cash}")


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

    def pop(self) -> Card:
        return self.deck.pop()


class Game:
    def __init__(self) -> None:
        self.cash = 1000
        self.bet_value = 10
        self.num_of_decks = 1
        self.split = True
        self.double = True

    def main_loop(self) -> None:
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

    def new_game(self) -> None:
        deck = Deck()
        deck.populate(self.num_of_decks)

        hand_stack = deque()

        dealer_cards = [deck.pop(), deck.pop()]
        player_cards = [deck.pop(), deck.pop()]

        hand_stack.append(Hand(self, player_cards))

        print("New game!")

        while True:
            try:
                current_hand = hand_stack.pop()
            except IndexError:
                try:
                    dealer_cards = [deck.pop(), deck.pop()]
                    player_cards = [deck.pop(), deck.pop()]

                    current_hand = Hand(self, player_cards)
                except IndexError:
                    print("Not enough cards in the deck! The game is over :)")
                    return

            # handle case when split or split and then doubled:
            # borderline (all hands blocked) -> it's time to open dealers hand:
            if current_hand.blocked and (len(hand_stack) == 0 or all([h.blocked for h in hand_stack])):
                decision = "K"
            # there are still hands with decisions to make:
            elif current_hand.blocked:
                hand_stack.appendleft(current_hand)
                continue
            # regular case:
            else:
                self.print_dealers(dealer_cards)
                current_hand.print_hand()
                decision = input("Decision: H - hit; K - keep; D - double; S - split; SAVE - save; BACK - menu\n").upper()

            if decision == "BACK":
                return
            elif decision == "H":
                try:
                    current_hand.add_card(deck)
                    self.print_dealers(dealer_cards)
                    current_hand.print_hand()
                except IndexError:
                    print("Not enough cards in the deck! The game is over :)")
                    return

                current_points = self.calculate_hand(current_hand.player_cards)
                print(current_points)

                if current_points > 21:
                    self.print_dealers(dealer_cards, show_off=True)
                    current_hand.print_hand()
                    print("Hand over 21. Hand lost.")
                else:
                    hand_stack.appendleft(current_hand)

            elif decision == "K":
                if not current_hand.blocked:  # block if not blocked
                    current_hand.blocked = True
                    hand_stack.appendleft(current_hand)
                elif len(hand_stack) == 0 or all([h.blocked for h in hand_stack]):
                    # Only if there is no more unblocked hands open dealers cards.
                    # It prevents opening the dealer if player has hands with decisions to make
                    current_points = self.calculate_hand(current_hand.player_cards)

                    dealer_points = self.calculate_hand(dealer_cards)
                    self.print_dealers(dealer_cards, show_off=True)
                    current_hand.print_hand()

                    while dealer_points <= 17:  # Hit dealers until it reaches at least 17 points
                        try:
                            dealer_cards.append(deck.pop())
                        except IndexError:
                            print("Not enough cards in the deck! The game is over :)")
                            return

                        dealer_points = self.calculate_hand(dealer_cards)
                        self.print_dealers(dealer_cards, show_off=True)

                    # Win comparison:
                    if dealer_points > 21 or current_points > dealer_points:
                        self.cash += current_hand.current_bet * 2
                        print("You won!")
                    else:
                        print("You lost!")

            elif decision == "D":
                self.cash -= current_hand.current_bet
                current_hand.current_bet = current_hand.current_bet * 2
                current_hand.blocked = True
                try:
                    current_hand.add_card(deck)
                except IndexError:
                    print("Not enough cards in the deck! The game is over :)")
                    return
                hand_stack.appendleft(current_hand)
            elif decision == "S":
                # append 'new' hand made of the last card:
                hand_stack.append(Hand(self, [current_hand.player_cards[-1]]))

                # append 'old' hand but trimmed:
                current_hand.player_cards = current_hand.player_cards[:-1]
                hand_stack.append(current_hand)
            elif decision == "SAVE":
                hand_stack.append(current_hand)
                # 
                # to_save = []
                # to_save.append({self.})
                # 
                # for hand in hand_stack:
                #     to_save.append(vars(hand))
            else:
                hand_stack.append(current_hand)
                print("wrong input!")

    def print_dealers(self, dealer_cards, show_off=False):
        if show_off:
            print(" ".join([str(c) for c in dealer_cards]))
        else:
            print(f"{dealer_cards[0]} **")

    def calculate_hand(self, cards: List) -> int:
        points = 0
        aces_indexes = []
        for index, card in enumerate(cards):
            points += card.value
            if card.num == "A" and card.value == 11:
                aces_indexes.append(index)

        if points > 21:
            for a_index in aces_indexes:
                cards[a_index].value = 1
                points -= 10
                if points <= 21:
                    break
        return points

    def load_game(self):
        print("Load game!")

    def settings(self):
        settings_msg = f"""Settings
        C - cash (current: {self.cash})
        B - bet (current: {self.bet_value})
        N - num_of_decks (current: {self.num_of_decks})
        S - split (current: {self.split})
        I - insurance (current: {self.insurance})
        D - double (current: {self.double})
        Enter - go back
        """
        print(settings_msg)


game = Game()
game.main_loop()
