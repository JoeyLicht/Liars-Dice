from model import *
from agents import *
from parse import *
import matplotlib.pyplot as plt
import os
import numpy as np

def plot_games(human_games, main_save_folder, human = True):
    """
    human_games: list of LiarsDiceGame objects

    Wrapper function to plot games in human_games using plot_game()
    """
    # save_root = './Results/'
    # run = 1
    # main_save_folder = save_root + f'run{run}'
    # while os.path.exists(main_save_folder):
    #     run += 1
    #     main_save_folder = save_root + f'run{run}'
    # #create save folder
    # os.makedirs(main_save_folder)

    challenge_values = []
    non_challenge_values = []
    challenge_implied_bluffs = []
    non_challenge_implied_bluffs = []
    num_dice_num_bids_dict = {}
    diff_dice_num_bids_dict = {}
    info_advantage_dict = {}
    for game_num, game_obj in enumerate(human_games):
        
        
        readable_game_number = game_num + 1
        print(f"game: {readable_game_number}")
            
        game_stats = plot_game(game_obj, "Me", "Subject", main_save_folder, readable_game_number, plot = human)
        challenge_values += game_stats["challenge_probs"]
        non_challenge_values += game_stats["non_challenge_probs"]
        challenge_implied_bluffs += game_stats["challenge_implied_bluffs"]
        non_challenge_implied_bluffs += game_stats["non_challenge_implied_bluffs"]
        combine_dicts(num_dice_num_bids_dict, game_stats["num_dice_num_bids"])
        combine_dicts(diff_dice_num_bids_dict, game_stats["diff_dice_num_bids"])
        combine_dicts(info_advantage_dict, game_stats["info_advantage"])
        # if game_num == 2:
        #     break
    
    plot_challenge_hist(challenge_values, non_challenge_values, main_save_folder, bluffs = False, human = human)
    plot_challenge_hist(challenge_implied_bluffs, non_challenge_implied_bluffs, main_save_folder, bluffs = True, human=human)

    # plt_name = main_save_folder + f'/num_dice_num_bids.png'
    # plot_dict(num_dice_num_bids_dict, "Human Data: Distribution of Number of Bids (Split by Total Dice on Board)", "Number of Bids", "Frequency", plt_name, "Total Dice on Board")
    # plt_name = main_save_folder + f'/diff_dice_num_bids.png'
    # plot_dict(diff_dice_num_bids_dict, "Human Data: Distribution of Number of Bids (Split by difference in Player Hands lengths)", "Number of Bids", "Frequency", plt_name, "Difference in Hands Length")
    print(f"saved to {main_save_folder}")
    return (num_dice_num_bids_dict, diff_dice_num_bids_dict, info_advantage_dict)

def combine_dicts(main, addition):
    for key, values in addition.items():
        if key in main:
            main[key].extend(values)
        else:
            main[key] = values

def plot_dict(dict_, title, xlabel, ylabel, plt_name, legend_name):
    # Plotting the histogram
    # plt.figure(figsize=(10, 6))
    # for key, values in dict_.items():
    #     plt.hist(values, label=str(key), alpha=0.7)
    # plt.title(title)
    # plt.xlabel(xlabel)
    # plt.ylabel(ylabel)
    # plt.legend(title=legend_name)
    # plt.savefig(plt_name + "_histogram.png")
    # plt.show()

    # Plotting the mean values with annotations
    plt.figure(figsize=(10, 6))
    means = {key: np.mean(values) for key, values in dict_.items()}
    bars = plt.bar(range(len(means)), means.values())
    plt.title("Mean of " + title)
    plt.xlabel(legend_name)
    plt.ylabel("Mean Values")

    # Set x-ticks
    plt.xticks(range(len(means)), means.keys())

    # Adding the y-value annotations on top of each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

    plt.savefig(plt_name + "_mean.png")
    # plt.show()

def plot_dicts(dicts, title, xlabel, ylabel, plt_name, legend_names):
    plt.figure(figsize=(10, 6))

    # Colors for the plots
    colors = ['red', 'blue', 'green']
    
    # Check if the list of legend names matches the list of dictionaries
    if len(legend_names) != len(dicts):
        raise ValueError("The number of legend names must match the number of dictionaries")

    for idx, dict_ in enumerate(dicts):
        # Calculate means
        means = {key: np.mean(values) for key, values in dict_.items()}
        
        # Create an offset for bars to avoid overlap
        offset = 0.2 * idx
        
        # Create bars for each dictionary
        bars = plt.bar([x + offset for x in range(len(means))], means.values(), width=0.2, color=colors[idx], label=legend_names[idx])
        
        # Adding the y-value annotations on top of each bar
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), ha='center', va='bottom')

    # Set chart title and labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Adjust x-ticks to be in the center of grouped bars
    if dicts:
        plt.xticks([r + offset/2 for r in range(len(dicts[0]))], list(dicts[0].keys()))

    # Add legend
    plt.legend(title="Legend")

    # Save and show plot
    plt.savefig(plt_name)
    # plt.show()


def plot_challenge_hist(challenge_values, non_challenge_values, main_save_folder, bluffs = False, human = True):
    plt.figure(figsize=(10, 6))
    plt.hist(non_challenge_values, bins=10, edgecolor='black', color = 'b', alpha = 0.8, label='Non-Challenge')
    plt.hist(challenge_values, bins=10, edgecolor='black', color = 'r', alpha=0.7, label='Challenge')
    mean_challenge = sum(challenge_values) / len(challenge_values)
    mean_non_challenge = sum(non_challenge_values) / len(non_challenge_values)
    plt.axvline(mean_challenge, color='r', linestyle='dashed', linewidth=2, label=f'Mean Challenge: {round(mean_challenge, 2)}')
    plt.axvline(mean_non_challenge, color='b', linestyle='dashed', linewidth=2, label=f'Mean Non-Challenge: {round(mean_non_challenge, 2)}')
    
    if human:
        descriptor = "Human Data"
    else:
        descriptor = "100 Simulated Games"
    # Add labels and title
    if not bluffs:
        plt.xlabel('Probability that a Bid is Correct')
        plt.ylabel('Frequency')
        plt.title(f'{descriptor} Distribution of Observer Probabilities that Bid is Correct')
        specific_name = f'challenge_hist.png'
    else:
        plt.xlabel("Bid Aggressiveness: (Total Board Quantity - Quantity In Bidder's Hand Equal to Bid Value) / Total Board Quantity")
        plt.ylabel('Frequency')
        plt.title(f'{descriptor} Distribution of Bid Aggressiveness')
        specific_name = f'aggressiveness_hist.png'
        
    
    if human:
        specific_name = f'/human_{specific_name}'
    else:
        specific_name = f'/simulated_{specific_name}'

    plt_name = main_save_folder + specific_name


    plt.legend()
    plt.savefig(plt_name)

    # Show or save the plot
    # plt.show() 
    print(f"saved to {main_save_folder}")


def plot_game(game_obj, player1_name, player2_name, game_save_folder, game_number, plot = True):
    """
    game_obj: LiarsDiceGame object
    player1_name: str player1's name
    player2_name: str player2's name
    game_save_folder: str of folder to save to
    game_number: int of the game number being played
    """

    game_stats = {"challenge_probs": [], "non_challenge_probs": [], 
                  "challenge_implied_bluffs": [], "non_challenge_implied_bluffs": [],
                  "num_dice_num_bids": {},
                  "diff_dice_num_bids": {},
                  "info_advantage": {},
                  }

    history = game_obj.game_history
    for round_num in history:
        if plot:
            plt.figure(figsize=(10, 6))

        actions = history[round_num]['Actions']
        if len(actions) > 0:
            
            hand1_dict = history[round_num]['Hands'][player1_name]
            hand2_dict = history[round_num]['Hands'][player2_name]
            hand_1_num_dice = len(dice_dict_to_sorted_list(hand1_dict))
            hand_2_num_dice = len(dice_dict_to_sorted_list(hand2_dict))
            hand1 = LiarsDiceHand(player1_name, hand1_dict, hand_2_num_dice)
            hand2 = LiarsDiceHand(player2_name, hand2_dict, hand_1_num_dice)
            if round_num == 1:
                modelGame = LiarsDiceGame(hand1, hand2)
            else:
                modelGame.overide_hand(hand1, hand2)

            num_bids = len(actions) - 1
            num_dice = len(hand1) + len(hand2)
            diff_dice = abs(len(hand1) - len(hand2))
            if num_dice in game_stats["num_dice_num_bids"]:
                game_stats["num_dice_num_bids"][num_dice].append(num_bids)
            else:
                game_stats["num_dice_num_bids"][num_dice] = [num_bids]

            if diff_dice in game_stats["diff_dice_num_bids"]:
                game_stats["diff_dice_num_bids"][diff_dice].append(num_bids)
            else:
                game_stats["diff_dice_num_bids"][diff_dice] = [num_bids]
            

            observing_probabilities = []
            bidding_probabilities = []
            bidder_label = []
            observer_label = []
            observing_bluff_probabilities = []
            implied_bluffs = []
            for action_lis in actions:
                action, acting_player_name, quantity, value, correct = action_lis
                if action == "Bid":
                    bid = Bid(int(quantity), int(value))
                    if acting_player_name == player1_name:
                        bidder_hand_object = hand1
                        observer_hand_object = hand2  
                        player1_observer = False  
                    elif acting_player_name == player2_name:
                        bidder_hand_object = hand2
                        observer_hand_object = hand1
                        player1_observer = True
                    else:
                        raise NameError(f"Invalid names")
                    
                    observer_expected_opponent_bluff_prob = observer_hand_object.expected_opponent_bluff_prob()
                    rounded_observer_expected_opponent_bluff_prob = round(observer_expected_opponent_bluff_prob, 2)
                    observing_bluff_probabilities.append(rounded_observer_expected_opponent_bluff_prob)
                    observer_prob_bid_correct = observer_hand_object.compute_conditional_probability_correct(bid, observer_expected_opponent_bluff_prob)
                    observing_probabilities.append(observer_prob_bid_correct)
                    bidder_prob_bid_correct = bidder_hand_object.compute_truthful_probability_correct(bid)
                    bidding_probabilities.append(bidder_prob_bid_correct)
                    
                    # int_implied_bluffs = int(bid.bid_quantity - bidder_hand_object.compute_expected_board_quantities()[bid.bid_value])
                    int_implied_bluffs = int(bid.bid_quantity - bidder_hand_object.user_dice_dict[bid.bid_value])
                    implied_bluffs_percentage = int_implied_bluffs / (len(bidder_hand_object) + len(observer_hand_object))
                    # bidder_non_value_dice = len(bidder_hand_object) - bidder_hand_object.user_dice_dict[bid.bid_value]
                    # bidder_implied_bluff_prob = implied_bluffs / bidder_non_value_dice
                    implied_bluffs.append(implied_bluffs_percentage)

                    bid_str = f'({bid.bid_quantity}, {bid.bid_value}, {modelGame.correct_bid(bid)})'
                    if player1_observer:
                        bidder_label.append(f"{player2_name}: {bid_str}")
                        observer_label.append(f"{player1_name}: {rounded_observer_expected_opponent_bluff_prob}")
                    else:
                        bidder_label.append(f"{player1_name}: {bid_str}")
                        observer_label.append(f"{player2_name}: {rounded_observer_expected_opponent_bluff_prob}")
                elif action == "Challenge":
                    if acting_player_name == player1_name:
                        challanger_hand_object = hand1
                        bidder_hand_object = hand2
                    elif acting_player_name == player2_name:
                        challanger_hand_object = hand2
                        bidder_hand_object = hand1
                    challenger_bluff_prob = challanger_hand_object.expected_opponent_bluff_prob()
                    challenger_prob_bid_correct = challanger_hand_object.compute_conditional_probability_correct(bid, challenger_bluff_prob)
                    game_stats["challenge_probs"].append(challenger_prob_bid_correct)
                    game_stats["non_challenge_probs"] += observing_probabilities[:-1]
                    game_stats["challenge_implied_bluffs"].append(implied_bluffs[-1])
                    game_stats["non_challenge_implied_bluffs"] += implied_bluffs[:-1]

                    if correct:
                        winner_hand_object = challanger_hand_object
                        loser_hand_object = bidder_hand_object
                    else:
                        winner_hand_object = bidder_hand_object
                        loser_hand_object = challanger_hand_object

                    
                    diff_dice = abs(len(winner_hand_object) - len(loser_hand_object))
                    if len(winner_hand_object) >= len(loser_hand_object):
                        information_advandage_winner = 1
                    else:
                        information_advandage_winner = 0

                    if diff_dice != 0:
                        if diff_dice in game_stats["info_advantage"]:
                            game_stats["info_advantage"][diff_dice].append(information_advandage_winner)
                        else:
                            game_stats["info_advantage"][diff_dice] = [information_advandage_winner]
                            

                else:
                    raise NameError(f"Invalid action")

            if plot:
                plt.plot(range(1, len(observing_probabilities) + 1), observing_probabilities, marker='o', label=f"Observer - Observing_player: observer's estimation of bid_player_bluff_probability")
                plt.plot(range(1, len(bidding_probabilities) + 1), bidding_probabilities, marker='o', label=f'Bidder -  Bidding_player: (bid quantity, bid value, bid true?)')
                for i, bid_label in enumerate(bidder_label):
                    x = i + 1  # Adjust x-coordinate for the bid_label
                    y = bidding_probabilities[i]  # y-coordinate from your data
                    plt.text(x, y, bid_label, ha='center', va='bottom')  # Adjust alignment as needed
                for i, obs_label in enumerate(observer_label):
                    x = i + 1  # Adjust x-coordinate for the obs_label
                    y = observing_probabilities[i]  # y-coordinate from your data
                    plt.text(x, y, obs_label, ha='center', va='top')  # Adjust alignment as needed

                plt.xlabel('Bid Number')
                plt.ylabel('Probability Bid Correct')
                plt.title(f'Game {game_number}, Round {round_num} Probability Bid Correct. \n {player1_name} hand ({hand_1_num_dice} dice) = {hand1_dict}, \n {player2_name} hand ({hand_2_num_dice} dice) = {hand2_dict}')
                plt.grid(True)
                plt.xticks(range(0, 8))
                plt.yticks([i * 0.1 for i in range(11)])
                plt.legend()  # This adds the legend with round_num numbers
                
                plt_name = os.path.join(game_save_folder, f"round_level/Game_{game_number}_Round_{round_num}_Bid_Probs.png")  # Use an appropriate file extension
                plt.savefig(plt_name)
                plt.close()
           
    return game_stats



if __name__ == "__main__":
    # plt.close()
    
    save_root = './Results/'
    run = 1
    main_save_folder = save_root + f'run{run}'
    while os.path.exists(main_save_folder):
        run += 1
        main_save_folder = save_root + f'run{run}'
    #create save folder
    os.makedirs(main_save_folder)
    os.makedirs(f'{main_save_folder}/round_level')
    
    file_name = './HumanData/30OrganizedData.csv'
    human_games = parse_game(file_name, True)

    human_num_dice_num_bids_dict, human_diff_dice_num_bids_dict, human_info_advantage_dict = plot_games(human_games, main_save_folder, human = True)

    
    player1_name = "Me"
    player2_name = "Subject"
    simulated_games = []

    for i in range(100):
        simulated_games.append(simulate_game(player1_name, player2_name, "conditional"))
    simulated_num_dice_num_bids_dict, simulated_diff_dice_num_bids_dict, simulated_info_advantage_dict = plot_games(simulated_games, main_save_folder, human = False)


    
    plt_name = main_save_folder + f'/num_dice_num_bids.png'
    legend_names = ["Human", "100 Simulated Games"]
    plot_dicts([human_num_dice_num_bids_dict, simulated_num_dice_num_bids_dict], "Mean Number of Bids Per Round (Split by Total Dice on Board)", "Total Dice on Board", "Mean Number Of Bids Per Round", plt_name, legend_names)
    plt_name = main_save_folder + f'/diff_dice_num_bids.png'
    plot_dicts([human_diff_dice_num_bids_dict, simulated_diff_dice_num_bids_dict], "Mean Number of Bids Per Round (Split by Difference in Player Hand Lengths)", "Difference in Hand Lengths", "Mean Number of Bids Per Round", plt_name, legend_names)

    plt_name = main_save_folder + f'/info_advantage.png'
    plot_dicts([human_info_advantage_dict, simulated_info_advantage_dict], "Percent of Rounds Won By Player with Informational Advantage (More Dice Than Opponent)", "Difference in Hand Lengths", "Percent of Rounds Won", plt_name, legend_names)
