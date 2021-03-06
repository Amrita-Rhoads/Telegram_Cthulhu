# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 11:18:11 2018

@author: Amrita

This module implements classes needed for a game of Cthulhu.

TODO: Implement better errors.
TODO: Implement game settings.
"""
import random
import emojis
import itertools

class GameError(Exception):
    """
    Exceptions that might occur in the game.
    """
    def __init__(self, message, code=0):
        self.message = message
        self.code = code


class InvalidSettingsError(GameError):
    """
    """
    pass


class Card:
    """
    A card for games of Don't Mess with Cthulhu.

    Attributes:
      title - the title of the card.
      description - a description of what the card does.
      symbol - the symbolic representation of the card.
      is_flipped - whether the card has been revealed.
    """

    def __init__(self, ctype=None):
        """
        Initializes a card with default information.

        Arguments:
          type - Optional. If a type of card is specified, will load info.
        """
        self.title = "Null"
        self.description = "A blank card. Should not be in the game."
        self.symbol = "null"
        word_len = len(ctype)
        # Scan for extant data.
        with open("card_information/card_data.txt") as f:
            for line in f:
                if ctype==line[0:word_len]:
                    card_data = line.rstrip().split(",")
                    self.title = card_data[0]
                    self.description = card_data[1]
                    self.symbol = emojis.encode(":{}:".format(card_data[2]))
        self.is_flipped = False

    def __str__(self):
        """
        Returns the symbolic representation of the card.
        """
        if self.is_flipped:
            return self.symbol
        else:
            return emojis.encode(":black_circle:")

    def help(self):
        """
        Returns help on how the card functions.

        TODO
        """
        pass

    def flip_up(self):
        """
        Flip the card face-up.
        """
        self.is_flipped = True

    def flip_down(self):
        """
        Flip the card face-down.
        """
        self.is_flipped = False


class PlayerGameData:
    """
    A class containing relevant data for a player in a game of Cthulhu.

    Attributes:
      role - the player's role.
      cards - the cards in the player's hand.
      can_claim - whether the player can claim currently.
      claim - what the player claims to have.
      has_flashlight - whether the player has the flashlight.
    """
    def __init__(self, role):
        """
        Initialize a player as though they're starting a game.
        """
        self.role = role
        self.cards = []
        self.can_claim = False
        self.claim = None
        self.has_flashlight = False


class PlayerStats:
    """
    A class containing statistics about a player's win record.

    Attributes:
        ngcw - Number of games player has won as a cultist.
        ngcl - Number of games player has lost as a cultist.
        ngiw - Number of games player has won as an investigator.
        ngil - Number of games player has lost as an investigator.
    """
    def __init__(self):
        """
        Initialize all stats to 0.
        """
        self.ngcw = 0
        self.ngcl = 0
        self.ngiw = 0
        self.ngil = 0


class Player:
    """
    A player for games of Don't Mess with Cthulhu.

    Attributes:
        p_id - the player's ID.
        nickname - the player's current nickname.
        status - the status of the player in the game.
        game_data - if the player is in a game, the data associated with it.
        stats - a dictionary containing a lot of player stats.
    """

    def __init__(self, player_id, nickname=None):
        """
        Initialize a blank Player with a given player id.

        Arguments:
          player_id - the ID to label this Player with.
          nickname - Optional. The player's name.
        """
        self.p_id = player_id
        if nickname:
            self.nickname = nickname
        self.status = "Idle"
        self.game_data = None
        self.stats = PlayerStats()

    def start_playing(self, role):
        """
        Updates instance to having started a game.

        Raises:
          Game Error - If the player wasn't in pending game.
        """
        self.game_data = PlayerGameData(role)
        self.status = "Playing"
        self.game_data.can_claim = True

    def start_spectating(self):
        # Todo
        self.status = "Spectating"

    def __str__(self):
        """
        Returns the players name.
        """
        return self.nickname

    def set_hand(self, hand):
        """
        Sets the contents of this player's hand.
        """
        self.game_data.cards = hand

    def give_card(self, card):
        """
        Give the player a new card.
        """
        self.game_data.cards.append(card)

    def set_claim(self, claim):
        """
        Sets the value of this player's claim.
        """
        if not self.game_data.can_claim:
            raise GameError("You cannot claim right now.")
        self.game_data.claim = claim
        self.game_data.can_claim = False

    def hand_summary(self):
        """
        Displays a summary of what's in a player's hand.

        Returns:
          contents - a string summarizing hand contents.

        Raises:
          GameError - if no game data exists for the player.
        """
        hand = {}
        contents = ""
        # Ensure this player has a hand.
        if not self.game_data:
            raise GameError("It appears this player isn't in a game.")
        # Count cards in the hand and format them.
        for card in self.game_data.cards:
            if card.title in hand:
                hand[card.title] += 1
            else:
                hand[card.title] = 1
        for card_type in hand:
            contents += "{} {}(s), ".format(hand[card_type], card_type)
        return contents

    def role_summary(self):
        """
        Displays the player's role and win condition.

        Returns:
          contents - a string summarizing the role.

        Raises:
          GameError - if the player is not in a game.
        """
        contents = ""
        if self.status != "Playing":
            raise GameError("Not currently playing a game.")
        return self.game_data.role

    def display_hand(self, omniscient=False):
        """
        Returns the hand as it should be displayed.

        Arguments:
          omniscient - If True, shows entire contents of hand.
        """
        display = ""
        for card in self.game_data.cards:
            if omniscient:
                display += card.symbol
            else:
                display += str(card)
        return display

    def display_claim(self):
        """
        Displays the player's claim in symbolic form.
        """
        display = ""
        for card in self.game_data.claim:
            display += card.symbol
        return display

    def reveal_card(self, pos=None):
        # Flip a specific card.
        if pos:
            if not self.game_data.cards[pos].is_flipped:
                raise GameError("No card to flip!")
            else:
                self.game_data.cards[pos].flip_up()
                return
        # Otherwise, just flip the first card.
        for card in self.game_data.cards:
            if not card.is_flipped:
                card.flip_up()
                return
        raise GameError("All cards are faceup!")

    def toggle_flashlight(self):
        """
        Toggle whether this player has the flashlight.
        """
        self.game_data.has_flashlight = not self.game_data.has_flashlight


class GameSettings:
    """
    Contains game settings that can be passed into a game.

    Attributes:
      expansions - a list of expansions being used.
      min_players - the minimum number of players.
      max_players - the maximum number of players.
    """

    def __init__(self):
        """
        Initialize to defaults.
        """
        self.expansions = []
        self.min_players = 3
        self.max_players = 10


class Game:
    """
    A game of Don't Mess with Cthulhu.

    Attributes:
        players - A list of players in the game or spectating.

        game_status - The status of this game.
        round_counter - Number of rounds that have passed.
        phase - Whether it's time for claims or investigation.
        turn - How many turns have passed in the current phase.

        deck - A deck of cards representing the game.
        discard - The discard pile.

        game_settings - The game's settings.
        game_logs - A representation of the game.
        winner - The winning team.
    """

    def __init__(self, game_settings=None):
        """
        Start a new, empty game of Don't Mess with Cthulhu.

        Arguments:
          game_settings - The game's settings.
        """
        self.players = []
        self.game_status = "Unstarted"
        self.game_settings = GameSettings()

    def add_player(self, player, is_playing=True):
        """
        Add a new player for the game.

        Arguments:
          player - a Player class.
          is_playing - whether the player is playing (True) or spectating.
        """
        # Check that the game accepts new players.
        if self.game_status != "Unstarted" and is_playing:
            raise GameError("The game has already started.")
        # Check that the player hasn't already joined.
        if player in self.players:
            if player.status == "Playing":
                raise GameError("You're already in this game.")
            elif player.status == "Spectating":
                raise GameError("You're already spectating this game.")

        # Add the player as a participant or spectator.
        if is_playing:
            player.status = "Playing"
        else:
            player.status = "Spectating"
        self.players.append(player)

    def remove_player(self, player):
        """
        Remove a player, if they were playing.
        """
        if player in self.players:
            self.players.remove(player)
        else:
            raise GameError("You weren't in the game.")

    def count_active_players(self):
        """
        A helper function that counts the number of non-spectating players.
        """
        return sum([p.status=="Playing" for p in self.players])

    def get_active_players(self):
        """
        A helper function that returns the non-spectating players.
        """
        return [p for p in self.players if p.status=="Playing"]

    def get_spectators(self):
        """
        A helper function that returns the spectating players.
        """
        return [p for p in self.players if p.status=="Spectating"]

    def get_current_player(self):
        """Get the current player."""
        if self.phase == "Claims":
            for p in self.get_active_players():
                if p.game_data.can_claim:
                    return p
        elif self.phase == "Investigation":
            for p in self.get_active_players():
                if p.game_data.has_flashlight:
                    return p

    def get_next_player(self, player):
        """Get the next active player."""
        ind = self.players.index(player)
        while True:
            ind += 1
            if ind == len(self.players):
                ind = 0
            if self.players[ind].status == "Playing":
                return self.players[ind]

    def start_game(self):
        """
        Starts the pending game.

        Raises:
          GameError - If the game has already been started.
        """
        if self.game_status != "Unstarted":
            raise GameError("This game has already been started.")
        else:
            # Assign roles to players.
            roles = self.make_roles()
            for i, p in enumerate(self.get_active_players()):
                p.start_playing(roles[i])
            # Deal cards.
            self.create_deck()
            self.deal_cards()
            # Give someone the flashlight.
            random.choice(self.get_active_players()).toggle_flashlight()
            # Note that the game is ongoing.
            self.game_status = "Ongoing"
            self.round_counter = 1
            self.phase = "Claims"
            self.turn = 1

    def create_deck(self):
        """
        Create the deck.

        TODO: Implement Necronomicon and Objects of Power.
        """
        self.deck = []
        self.discard = []
        n_players = self.count_active_players()
        # Add Cthulhu card(s).
        if n_players > 8:
            self.deck.append(Card(ctype="Cthulhu"))
        self.deck.append(Card(ctype="Cthulhu"))
        # Add Elder Signs.
        for i in range(n_players):
            self.deck.append(Card(ctype="Elder Sign"))
        # Add blanks.
        for i in range((n_players * 5) - len(self.deck)):
            self.deck.append(Card(ctype="Blank"))

    def make_roles(self):
        """
        Assign roles to players.
        """
        # Determine the number of investigators and cultists.
        n_players = self.count_active_players()
        print(n_players)
        got_info = False
        with open("roles/role_info.txt") as f:
            for line in f:
                if str(n_players)==line.rstrip().split(",")[0]:
                    role_data = line.rstrip().split(",")
                    n_investigators = int(role_data[1])
                    n_cultists = int(role_data[2])
                    got_info = True
        if not got_info:
            raise GameError("Failed to find a role setup.")
        # Make a deck of roles and distribute them.
        roles = ["Investigator"] * n_investigators + ["Cultist"] * n_cultists
        random.shuffle(roles)
        return roles

    def deal_cards(self):
        """
        Deal cards equally between all active players.
        """
        random.shuffle(self.deck)
        while len(self.deck) > 0:
            for p in self.get_active_players():
                p.give_card(self.deck.pop())

    def get_log(self, setting=None):
        """
        Gets a display of the game state, according to settings.
        """
        pass

    def set_claim(self, player, blank, elder, cthulhu):
        """
        Sets the claim for a player and updates the game log accordingly.
        """
        claim = []
        for i in range(blank):
            claim.append(Card(ctype="Blank"))
        for i in range(elder):
            claim.append(Card(ctype="Elder Sign"))
        for i in range(cthulhu):
            claim.append(Card(ctype="Cthulhu"))
        player.set_claim(claim)
        if self.phase == "Claims":
            self.get_next_player(player).game_data.can_claim = True
            self.new_turn()

    def investigate(self, user, target, pos=None):
        """
        Has one player investigate another.
        """
        if not user.game_data.has_flashlight:
            raise GameError("Must have the flashlight to investigate!")
        user.game_data.has_flashlight = False
        target.reveal_card(pos=pos)
        target.game_data.has_flashlight = True
        self.new_turn()

    def new_turn(self):
        """Check for winners, etc."""
        self.check_winner()
        self.turn += 1
        if self.turn > self.count_active_players():
            if self.phase == "Claims":
                self.new_phase()
            else:
                self.new_round()

    def new_phase(self):
        """Transition from claims to investigations."""
        self.phase = "Investigation"
        self.turn = 1
        for p in self.get_active_players():
            p.game_data.can_claim = True

    def new_round(self):
        """
        Collect and redeal cards.
        """
        self.phase = "Claims"
        self.turn = 1
        # Reset player data as needed.
        for p in self.get_active_players():
            # Return cards to deck or discard.
            for card in p.game_data.cards:
                if card.is_flipped:
                    self.discard.append(card)
                else:
                    self.deck.append(card)
            p.game_data.cards = []
            # Ensure claims will work.
            if p.game_data.has_flashlight:
                p.game_data.can_claim = True
            else:
                p.game_data.can_claim = False
        # Deal out cards again.
        self.deal_cards()

    def check_winner(self):
        """
        Checks whether a team has won.
        """
        cards_revealed = 0
        signs_found = 0
        # Search through all revealed cards.
        revealed = [p.game_data.cards for p in self.get_active_players()]
        revealed.append(self.discard)
        for card in itertools.chain(*revealed):
            if card.is_flipped:
                cards_revealed += 1
                if card.title == "Cthulhu":
                    self.winner = "Cultist"
                elif card.title == "Elder Sign":
                    signs_found += 1
        if signs_found >= self.count_active_players():
            self.winner = "Investigator"
        elif cards_revealed >= self.count_active_players() * 4:
            self.winner = "Cultist"

    def end_game(self):
        """
        Updates player statistics and finishes a game.
        """
        self.game_status = "Ended"
        # print game log
        # update player stats
        pass

    def display_board(self):
        """
        Returns a nicely formatted version of the board as it is.
        """
        display = ""
        display += "Round: {}   ".format(self.round_counter)
        display += "Phase: {}   ".format(self.phase)
        display += "Turn: {} \n".format(self.turn)
        for i, player in enumerate(self.get_active_players()):
            display += str(i + 1)
            display += " : "
            display += str(player)
            if player.game_data.has_flashlight:
                display += "(" + emojis.encode(":flashlight:") + ")"
            display += " : "
            display += player.display_hand()
            display += "\n"
            if player.display_claim():
                display += ("Claimed: %s" % player.display_claim())
                display += "\n"
            display += "\n"
        return display
    ############################

    def get_whose_claim(self):
        """
        Returns whose claim it is.
        """
        return self.whose_claim

    def is_valid_name(self, name):
        """
        Returns whether the name is a valid player.

        @name - the player's name.
        """
        for i, player in enumerate(self.players):
            if str(player).lower() in name.lower():
                return i
            elif i > 0 and str(i + 1) in name:
                return i
            elif i == 0 and "1" in name and "10" not in name:
                return i
        return -1

    def get_position(self, player_id=None, name=None):
        """
        Gets the position of a player based on their name or id. Returns -1
        if not found.
        """
        for i, player in enumerate(self.players):
            if player_id == player.get_id():
                return i
            elif name == str(player):
                return i
        return -1

    def recollect_cards(self):
        """
        Recollects the cards from a round and resets claims.
        """
        assert len(self.moves) == len(self.players)
        self.deck.return_cards(self.moves)
        self.moves = []
        for player in self.players:
            player.set_claim(0, 0, 0)

    def claim_old(self, pos, blank, elder, cthulhu):
        """
        Sets the claim for a player at position pos. Do nothing if disallowed.

        @param pos - position of player.
        @param blank - number of blanks to claim.
        @param elder - number of elder signs to claim.
        @param cthulhu - number of cthulhus to claim.
        """
        # If the player can claim, update their claim.
        if self.whose_claim == pos or self.whose_claim == -1:
            self.players[pos].set_claim(blank, elder, cthulhu)
        # If the next person to claim needs to be updated, do so.
        if self.whose_claim == pos:
            self.whose_claim += 1
        # Wrap around the table in terms of claims.
        if self.whose_claim == len(self.players):
            self.whose_claim = 0
        # If everybody has claimed, anyone can now claim.
        if self.whose_claim == self.claim_start:
            self.whose_claim = -1

    def investigate_old(position):
        """
        Investigate the player at position position and return result.
        """
        assert self.can_investigate_position(position)
        # Investigate and add the move to the history.
        temp = self.flashlight
        self.flashlight = position
        move = self.players[temp].investigate(self.players[position])
        self.moves.append(move)
        # If this is the last investigation of a round, update the counter.
        if len(self.moves) == len(self.players):
            self.round_number += 1
        # If an elder sign was found, update the signs remaining.
        if "E" in move:
            self.signs_remaining -= 1
        return move

    def redeal(self):
        """
        If needed, recollect and deal cards. Returns True if done.
        """
        if len(self.moves) >= len(self.players):
            self.recollect_cards()
            self.deal_cards()
            return True
        return False

    def take_move(self):
        """
        Takes a player to investigate via raw_input.

        Obsolete, except for text-based games.
        """
        move = input("Who do you want to investigate? \n")
        for i, player in enumerate(self.players):
            # This will have issues in 10 player games - return to pls.
            if str(i + 1) in move or str(player) in move:
                if player.can_be_investigated():
                    temp = self.flashlight
                    self.flashlight = i
                    return self.players[temp].investigate(player)
                else:
                    print("You can't investigate this player.")
        print("Looks like you entered invalid input. Please try again.")



    def print_board(self):
        """
        Prints a simple representation of the board.

        Mostly obsolete.
        """
        for i in range(len(self.players)):
            print(str(i + 1), ":", str(self.players[i]),
                  self.players[i].display_hand())
        print("Flashlight is with player", self.flashlight + 1)

    def do_test_round(self):
        """
        Does a simple test round, displaying everything.
        """
        self.deal_cards()
        self.print_board()

        for i, player in enumerate(self.players):
            player.print_info()

        successful_moves = 0
        moves = []
        while (successful_moves < len(self.players)):
            move = self.take_move()
            if move:
                successful_moves += 1
                self.print_board()
                moves.append(move)
            # Maybe split this up into a checker function.
                if "E" in move:
                    self.signs_remaining -= 1
                    if self.signs_remaining == 0:
                        print("Congratulations! Investigator victory!")
                        break
                if "C" in move:
                    print("Cultist victory!")
                    break
        self.recollect_cards(moves)
