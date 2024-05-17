from model import *
import random
import math


def simulate_game(player1_name, player2_name, probability_method, starting_num_dice=5, verbose = True):
    """
    player1_name: str of player name. This is the starting player in round 1
    player2_name: str of player name
    probability_method: str. "truthful" uses compute_truthful_probability(), "conditional" uses compute_conditional_probability()
    starting_num_dice: int of number of dice to start game with for each player (default 5)

    Simulate one full game
    """
    # Set Up
    hand1_dict = create_hand(starting_num_dice)
    hand2_dict = create_hand(starting_num_dice)

    hand1 = LiarsDiceHand(player1_name, hand1_dict, len(dice_dict_to_sorted_list(hand2_dict)))
    hand2 = LiarsDiceHand(player2_name, hand2_dict, len(dice_dict_to_sorted_list(hand1_dict)))

    game = LiarsDiceGame(hand1, hand2)

    # Game Simulation
    round_number = 1   

    while not game.game_over:
        if verbose:
            print(f'Round #{round_number}')
            print(game.access_hand(player1_name))
            print(game.access_hand(player2_name))
        bidder_name = game.turn

        # Opening Bid
        previous_bid = None
        round_over = False
        while not round_over:
            bidder_name = game.turn
            if bidder_name == game.player1_name: 
                bidder_hand_object = game.player1_hand_object
                observer_hand_object = game.player2_hand_object
                observer_name = game.player2_name
            else: 
                bidder_hand_object = game.player2_hand_object
                observer_hand_object = game.player1_hand_object
                observer_name = game.player1_name

            
            #make a bid
            bid = game.construct_bid(bidder_name, previous_bid) 
            game.declare_bid(bidder_name, bid)

            #determine if challenge bid

            #compute the probability of a bid being correct
            if probability_method == "truthful":
                prob_bid_correct = observer_hand_object.compute_truthful_probability_correct(bid)
            elif probability_method == "conditional":
                prob_bid_correct = observer_hand_object.compute_conditional_probability_correct(bid, observer_hand_object.expected_opponent_bluff_prob())
            else:
                raise NameError(f"Incorrect probability method. You chose {probability_method}.")


            print(f"{observer_name}'s estimated ({probability_method}) probability {bidder_name}'s bid Correct : {round(prob_bid_correct, 3)}")
            if prob_bid_correct > observer_hand_object.user_challenge_threshold: # bid likely enough to not challenging
                total_dice_on_board = len(bidder_hand_object) + len(observer_hand_object)
                if bid.bid_value == 6 and bid.bid_quantity == total_dice_on_board: # the player is forced to challenge, because there are no more possible bids
                    game.challenge_bid(bid, observer_name)
                    round_over = True
            else:
                game.challenge_bid(bid, observer_name)
                round_over = True
            
            previous_bid = bid

        round_over = False
        round_number += 1

    if verbose:
        game.get_game_history()
    return game


if __name__ == "__main__":
    # simulate_game("Me", "Subject", "truthful")
    simulate_game("Me", "Subject", "conditional")

    