import numpy as np
import random
from scipy.stats import binom
import math
import itertools
from collections import Counter
from math import factorial


def convert_list_to_dict(hand):
    """
    hand: list integers randomly generated between 1 and 6
    
    Return the dictionary representation of `hand`
    """
    res = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0} # instantiate
    for die in hand:
        res[die] += 1
    return res

def create_hand(num_dice):
    """
    num_dice: int [1, 5] of number of dice to roll

    return a return the dictionary representation of `hand` with `num_dice`
    """
    if not 0 <= num_dice <= 5:
        raise ValueError(f"Choose number between 0-5 for dice number. You chose {num_dice}.")
    hand =[]
    for i in range(num_dice):
        hand.append(random.randint(1, 6))
    return convert_list_to_dict(hand)

def dice_dict_to_sorted_list(dice_dict):
    """
    dice_dict: dict with keys from 1 to 6 and values as the count of dice of that value
    returns a list of dice values sorted from smallest to largest
    """
    dice_list = []
    for die_value, count in dice_dict.items():
        dice_list.extend([die_value] * count)

    dice_list.sort()
    return dice_list

def select_random_dice(user_dice_dict):
    """
    user_dice_dict: dict with keys from 1 to 6 and values as the count of dice of that value
    returns a randomly selected die from the user's hand
    """
    all_dice = []
    for die_value, count in user_dice_dict.items():
        all_dice.extend([die_value] * count)

    if not all_dice:
        raise ValueError("No dice in hand to select.")

    return random.choice(all_dice)


memo_list_hands = {}  #keys are `user_num_dice`, values are list of dictionaries of all possible hands of with `user_num_dice` dice

def all_possible_list_hands(user_num_dice):
    """
    user_num_dice: int [1, 5] of number of dice to in user hand

    return a list of all possible lists of `user_num_dice` integers randomly generated between 1 and 6
    """
    if not 0 <= user_num_dice <= 5:
        raise ValueError(f"Choose number between 0-5 for dice number. You chose {user_num_dice}.")
    
    if user_num_dice in memo_list_hands:
        return memo_list_hands[user_num_dice]

    dice_range = range(1, 7)  # Dice numbers from 1 to 6
    hands = [convert_list_to_dict(hand) for hand in itertools.combinations_with_replacement(dice_range, user_num_dice)]

    memo_list_hands[user_num_dice] = hands

    return hands

memo_toy_hand_objects = {} #keys are tuples (`user_num_dice`, `opponent_num_dice`), values are list of all possible hand_objects

def all_possible_toy_hand_objects(user_num_dice, opponent_num_dice):
    """
    user_num_dice: int [1, 5] of number of dice in user hand
    opponent_num_dice: int [1, 5] of number of dice in opponent hand

    return a list of all LiarsDiceHand objects with `user_num_dice` and opponent_num_dice
    """

    if not 0 <= user_num_dice <= 5:
        raise ValueError(f"Choose number between 0-5 for `user_num_dice`. You chose {user_num_dice}.")
    
    if not 0 <= opponent_num_dice <= 5:
        raise ValueError(f"Choose number between 0-5 for `opponent_num_dice`. You chose {opponent_num_dice}.")
    
    key = (user_num_dice, opponent_num_dice)
    if key in memo_toy_hand_objects:
        return memo_toy_hand_objects[key]

    hand_objects = []
    for list_hand in all_possible_list_hands(user_num_dice):
        hand_objects.append(LiarsDiceHand('Toy', list_hand, opponent_num_dice))

    memo_toy_hand_objects[key] = hand_objects

    return hand_objects



class LiarsDiceGame:
    def __init__(self, player1_hand_object, player2_hand_object):
        """
        player1_hand_object: player1's LiarsDiceHand
        player2_hand_object: player2's LiarsDiceHand
        
        Initalize a Game of Liars Dice. Player1 will query first by default
        """

        # make sure valid initialization
        self.valid(player1_hand_object, player2_hand_object)
        
        self.player1_hand_object = player1_hand_object
        self.player1_name = player1_hand_object.name
        self.player2_hand_object = player2_hand_object
        self.player2_name = player2_hand_object.name
        self.turn = self.player1_name
        self.round_number = 1
        self.game_over = False

        # dictionary of game history
        # keys: round #
        # values: dictionary of information in that round
            # keys: "Hands", "Actions", "Winner", "Loser"
            # values:
                # Names and Hands of the players: {"Name" : hand(list)}
                # Bids: ["Bid", bidding player, bid dice quantity, bid dice value, correct bid?] 
                #   / Challenges: ["Challenge", challenging player, bid dice quantity challenged, bid dice value challenged, successful challenge?]
                # Winner: "Winner Name"
                # Loser: "Loser Name"
        self.game_history = {1: {"Hands": {}, "Actions":[], "Winner": "", "Loser": ""}, 
                             2: {"Hands": {}, "Actions":[], "Winner": "", "Loser": ""}, 
                             3: {"Hands": {}, "Actions":[], "Winner": "", "Loser": ""}, 
                             4: {"Hands": {}, "Actions":[], "Winner": "", "Loser": ""}, 
                             5: {"Hands": {}, "Actions":[], "Winner": "", "Loser": ""}, 
                             6: {"Hands": {}, "Actions":[], "Winner": "", "Loser": ""}, 
                             7: {"Hands": {}, "Actions":[], "Winner": "", "Loser": ""}, 
                             8: {"Hands": {}, "Actions":[], "Winner": "", "Loser": ""}, 
                             9: {"Hands": {}, "Actions":[], "Winner": "", "Loser": ""}}
    
    def valid(self, player1_hand_object, player2_hand_object):
        """
        Ensure valid game configeration
        """
        assert len(player1_hand_object) == player2_hand_object.opponent_num_dice, f"Inconsistent hand sizes: {player1_hand_object}"
        assert len(player2_hand_object) == player1_hand_object.opponent_num_dice, f"Inconsistent hand sizes"

    def overide_hand(self, new_player1_hand_object, new_player2_hand_object):
        """
        This Function allows you to manually input hand objects of your choosing
        """
        self.player1_hand_object = new_player1_hand_object
        self.player2_hand_object = new_player2_hand_object 

    def declare_bid(self, bidding_player, bid):
        """
        bidding_player: name of player making the bid
        bid: Bid object

        Adds bid to self.bid_history
        """
        # check that the correct player is bidding this turn
        assert bidding_player == self.turn, f'bidding_player: {bidding_player}, turn: {self.turn}'

        is_bid_correct = self.correct_bid(bid)
        self.game_history[self.round_number]["Actions"].append(["Bid", bidding_player, bid.bid_quantity, bid.bid_value, is_bid_correct])

        # switch turns
        if bidding_player == self.player1_name:
            self.turn = self.player2_name
        else:
            self.turn = self.player1_name

        print(f'{bidding_player} bid {bid.bid_quantity} dice of value {bid.bid_value}. Correct? {is_bid_correct}.')

    def construct_bid(self, bidding_player, previous_bid):
        """
        bidding_player: name of player making the bid
        previous_bid: Bid object of previous round bid. None if we are constructing the first bid
        
        return Bid object of the newly constructed bid
        """
        if bidding_player == self.player1_name:
            player_hand = self.player1_hand_object
        else:
            player_hand = self.player1_hand_object
        
        #can't raise bid beyond 6
        max_die_value = 6

        #equal to what player actually has + what the player expects the opponent has
        expected_board = player_hand.compute_expected_board_quantities()

        if previous_bid == None:
            #assume they choose their first dice at random from the dice they have (so if they have multiple of a dice it has
            # a larger chance of getting selected)
            new_bid_value = select_random_dice(player_hand.user_dice_dict)
            min_quantity = 1
        else:
            if previous_bid.bid_value == max_die_value:
                new_bid_value = previous_bid.bid_value
                min_quantity = previous_bid.bid_quantity + 1
            else:
                # player keeps same bid value if they expect at greater than that quantity that on the board
                if expected_board[previous_bid.bid_value] > previous_bid.bid_quantity: 
                    new_bid_value = previous_bid.bid_value
                    min_quantity = previous_bid.bid_quantity + 1
                else:
                    min_quantity = 1
                    has_valid_value = False
                    #player finds the value they have nearest (but greater than) the previous bid value
                    for new_bid_value in range(int(previous_bid.bid_value) + 1, int(max_die_value) + 1):
                        if player_hand.user_dice_dict[new_bid_value] > 0:
                            has_valid_value = True
                            break 
                    
                    #player has no dice greater than the current value so they will select a value at randome
                    if not has_valid_value:
                        new_bid_value = random.randint(previous_bid.bid_value + 1, max_die_value)
        
        expected_board_quantity = expected_board[new_bid_value]
        player_actual_quantity = player_hand.user_dice_dict[new_bid_value]
        player_remaining_dice = len(player_hand) - player_actual_quantity
        #bluff is bernouli probability of bluffing on each remaining dice. In expection you multiply p * n
        player_bluff_quantity = player_hand.user_bluff_prob() * player_remaining_dice 
        int_quantity = round(expected_board_quantity + player_bluff_quantity, 0)
        max_dice_quant = len(player_hand) + player_hand.opponent_num_dice
        new_bid_quantity = int(max(int_quantity, min_quantity))

        return Bid(new_bid_quantity, new_bid_value)

    def correct_bid(self, bid):
        """
        bid: Bid object

        Return boolean if there exists >= `bid.bid_quantity` of `bid.bid_value` on the board
        """
        # correct bid considering both players' hands
        actual_quantity = self.player1_hand_object.quantity_of_value(bid.bid_value) + self.player2_hand_object.quantity_of_value(bid.bid_value)
        correct = actual_quantity >= bid.bid_quantity

        return correct

    def correct_bid_self(self, player_name, bid):
        """
        player_name: str of player name
        bid: Bid object

        Return boolean if there exists >= `bid.bid_quantity` of `bid.bid_value` in `player_name`s hand 
        """
        # correct bid looking **only at player_name's** hand
        if player_name == self.player1_name:
            player_hand = self.player1_hand_object
        else:
            player_hand = self.player2_hand_object
        quantity = player_hand.user_dice_dict[bid.bid_value] 
        
        correct = quantity >= bid.bid_quantity

        return correct

    def challenge_bid(self, bid, challenging_player_name):
        """
        bid: Bid object
        challenging_player_name: str of player's name that is making the challenge

        Update game state after a bid challenge. Print the number of dice remaining after losing player has lost a dice and
        both players have rerolled. Also print the winner and loser of this challenge as this determines the player that 
        makes the next bid
        """
        #slightly unintuitive, but self.turn changes after a bid is made
        assert challenging_player_name == self.turn, "Can't challenge your own bid"

        
        is_correct_bid = self.correct_bid(bid)
        is_successful_challenge = not is_correct_bid

        # update game history with current hands and challenge
        self.game_history[self.round_number]["Hands"][self.player1_name] = self.player1_hand_object.user_dice_dict
        self.game_history[self.round_number]["Hands"][self.player2_name] = self.player2_hand_object.user_dice_dict
        self.game_history[self.round_number]["Actions"].append(["Challenge", challenging_player_name, bid.bid_quantity, bid.bid_value, is_successful_challenge])

        # rerolls and loser gets next turn
        if challenging_player_name == self.player1_name:
            if is_correct_bid: # player 1 lost challenge, loses 1 die
                self.player1_hand_object.decrement_and_reroll(True)
                self.player2_hand_object.decrement_and_reroll(False)
                winner, loser = self.player2_name, self.player1_name
                self.turn = self.player1_name
            else: # player 2 lost challenge, loses 1 die
                self.player1_hand_object.decrement_and_reroll(False)
                self.player2_hand_object.decrement_and_reroll(True)
                winner, loser = self.player1_name, self.player2_name
                self.turn = self.player2_name
        elif challenging_player_name == self.player2_name:
            if is_correct_bid: # player 2 lost challenge, loses 1 die
                self.player1_hand_object.decrement_and_reroll(False)
                self.player2_hand_object.decrement_and_reroll(True)
                winner, loser = self.player1_name, self.player2_name
                self.turn = self.player2_name
            else: # player 1 lost challenge, loses 1 die
                self.player1_hand_object.decrement_and_reroll(True)
                self.player2_hand_object.decrement_and_reroll(False)
                winner, loser = self.player2_name, self.player1_name
                self.turn = self.player1_name
        else:
            raise NameError(f'{challenging_player_name} not valid name. Must be {self.player1_name} or {self.player2_name}')
        
        # current round ends, update game history with results
        self.game_history[self.round_number]["Winner"] = winner
        self.game_history[self.round_number]["Loser"] = loser
        
        self.round_number += 1

        remaining_dice_player1 = len(self.player1_hand_object)
        remaining_dice_player2 = len(self.player2_hand_object)
        
        # print info per the spec
        print(f'{challenging_player_name} challenged. Challenge successful? {is_successful_challenge}')
        print(f'Winner of challenge: {winner}. Loser of challenge: {loser}.')
        print(f'{self.player1_name} has {remaining_dice_player1} dice remaining.')
        print(f'{self.player2_name} has {remaining_dice_player2} dice remaining.')

        if remaining_dice_player1 > 0 and remaining_dice_player2 > 0:
            print(f'{self.turn} has the next turn.\n')
        else:
            print(f"Game over. {winner} wins, {loser} loses.\n")
            self.game_over = True
    
    def access_hand(self, player_name):
        """
        player_name: str of name (must be equal to self.player1_name or self.player2_name)

        Return `player_name`s hand object
        """

        if player_name == self.player1_name:
            return self.player1_hand_object
        elif player_name == self.player2_name:
            return self.player2_hand_object
        else:
            raise NameError(f'{player_name} not valid name. Must be {self.player1_name} or {self.player2_name}')
        
    def get_game_history(self):
        """
        Prints readable/formatted game history
        """
        print("GAME HISTORY: \n")
        print(f'ACTION = [Bid/Challenge, bidding_player/challenging player, bid_quantity, bid_value, is_bid_correct/is_challenge_correct]')
        for round, info in self.game_history.items():
            print(f'Round {round}:')
            for key, value in info.items():
                print(f'\t{key}: {value}')
        

class LiarsDiceHand:
    def __init__(self, name, user_dice_dict, opponent_num_dice):
        """
        user_dice_dict: dictionary of the quantity of 1,2,..,6 in user's hand 1 <= dice in user_dice_dict <= 5
        opponent: integer of opponent's hand size [1, 5] 
        
        Initalize a user's hand
        """
        self.valid(user_dice_dict, opponent_num_dice)

        self.name = name
        # self.user_num_dice = len(user_hand)
        # self.user_bluff_prob = 1 / len(user_hand)
        self.user_dice_dict = user_dice_dict
        self.user_challenge_threshold = 0.51

        self.opponent_num_dice = opponent_num_dice
        # uniform_prob = opponent_num_dice / 6 
        # self.expected_opponent_dice_dict = {1: uniform_prob, 2: uniform_prob, 3: uniform_prob, 4: uniform_prob, 5: uniform_prob, 6: uniform_prob} 
        # self.expected_opponent_bluff_prob = 1 / opponent_num_dice
    
    def user_bluff_prob(self):
        return (1 / len(self)) ** 2
    
    def expected_opponent_bluff_prob(self):
        return (1 / self.opponent_num_dice) ** 2
    
    def expected_opponent_dice_dict(self):
        uniform_prob = self.opponent_num_dice / 6 
        return {1: uniform_prob, 2: uniform_prob, 3: uniform_prob, 4: uniform_prob, 5: uniform_prob, 6: uniform_prob} 

    def valid(self, user_dice_dict, opponent_num_dice):
        """
        user_dice_dict: dictionary of the quantity of 1,2,..,6 in user's hand 1 <= dice in user_dice_dict <= 5
        opponent: integer of opponent's hand size [1, 5] 
        
        Ensure valid hand configuration
        """
        user_num_dice = sum(user_dice_dict.values())
        

        assert ((user_num_dice > 0) or (opponent_num_dice > 0)), "At least one player must have positive dice"
        assert (user_num_dice >= 0), "User can't have negative dice"
        assert (opponent_num_dice >= 0), "Opponent can't have negative dice"
        assert (user_num_dice <= 5), "User can't have more than 5 dice"
        assert (opponent_num_dice <= 5), "Opponent can't have more than 5 dice"
    
    def decrement_and_reroll(self, user_lost):
        """
        user_lost: boolean True if user lost round, boolean False if opponent lost round
    

        return None. Function updates the internal state of the object by 
        decrementing one from the num_dice value of the loser, and reroll user's hand using the `create_hand` helper function
        """
        new_user_num_dice = len(self)
        new_opponent_num_dice = self.opponent_num_dice

        if user_lost:
            new_user_num_dice -= 1
        else:
            new_opponent_num_dice -= 1
            
        new_user_hand = create_hand(new_user_num_dice)
        self.__init__(self.name, new_user_hand, new_opponent_num_dice)


    def compute_expected_board_quantities(self):
        """
        Return dictionary of the expected number of each dice from the user's perspective
        """
        total_dict = {}

        # the expected number of each dice in the opponent's hand is (1/6 * # of dice opponent has)
        for i in self.user_dice_dict.keys():
            total_dict[i] = self.user_dice_dict[i] + self.expected_opponent_dice_dict()[i]
        
        return total_dict

    def compute_truthful_probability_correct(self, bid):
        """
        bid: Bid object

        Return the probability of bid being correct from the perspective of the user (since they only have information about their hand and the size of the opponents hand) 
        This is the "truthful" probability because it does not account for bluffing
        """
        quantity_opponent_needs_to_have = int(bid.bid_quantity - self.user_dice_dict[bid.bid_value])
        if quantity_opponent_needs_to_have <= 0:
            return 1

        # Probability of rolling at least k of a value = 
        # sum from k to 5 of [(5 choose k) * (1/6)^k * (5/6)^(5-k)]
        # basically the sum from k to 5 of binom.pmf(k=k,n=5,p=1/6)

        uniform = 1/6
        probability_sum = 0
        for k in range(quantity_opponent_needs_to_have, self.opponent_num_dice + 1):
            probability_sum += binom.pmf(k=k, n=self.opponent_num_dice, p=uniform)

        return probability_sum
    
    def conditional_bid_prob(self, bid, s2_expected_bluff_prob):
        """
        IMPORTANT: user calling func is s2, the bidding player
        
        bid: Bid object
        s2_expected_bluff_prob: probability that s1 assigned to s2 bluffing
        
        Return probability user would make bid `bid` given what they know about their hand, s2, and their expected oppoenents hand, p(s1)

        s1 is observer (opponent), s2 is bidding player (user) and b is a valid bid: 
            p(b|s2, p(s1)) = sum over all i,j of p(i bid.bid_value in s1) * p(j user bluffs) such that with i+j = quantity_remaining that s2 doesn't have in it's hand
        """
        quantity_remaining = bid.bid_quantity - self.user_dice_dict[bid.bid_value]
        user_quantity_remaining = len(self) - self.user_dice_dict[bid.bid_value]
        opponent_quantity_remaining = self.opponent_num_dice

        prob_sum = 0
        for bluff_quantity in range(quantity_remaining + 1):
            opponent_quantity = quantity_remaining - bluff_quantity
            #make sure valid bluff_quantity and opponent quantity
            if (opponent_quantity_remaining >= opponent_quantity and user_quantity_remaining >= bluff_quantity): 
                #uniform assumption assumed throughout
                prob_exactly_opponent_quantity = (1/6) ** opponent_quantity 
                prob_exactly_bluff_quantity = s2_expected_bluff_prob ** bluff_quantity 
                prob_sum += prob_exactly_opponent_quantity * prob_exactly_bluff_quantity
        return prob_sum

    def prob_hand(self):
        """
        Compute the probability of constructing self.user_dice_dict assuming uniform probability
        """
        total_dice = len(self)

        if total_dice == 0:
            return 0  # No dice in hand

        # Probability of each die roll
        single_die_prob = 1/6

        # Compute multinomial coefficient
        multinomial_coeff = factorial(total_dice)
        for count in self.user_dice_dict.values():
            multinomial_coeff /= factorial(count)

        # Compute overall probability
        overall_prob = multinomial_coeff * (single_die_prob ** total_dice)
        return overall_prob

    def conditional_opponent_hand_prob(self, bid, bidding_hand, s2_expected_bluff_prob):
        """
        IMPORTANT: user calling func is s1, the observing player

        bid: Bid object
        bidding_hand: a valid LiarsDiceHand object of observed s2's (bidding player/oppoenent) hand
        s2_expected_bluff_prob: probability that s1 assigned to s2 bluffing

        s1 is observer (user), s2 is bidding player (opponent) and b is a valid bid: 
            p(s2|b,p(s1)) = [p(b|s2,p(s1) * p(s2))]/[sum over all valid s2 of p(b|s2,p(s1) * p(s2)]

        return probability of observing `bidding_hand` given bid `bid` and oponents expectation of s1's hand (uniform assumption held throughout)
        """
        bidding_hand_conditional_bid_prob = bidding_hand.conditional_bid_prob(bid, s2_expected_bluff_prob)
        
        bayes_numerator = bidding_hand_conditional_bid_prob * bidding_hand.prob_hand()

        bayes_denomenator = 0
        for s2_hand_obj in all_possible_toy_hand_objects(len(bidding_hand), len(self)):
            prob_hand = s2_hand_obj.prob_hand()
            bayes_denomenator += s2_hand_obj.conditional_bid_prob(bid, s2_expected_bluff_prob) * prob_hand
    
        return bayes_numerator / bayes_denomenator

    def compute_conditional_probability_correct(self, bid, s2_expected_bluff_prob):
        """
        IMPORTANT: user calling func is s1, the observing player
        
        bid: Bid object
        s2_expected_bluff_prob: probability that s1 assigned to s2 bluffing

        Return the probability of bid being correct where the user is the observer.

        s1 is observer (user), s2 is bidding player (opponent) and b is a valid bid:
            P(bid b correct) = sum over all possible s2 of (indicator variable correct_bid with s2 and s1) * p(s2|bid b, p(s1))
        """
        
        def correct_bid(bid, player1_hand_object, player2_hand_object):
            """
            player1_hand_object: LiarsDiceHand object
            player2_hand_object: LiarsDiceHand object

            Return boolean if there exists >= `bid.bid_quantity` of `bid.bid_value` on the board
            """
            # correct bid considering both players' hands
            actual_quantity = player1_hand_object.quantity_of_value(bid.bid_value) + player2_hand_object.quantity_of_value(bid.bid_value)
            correct = actual_quantity >= bid.bid_quantity
            return correct
        
        res = 0
        for s2_hand_obj in all_possible_toy_hand_objects(self.opponent_num_dice, len(self)):
            if correct_bid(bid, self, s2_hand_obj): #todo have a function that checks if bid satisfied using self.user_dice_dict and hand_dict
                res += self.conditional_opponent_hand_prob(bid, s2_hand_obj, s2_expected_bluff_prob)

        return res

    def quantity_of_value(self, value):
        assert (1 <= value and value <=6), f'invalid value: {value}'
        return self.user_dice_dict[value]

    def __str__(self):
        """
        Return a string representation of the current game state from the user's perspective
        """
        user_hand_str = ', '.join(map(str, dice_dict_to_sorted_list(self.user_dice_dict)))

        return (f"{self.name}\n"
                f"Hand: [{user_hand_str}]\n"
                f"Number of dice: {len(self)}\n"
                f"Opponent's number of dice: {self.opponent_num_dice}\n")
    
    def __len__(self):
        """
        Return the number of dice in user's hand
        """
        return sum(self.user_dice_dict.values())
    

class Bid:
    def __init__(self, bid_quantity, bid_value):
        """
        bid_quantity: int of bidding quantity
        bid_value: int of bidding dice value
    
        Initalize a Liars Dice bid
        """
        # make sure valid initialization
        self.valid_bid(bid_quantity, bid_value)

        self.bid_quantity = bid_quantity
        self.bid_value = bid_value
        
    def valid_bid(self, bid_quantity, bid_value):
        """
        bid_quantity: int of bidding quantity
        bid_value: int of bidding dice value
        
        Ensure valid bid parameters
        """
        assert isinstance(bid_quantity, int), f"bid_quantity, {bid_quantity} must be an integer"
        assert isinstance(bid_value, int), f"bid_value, {bid_value} must be an integer"
        assert bid_quantity > 0, f"bid_quantity, {bid_quantity} must be possitive"
        assert (bid_value >= 1 and bid_value <= 6), f"bid_value, {bid_value} must be between 1 and 6"
    
    def __str__(self):
        print(f"bid_quantity: {self.bid_quantity}, bid_value: {self.bid_value}")

if __name__ == "__main__":
    pass
    

