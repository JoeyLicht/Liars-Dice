import pandas as pd
import numpy as np
import random
from model import *




def parse_game(file_name, verbose = False):
    df = pd.read_csv(file_name)

    #group by game
    history={}
    df['Game'] = df['Game'].fillna(method='ffill')
    grouped = df.groupby('Game')

    def check_counts(list1, list2, value, count):
        """
        adds the number of dice with the value
        we want, and checks if it's at least
        as the bid count
        """
        count_in_list1 = list1.count(value)
        count_in_list2 = list2.count(value)
        return count_in_list1 + count_in_list2 >= count



    for game_number, group in grouped:
        
        # print(f"Processing Subgame {game_number}.")
        history[game_number] = {}
        
        #group by rounds/rolls in game:
        group['Roll'] = group['Roll'].fillna(method='ffill')
        grouped_round = group.groupby('Roll')
        # Process each round in the 'grouped_round' DataFrame
        # 'grouped_round' is a DataFrame containing rows for a specific round
        for r_num, round in grouped_round:
            # print(round, "DONE")
            Winner = None
            Loser = None
            #Original hand from csv
            player_1 = list(round["Me"].fillna(0))
            player_2 = list(round["Subject"].fillna(0))
            
            #organizing the hands:
            hand_1 = [index + 1 for index, count in enumerate(player_1) for _ in range(int(count))]
            hand_2 = [index + 1 for index, count in enumerate(player_2) for _ in range(int(count))]

            #collecting actions: #"bid" / "Challenge" #player #count #value #istrue
            Actions =[]
            for index, row in round.iterrows():
                # print(row)
                speaking_player = row["Speaking Player"]
                # print("SP",speaking_player)
                if pd.isna(speaking_player): #=="NaN":
                    continue
                other_player = 'Me' if speaking_player == 'Subject' else 'Subject'
                # print("ROW", row,"INDEX",index)
                count = row["Count"]
                dice = row["Dice #"]
                successful_challenge = row["Successfull Challenge?"]
                # print('suc', successful_challenge)
                true_count = check_counts(hand_1, hand_2, dice,count) 
                
                Actions.append(['Bid', speaking_player, count, dice, true_count])

                if not pd.isna(successful_challenge): # != "NaN":
                    yes = bool(successful_challenge=='Yes' or successful_challenge=='yes')
                    Actions.append(['Challenge', other_player, count, dice, not true_count])
                    if true_count:
                        Winner = speaking_player
                        Loser = other_player
                    else:
                        Loser = speaking_player
                        Winner = other_player 
            
            history[game_number]["Round "+str(r_num)] = {"Hands": {"Me":hand_1, "Subject":hand_2}, "Actions":Actions, "Winner": Winner , "Loser": Loser}

    if verbose:
        print(history)

    game_object_lis = (history_to_obj(history))
    return game_object_lis

def history_to_obj(history):
    """
    takes a history
    returns a list of games
    objects.
    """
    games = []
    for g in history:
        # print(f"game {g}")
        starting_player = history[g]["Round 1.0"]["Actions"][0][1]
        second_player = history[g]["Round 1.0"]["Actions"][1][1]
        for round in history[g]:
            starting_player_hand = LiarsDiceHand(starting_player, convert_list_to_dict(history[g][round]["Hands"][starting_player]), len(history[g][round]["Hands"]["Subject"]))
            second_player_hand = LiarsDiceHand(second_player, convert_list_to_dict(history[g][round]["Hands"][second_player]), len(history[g][round]["Hands"][starting_player]))
            if round == "Round 1.0":
                game = LiarsDiceGame(starting_player_hand, second_player_hand)
            else:
                game.overide_hand(starting_player_hand, second_player_hand)
            print(f"game {g}, {round}")
            print(f"{starting_player} hand: {starting_player_hand.user_dice_dict}")
            print(f"{second_player} hand: {second_player_hand.user_dice_dict}")
            
            

            # print(f'game: {g}, {round}, turn: {game.turn}')
            # print(f'Me: {starting_player_hand.user_hand}, User: {second_player_hand.user_hand}')
            for action in history[g][round]["Actions"]:
                player_turn = action[1]
                quantity = action[2]
                value = action[3]
                bid = Bid(int(quantity), int(value))
                # print(f'{action[0]}, {player_turn}, quantity {quantity}, value {value}')
                if action[0] == "Challenge":
                    # print(f'turn before challenge: {game.turn}')
                    game.challenge_bid(bid, player_turn)
                    # print(f'turn after challenge: {game.turn}')
                else:
                    game.declare_bid(player_turn, bid)
        games.append(game)
    return games




if __name__ == "__main__":
    # file_name ='/Users/danaru/Desktop/organizedData.csv'
    # file_name = './HumanData/ExampleOrganizedData.csv'
    file_name = './HumanData/30OrganizedData.csv'
    human_games = parse_game(file_name, True)

    print(human_games)
    # game_obj_lis = parse_game(file_name, verbose = True)
    # print(len(game_obj_lis))

