import time
from math import inf as infinity
import random
weight = [[1, 1, 3, 1, 1],
		[1, 7, 4, 7, 1],
		[3, 4, 8, 4, 3],
		[1, 7, 4, 7, 1],
		[1, 1, 3, 1, 1]]

starting_move = []

class Board:
	def __init__(self, board):
		self.board = [ [0]*5 for i in range(5)]
		self.ai = 0
		self.op = 0
		for i, row in enumerate(board):
			for j, pos in enumerate(row):
				self.board[i][j] = pos
				if pos == -1:
					self.op += 1
				elif pos == 1:
					self.ai += 1
				else: pass

	def gameover(self):
		r = 0
		for i in range(0,5):
			for j in range(0,5):
				r += self.board[i][j]
		if r == 16 or r == -16 : 
			return True
		else: 
			return False
	def eval(self):
		count_me = 0
		count_player = 0
		for i, row in enumerate(self.board):
			for j, pos in enumerate(row):
				if pos == 1:
					# print(weight[i][j])
					count_me += weight[i][j]
				elif pos == -1:
					# print("-",weight[i][j])
					count_player += weight[i][j]
		# print("/")
		return count_me - count_player

	def possibleDest(self, posY, posX):
		no = posY * 5 + posX
		res = list()
		if no % 2 == 0:
			res = filter(lambda x: 0 <= x[0] < 5 and 0 <= x[1] < 5, [(posY - 1, posX - 1), (posY - 1, posX), (posY - 1, posX + 1), (posY, posX - 1), (posY, posX + 1), (posY + 1, posX - 1), (posY + 1, posX), (posY + 1, posX + 1)])
		else:
			res = filter(lambda x: 0 <= x[0] < 5 and 0 <= x[1] < 5, [(posY - 1, posX), (posY, posX - 1), (posY, posX + 1), (posY + 1, posX)])
		return res

	# Get all Available moves from player (-1 or 1)
	def getAvailableMoves(self, player):
		res = list()
		for i, row in enumerate(self.board):
			for j, pos in enumerate(row):
				if pos == player:
					# Init possible destination of a chess piece:
					dest = self.possibleDest(i, j)
					for index, (destY, destX) in enumerate(dest):
						if self.board[destY][destX] == 0:
							res.append( ((i, j), (destY, destX)) )
		return res

	# Referenced from Go chess
	def liberty(self):
		liberty_map = [[False]*5 for i in range(5)]
		for i, row in enumerate(self.board):
			for j, pos in enumerate(row):
				if pos != 0:
					# First get piece of chess with liberty (air)
					surrounding = self.possibleDest(i, j)
					if any(self.board[place[0]][place[1]] == 0 for place in surrounding):
						liberty_map[i][j] = True

		# Check for group liberty:		
		while(True):
			changed = False
			for i, row in enumerate(liberty_map):
				for j, pos in enumerate(row):
					if self.board[i][j] != 0 and liberty_map[i][j] == False:
						surrounding = self.possibleDest(i, j)
						if any(liberty_map[place[0]][place[1]] == True and self.board[place[0]][place[1]] == self.board[i][j] for place in surrounding):
							liberty_map[i][j] = True
							changed = True
			if changed == False: 
				break
		return liberty_map

	def makeMove(self, src, dest):
		res = Board(self.board)
		chessPiece = res.board[src[0]][src[1]]
		res.board[src[0]][src[1]] = 0
		res.board[dest[0]][dest[1]] = chessPiece

		# Gánh
		if ((dest[0] * 5 + dest[1]) % 2) == 0:
			ganh_listing = filter(lambda x: 0 <= x[0][0] < 5 and 0 <= x[0][1] < 5 and 0 <= x[1][0] < 5 and 0 <= x[1][1] < 5, 
							[((dest[0] - 1, dest[1] - 1), (dest[0] + 1, dest[1] + 1)),
							((dest[0] - 1, dest[1]), (dest[0] + 1, dest[1])),
							((dest[0] - 1, dest[1] + 1), (dest[0] + 1, dest[1] - 1)),
							((dest[0], dest[1] - 1), (dest[0], dest[1] + 1))])
			for x, y in ganh_listing:
				if res.board[x[0]][x[1]] == res.board[y[0]][y[1]]:
					res.board[x[0]][x[1]] = chessPiece
					res.board[y[0]][y[1]] = chessPiece
		else:
			ganh_listing = filter(lambda x: 0 <= x[0][0] < 5 and 0 <= x[0][1] < 5 and 0 <= x[1][0] < 5 and 0 <= x[1][1] < 5, 
							[((dest[0] - 1, dest[1]), (dest[0] + 1, dest[1])),
							((dest[0], dest[1] - 1), (dest[0], dest[1] + 1))])
			for x, y in ganh_listing:
				# print (x[0], x[1], y[0], y[1])
				if res.board[x[0]][x[1]] != 0 and res.board[y[0]][y[1]] != 0 and res.board[x[0]][x[1]] == res.board[y[0]][y[1]]:
					res.board[x[0]][x[1]] = chessPiece
					res.board[y[0]][y[1]] = chessPiece

		# Chẹt
		liberty_map = res.liberty()
		for i, row in enumerate(liberty_map):
			for j, pos in enumerate(row):
				if res.board[i][j] != 0 and pos == False:
					res.board[i][j] = chessPiece

		# Trap Sniffer: No idea :))

		return res

	def isTrapChess(self):

		return False
	def __str__(self):
		res = "[\n"
		for x in self.board:
			res += "["
			for y in x:
				if (y >= 0):
					res += ' ' + str(y) + ', '
				else:
					res += str(y) + ', '
			res += "]\n"
		res += "]"
		return res




def minimax(board, depth, alpha, beta, maximize, player):
	if depth == 0 or board.gameover() : return None, board.eval()
	moves = board.getAvailableMoves(player)
	# for i in moves:
	# 	print(i)
	# best_move = random.choice(moves)
	
	if maximize:
		max_eval = -infinity
		best_move = None
		for move in moves:
			# print("/",move,"/")
			newboard = board
			newboard = newboard.makeMove(move[0],move[1])
			current_eval = minimax(newboard, depth - 1, alpha, beta, False, -player)[1]
			if current_eval > max_eval:
				max_eval = current_eval
				best_move = move
			# alpha = max(alpha, current_eval)
			# if beta <= alpha:
			# 	print("break")
			# 	break
		# print(best_move, max_eval)
		return best_move, max_eval
	else:
		min_eval = infinity
		best_move = None
		for move in moves:
			# print("/",move,"/")
			newboard = board
			newboard = newboard.makeMove(move[0],move[1])
			current_eval = minimax(newboard, depth - 1, alpha, beta, True, -player)[1]
			if current_eval <  min_eval :
				min_eval = current_eval
				best_move = move
			# beta = min(beta, current_eval)
			# if beta <= alpha:
			# 		print("break")
			# 		break
		# print(best_move, min_eval)
		return best_move, min_eval

def move(prev_board, board, player, remain_time_x, remain_time_o):
	if prev_board is None:
		pre_board = [[]]
	if prev_board:
		pre_board = Board(prev_board)
	cur_board = Board(board)
	return minimax(cur_board, 3, infinity, -infinity, True, player)[0]
	
testboard1 = Board([
				[ 1,  0, -1,  0, -1],
				[ 0,  1,  0,  0, -1],
				[-1, -1,  1,  0,  0],
				[ 1,  1, -1, -1, -1],
				[ 1,  0,  0,  1,  1]
			  ])

print(move(None, [[1, 1, 1, 1, 1],
				 [1, 0, 0, 0, 1],
				 [1, 0, 0, 0, -1],
				 [-1, 0, 0, 0, -1],
				 [-1, -1, -1, -1, -1]]
, -1, 0, 0)
)

# print(move([
# 			[ 1,  0, 0,  -1, -1],
#  			[ 0,  1,  0,  0, -1],
#  			[-1, -1,  1,  0,  0],
#  			[ 1,  1, -1, -1, -1],
#  			[ 1,  0,  0,  1,  1]
#  			]
#     ,[
# 			[ 1,  0, -1,  0, -1],
#  			[ 0,  1,  0,  0, -1],
#  			[-1, -1,  1,  0,  0],
#  			[ 1,  1, -1, -1, -1],
#  			[ 1,  0,  0,  1,  1]
#  			]
# 			,1,9,9))
# print(testboard1)
# print(testboard1.makeMove((1,1), (1,2)))

# testboard1 = Board([
# 				[ 1,  0, -1,  0, -1],
#  				[ 0,  1,  0,  0, -1],
#  				[-1, -1,  1,  0,  0],
#  				[ 1,  1, -1, -1, -1],
#  				[ 1,  0,  0,  1,  1]
#  			  ])
# newboard = testboard1
# print("=============================================================")
# print("Testboard1: Chẹt/Vây")
# print(testboard1)
# print("Move from (0, 0) to (1, 0)")
# start = time.perf_counter()
# print(testboard1.makeMove((0,0), (1,0)))
# end = time.perf_counter()
# print(newboard)
# print("Chẹt ended in", end - start, "seconds")

# print("\n=============================================================")
# testboard2 = Board([
# 				[ 0,  0, -1,  0, -1],
#  				[ 1,  1,  0,  0, -1],
#  				[ 1,  1,  1,  0,  0],
#  				[ 1,  0,  1, -1, -1],
#  				[ 1, -1,  1,  0, -1]
#  			  ])
# print("Testboard2: Gánh")
# print(testboard2)
# print("Move from (4, 1) to (3, 1)")
# start = time.perf_counter()
# print(testboard2.makeMove((4,1), (3,1)))
# end = time.perf_counter()
# print("Gánh ended in", end - start, "seconds")