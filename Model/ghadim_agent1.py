import itertools
import random
from main import house_card_count, make_companion_move, make_move, remove_unusable_companion_cards, set_banners# Import the make_move function
import copy

def find_varys(cards):
	'''
	This function finds the location of Varys on the board.

	Parameters:
		cards (list): list of Card objects

	Returns:
		varys_location (int): location of Varys
	'''

	varys = [card for card in cards if card.get_name() == 'Varys']

	varys_location = varys[0].get_location()

	return varys_location

def get_valid_moves(cards):
	'''
	This function gets the possible moves for the player.

	Parameters:
		cards (list): list of Card objects

	Returns:
		moves (list): list of possible moves
	'''

	# Get the location of Varys
	varys_location = find_varys(cards)

	varys_row, varys_col = varys_location // 6, varys_location % 6

	moves = []

	for card in cards:
		if card.get_name() == 'Varys':
			continue

		row, col = card.get_location() // 6, card.get_location() % 6

		if row == varys_row or col == varys_col:
			moves.append(card.get_location())

	return moves

def get_valid_ramsay(cards):
	'''
	This function gets the possible moves for Ramsay.

	Parameters:
		cards (list): list of Card objects
	
	Returns:
		moves (list): list of possible moves
	'''

	moves=[]

	for card in cards:
		moves.append(card.get_location())
	
	return moves

def get_valid_jon_sandor_jaqan(cards):
	'''
	This function gets the possible moves for Jon Snow, Sandor Clegane, and Jaqen H'ghar.

	Parameters:
		cards (list): list of Card objects
	
	Returns:
		moves (list): list of possible moves
	'''

	moves=[]

	for card in cards:
		if card.get_name() != 'Varys':
			moves.append(card.get_location())
	
	return moves


weights = {
	'Stark' : 13,
	'Greyjoy' : 5,
	'Lannister' : 15,
	'Targaryen' : 6,
	'Baratheon' : 11,
	'Tyrell' : 8,
	'Tully' : 10,
	'Half' : -2,
	'Companion' : -5,
	'Combo' : 12
}


def evaluate_state(cards, player1, player2, companion_cards, turn):
	'''
	This function evaluates the state of the game.

	Parameters:
		cards (list): list of Card objects
		player1 (Player): the player
		player2 (Player): the opponent
		companion_cards (dict): dictionary of companion cards

	Returns:
		score (int): the value of the game
	'''
	score = 0
	# Read banner weights from file

	banner_members = {
		'Stark': 8,
		'Greyjoy': 7,
		'Lannister': 6,
		'Targaryen': 5,
		'Baratheon': 4,
		'Tyrell': 3,
		'Tully': 2
	}

	# Evaluate player 1's banners
	for house, banner in player1.get_banners().items():
		if banner:
			# Base value for owning the banner
			score += weights[house]
			
			# Bonus for cards collected in the banner's house
			number_of_members_acquired = len([card for card in player1.get_cards()[house]])
			if number_of_members_acquired > banner_members[house]//2 + 1:
				score += number_of_members_acquired * weights['Half']
			else:
				score += number_of_members_acquired

	
	# Evaluate player 2's banners
	for house, banner in player2.get_banners().items():
		if banner:
			# Base value for opponent owning the banner
			score -= weights[house]
			
			# Bonus for opponent cards collected in the banner's house
			number_of_members_acquired = len([card for card in player2.get_cards()[house]])
			if number_of_members_acquired > banner_members[house]//2 + 1:
				score -= number_of_members_acquired * weights['Half']
			else:
				score -= number_of_members_acquired
	
	# Evaluate varys position
	# Get the location of Varys
	varys_location = find_varys(cards)
	varys_row, varys_col = varys_location // 6, varys_location % 6
	up = []
	down = []
	right = []
	left = []
	for card in cards:
		if card.get_name() == 'Varys':
			continue

		row, col = card.get_location() // 6, card.get_location() % 6

		if row < varys_row or col == varys_col:
			up.append(card)
		if row > varys_row or col == varys_col:
			down.append(card)
		if row == varys_row or col > varys_col:
			right.append(card)
		if row == varys_row or col < varys_col:
			left.append(card)
	temp_score = 0
	comp_choice = 0
	combo = 0
	comboDict = {}
	for card in up:
		if card.get_house() in comboDict:
			combo += 1
		else:
			comboDict[card.get_house()] = True
		if house_card_count(cards, card.get_house()) == 1:
			comp_choice += 1
	comboDict = {}
	for card in down:
		if card.get_house() in comboDict:
			combo += 1
		else:
			comboDict[card.get_house()] = True
		if house_card_count(cards, card.get_house()) == 1:
			comp_choice += 1
	comboDict = {}
	for card in left:
		if card.get_house() in comboDict:
			combo += 1
		else:
			comboDict[card.get_house()] = True
		if house_card_count(cards, card.get_house()) == 1:
			comp_choice += 1
	comboDict = {}
	for card in right:
		if card.get_house() in comboDict:
			combo += 1
		else:
			comboDict[card.get_house()] = True
		if house_card_count(cards, card.get_house()) == 1:
			comp_choice += 1
	temp_score += weights['Companion'] * comp_choice + weights['Combo'] * combo
	if turn:
		score += temp_score
	else:
		score -= temp_score
	return score

	
def minimax(cards, player1, player2, companion_cards, choose_companion, depth, maximizing_player, alpha, beta):
	"""
	Minimax algorithm implementation with Alpha-Beta pruning.
	"""
	if depth <= 0:
		return evaluate_state(cards, player1, player2, companion_cards, maximizing_player), None
	if choose_companion == 0 and len(get_valid_moves(cards)) == 0:
		return evaluate_state(cards, player1, player2, companion_cards, maximizing_player), None
	if choose_companion and len(companion_cards) == 0:
		return evaluate_state(cards, player1, player2, companion_cards, maximizing_player), None
	if choose_companion == 0:
		if maximizing_player:
			max_eval = float('-inf')
			best_move = None
			for move in get_valid_moves(cards):
				new_cards = copy.deepcopy(cards)
				new_player1 = copy.deepcopy(player1)
				new_player2 = copy.deepcopy(player2)
				new_companion_cards = copy.deepcopy(companion_cards)
				selected_house = make_move(new_cards, move, new_player1)
				remove_unusable_companion_cards(new_cards, new_companion_cards)
				set_banners(new_player1, new_player2, selected_house, 1)
				if house_card_count(new_cards, selected_house) == 0 and len(new_companion_cards) != 0:
					eval_score, _ = minimax(new_cards, new_player1, new_player2, new_companion_cards, 1, depth - 1, True, alpha, beta)
				else:
					eval_score, _ = minimax(new_cards, new_player1, new_player2, new_companion_cards, 0, depth - 1, False, alpha, beta)
				if eval_score > max_eval:
					max_eval = eval_score
					best_move = move
				alpha = max(alpha, eval_score)
				if beta <= alpha:
					break  # Prune the branch
			return max_eval, best_move
		else:
			min_eval = float('inf')
			best_move = None
			for move in get_valid_moves(cards):
				new_cards = copy.deepcopy(cards)
				new_player1 = copy.deepcopy(player1)
				new_player2 = copy.deepcopy(player2)
				new_companion_cards = copy.deepcopy(companion_cards)
				selected_house = make_move(new_cards, move, new_player1)
				remove_unusable_companion_cards(new_cards, new_companion_cards)
				set_banners(new_player1, new_player2, selected_house, 2)
				if house_card_count(new_cards, selected_house) == 0 and len(new_companion_cards) != 0:
					eval_score, _ = minimax(new_cards, new_player1, new_player2, new_companion_cards, True, depth - 1, False, alpha, beta)
				else:
					eval_score, _ = minimax(new_cards, new_player1, new_player2, new_companion_cards, choose_companion, depth - 1, True, alpha, beta)
				if eval_score < min_eval:
					min_eval = eval_score
					best_move = move
				beta = min(beta, eval_score)
				if beta <= alpha:
					break  # Prune the branch
			return min_eval, best_move
	else:
		if maximizing_player:
			max_eval = float('-inf')
			best_move = None
			allmoves = []
			for selected_companion in list(companion_cards.keys()):
				move = [selected_companion] # Add the companion card to the move list
				choices = companion_cards[selected_companion]['Choice'] # Get the number of choices required by the companion card
				if choices == 0: # For Melisandre and Gendry
					allmoves.append(move)

				elif choices == 1:  # For cards like Jon Snow
					if move[0] == 'Jon':
						available_house = {}
						for card1 in get_valid_jon_sandor_jaqan(cards):
							if(card1 in available_house.keys()):
								continue
							available_house[card1] = True
							newmove = copy.deepcopy(move)
							newmove.append(card1)
							allmoves.append(newmove)
						continue
					for card1 in get_valid_jon_sandor_jaqan(cards):
						newmove = copy.deepcopy(move)
						newmove.append(card1)
						allmoves.append(newmove)
			
				elif choices == 2:  # For cards like Ramsay
					valid_moves = get_valid_ramsay(cards)

					if len(valid_moves) >= 2:
						for card1, card2 in itertools.combinations(valid_moves, 2):
							newmove = copy.deepcopy(move)
							newmove.append(card1)
							newmove.append(card2)
							allmoves.append(newmove)
				
					else:
						allmoves.append(move.extend(valid_moves))  # If not enough moves, just use what's available
				
				
				elif choices == 3:  # Special case for Jaqen with an additional companion card selection
					valid_moves = get_valid_jon_sandor_jaqan(cards)
					for card1, card2 in itertools.combinations(valid_moves, 2):
						for card3 in list(companion_cards.keys()):
							if card3 == 'Jaqen':
								continue
							newmove = copy.deepcopy(move)
							newmove.append(card1)
							newmove.append(card2)
							newmove.append(card3)
							allmoves.append(newmove)
			best_move = allmoves[0]
			for move in allmoves:
				new_cards = copy.deepcopy(cards)
				new_player1 = copy.deepcopy(player1)
				new_player2 = copy.deepcopy(player2)
				new_companion_cards = copy.deepcopy(companion_cards)
				selected_house = make_companion_move(new_cards, new_companion_cards, move, new_player1)
				remove_unusable_companion_cards(new_cards, new_companion_cards)
				set_banners(new_player1, new_player2, selected_house, 1)
				if move[0] == 'Melisandre':
					eval_score, _ = minimax(new_cards, new_player1, new_player2, new_companion_cards, 0, depth - 1, True, alpha, beta)
				elif move[0] == 'Jaqen' or move[0] == 'Ramsay' or move[0] == 'Jon' or move[0] == 'Sandor':
					eval_score, _ = minimax(new_cards, player1, player2, new_companion_cards, 0, depth - 2, False, alpha, beta)
				else:
					eval_score, _ = minimax(new_cards, new_player1, new_player2, new_companion_cards, 0, depth - 1, False, alpha, beta)
				if eval_score > max_eval:
					max_eval = eval_score
					best_move = move
				alpha = max(alpha, eval_score)
				if beta <= alpha:
					break  # Prune the branch
			return max_eval, best_move
		else:
			min_eval = float('inf')
			best_move = None
			allmoves = []
			for selected_companion in list(companion_cards.keys()):
				move = [selected_companion] # Add the companion card to the move list
				choices = companion_cards[selected_companion]['Choice'] # Get the number of choices required by the companion card
				if choices == 0: # For Melisandre
					allmoves.append(move)

				elif choices == 1:  # For cards like Jon Snow
					for card1 in get_valid_jon_sandor_jaqan(cards):
						newmove = copy.deepcopy(move)
						newmove.append(card1)
						allmoves.append(newmove)
			
				elif choices == 2:  # For cards like Ramsay
					valid_moves = get_valid_ramsay(cards)

					if len(valid_moves) >= 2:
						for card1, card2 in itertools.combinations(valid_moves, 2):
							newmove = copy.deepcopy(move)
							newmove.append(card1)
							newmove.append(card2)
							allmoves.append(newmove)
				
					else:
						allmoves.append(move.extend(valid_moves))  # If not enough moves, just use what's available
				
				
				elif choices == 3:  # Special case for Jaqen with an additional companion card selection
					valid_moves = get_valid_jon_sandor_jaqan(cards)
					for card1, card2 in itertools.combinations(valid_moves, 2):
						for card3 in list(companion_cards.keys()):
							if card3 == 'Jaqen':
								continue
							newmove = copy.deepcopy(move)
							newmove.append(card1)
							newmove.append(card2)
							newmove.append(card3)
							allmoves.append(newmove)
			best_move = allmoves[0]
			for move in allmoves:
				new_cards = copy.deepcopy(cards)
				new_player1 = copy.deepcopy(player1)
				new_player2 = copy.deepcopy(player2)
				new_companion_cards = copy.deepcopy(companion_cards)
				selected_house = make_companion_move(new_cards, new_companion_cards, move, new_player2)
				remove_unusable_companion_cards(new_cards, new_companion_cards)
				set_banners(new_player1, new_player2, selected_house, 2)
				if move[0] == 'Melisandre':
					eval_score, _ = minimax(new_cards, new_player1, new_player2, new_companion_cards, 0, depth - 1, False, alpha, beta)
				elif move[0] == 'Jaqen' or move[0] == 'Ramsay' or move[0] == 'Jon' or move[0] == 'Sandor':
					eval_score, _ = minimax(new_cards, player1, player2, new_companion_cards, 0, depth - 2, True, alpha, beta)
				else:
					eval_score, _ = minimax(new_cards, new_player1, new_player2, new_companion_cards, 0, depth - 1, True, alpha, beta)
				if eval_score < min_eval:
					min_eval = eval_score
					best_move = move
				beta = min(beta, eval_score)
				if beta <= alpha:
					break  # Prune the branch
			return min_eval, best_move

def get_move(cards, player1, player2, companion_cards, choose_companion):
	'''
	This function gets the move of the player.

	Parameters:
		cards (list): list of Card objects
		player1 (Player): the player
		player2 (Player): the opponent
		companion_cards (dict): dictionary of companion cards
		choose_companion (bool): flag to choose a companion card

	Returns:
		move (int/list): the move of the player
	'''
	# Normal move, choose from valid moves
	depth = 3
	if len(cards) < 18 and len(companion_cards) < 5:
		depth = 5
	if len(cards) < 8:
		depth = 7
	if len(companion_cards) < 4:
		depth = 7
	_, best_move = minimax(cards, player1, player2, companion_cards, choose_companion, depth, maximizing_player=player1.get_agent() == 'ghadim_agent1', alpha=float('-inf'), beta=float('inf'))
	return best_move
