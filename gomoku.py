import numpy as np
import sys, pygame
import math, time
from time import sleep
import random

BOARD_SIZE = 15
IN_A_ROW = 5
game = True
BLANK = 0
PLAYER_PIECE = 1
BOT_PIECE = 2
YELLOW = (255, 219, 34)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (225, 20, 20)

def build_board():
    board = np.zeros((BOARD_SIZE, BOARD_SIZE))
    return board

def draw_board(board):
    screen.fill(YELLOW)
    for col in range(BOARD_SIZE - 1):
        for row in range(BOARD_SIZE - 1):
            pygame.draw.rect(screen, BLACK, ((col*squaresize + padding), (row*squaresize + padding), squaresize, squaresize), 1)
    
    for col in range(BOARD_SIZE):
        for row in range(BOARD_SIZE):        
            if board [row][col] == 1:
                pygame.draw.circle(screen, BLACK, (col*squaresize + padding, row*squaresize + padding), radius)
            elif board [row][col] == 2:
                pygame.draw.circle(screen,  WHITE, (col*squaresize + padding, row*squaresize + padding), radius)
    pygame.display.update()

def winning_move(board, piece):
    # check horizontally
    for row in range(BOARD_SIZE):
         for column in range(BOARD_SIZE - (IN_A_ROW - 1)):
             if board[row][column] == piece and board[row][column+1] == piece and board[row][column+2] == piece and board[row][column+3] == piece and board[row][column+4] == piece:
                for i in range(IN_A_ROW):
                    pygame.draw.circle(screen,  RED, ((column + i)*squaresize + padding, row*squaresize + padding), radius, 3)
                    pygame.display.update()
                return True

    # check vertically
    for column in range(BOARD_SIZE):
         for row in range(BOARD_SIZE - (IN_A_ROW - 1)):
             if board[row][column] == piece and board[row+1][column] == piece and board[row+2][column] == piece and board[row+3][column] == piece and board[row+4][column] == piece:
                for i in range(IN_A_ROW):
                    pygame.draw.circle(screen,  RED, (column*squaresize + padding, (row + i)*squaresize + padding), radius, 3)
                    pygame.display.update()
                return True
    
    # check positive diagonals
    for column in range(BOARD_SIZE - (IN_A_ROW - 1)):
         for row in range(BOARD_SIZE - (IN_A_ROW - 1)):
             if board[row][column] == piece and board[row+1][column+1] == piece and board[row+2][column+2] == piece and board[row+3][column+3] == piece and board[row+4][column+4] == piece:
                for i in range(IN_A_ROW):
                    pygame.draw.circle(screen,  RED, ((column + i)*squaresize + padding, (row + i)*squaresize + padding), radius, 3)
                    pygame.display.update()
                return True

    # check negative diagonals
    for column in range(BOARD_SIZE - (IN_A_ROW - 1)):
         for row in range((IN_A_ROW-1), BOARD_SIZE):
             if board[row][column] == piece and board[row-1][column+1] == piece and board[row-2][column+2] == piece and board[row-3][column+3] == piece and board[row-4][column+4] == piece:
                for i in range(IN_A_ROW):
                    pygame.draw.circle(screen,  RED, ((column + i)*squaresize + padding, (row - i)*squaresize + padding), radius, 3)
                    pygame.display.update()
                return True

def get_valid_locations(board):
    valid_location_list = []
    for row in range (BOARD_SIZE):
        for col in range (BOARD_SIZE):
            if board[row][col] == 0:
                valid_location_list.append((row,col))

    return valid_location_list

def window_scoring(window, piece):
    if piece == BOT_PIECE:
        opponent_piece = PLAYER_PIECE
    else:
        opponent_piece = BOT_PIECE

    score = 0
    if window.count(piece) == IN_A_ROW:
                score += 1000
    elif window.count(piece) == (IN_A_ROW-1) and window.count(BLANK) == 1:
                score += 50
    elif window.count(opponent_piece) == (IN_A_ROW-1) and window.count(BLANK) == 1:
                score -= 70
    elif window.count(piece) == (IN_A_ROW-2) and window.count(BLANK) == 2:
                score += 15
    elif window.count(opponent_piece) == (IN_A_ROW-2) and window.count(BLANK) == 2:
                score -= 30

    return score

def score_position(board, piece):
    score = 0
    center_array = []
    # center scoring
    center_point = BOARD_SIZE // 2 + 1
    lower, upper = (center_point-2), (center_point+1)
    for c in range (lower, upper):
        for r in range (lower, upper):
            center_array.append(board[r][c])
    center_count = center_array.count(piece)
    score += center_count * 10

    # horizontal scoring
    for r in range(BOARD_SIZE):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range (BOARD_SIZE - (IN_A_ROW-1)):
            window = row_array[c:c + IN_A_ROW]
            score += window_scoring(window, piece)

    # vertical scoring
    for c in range(BOARD_SIZE):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(BOARD_SIZE - (IN_A_ROW-1)):
            window = col_array[r:r + IN_A_ROW]
            score += window_scoring(window, piece)

    #positive diagonal
    for r in range((IN_A_ROW-1), BOARD_SIZE):
        for c in range (BOARD_SIZE - (IN_A_ROW-1)):
            window = []
            for i in range (0, IN_A_ROW):
                window.append(board[r-i][c+i])
            score += window_scoring(window, piece)
    #negative diagonal
    for r in range(BOARD_SIZE - (IN_A_ROW-1)):
        for c in range(BOARD_SIZE - (IN_A_ROW-1)):
            window = []
            for i in range (0, IN_A_ROW):
                window.append(board[r+i][c+i])
            score += window_scoring(window, piece)

    return score

def minimax(board, depth, alpha, beta, maximizingPlayer):
    # [score, row, col]
    valid_location_list = get_valid_locations(board)
    if depth == 0:
        return [(score_position(board, BOT_PIECE)), 0, 0]
    elif winning_move(board, BOT_PIECE): # bot won
        return [100000, 0, 0]
    elif winning_move(board, PLAYER_PIECE): # bot lost
        return [-10000, 0, 0]
    elif len(valid_location_list) == 0: # tie
        return [0, 0, 0]
    
    choice = random.choice(valid_location_list)
    if maximizingPlayer:
        maxVal = [-math.inf, choice[0], choice[1]]
        for choices in valid_location_list:
            row, col = choices[0], choices[1]
            temp_board = board.copy()
            temp_board[row][col] = BOT_PIECE
            newScore = minimax(temp_board, depth-1, alpha, beta, False)
            newScoreArray = [newScore[0], row, col]
            if newScore[0] > maxVal[0]:
                maxVal = newScoreArray
            alpha = max(alpha, newScore[0])
            if alpha >= beta:
                break
        return maxVal

    else:
        minVal = [math.inf, choice[0], choice[1]]
        for choices in valid_location_list:
            row, col = choices[0], choices[1]
            temp_board = board.copy()
            temp_board[row][col] = BOT_PIECE
            newScore = minimax(temp_board, depth-1, alpha, beta, True)
            newScoreArray = [newScore[0], row, col]
            if newScore[0] < minVal[0]:
                minVal = newScoreArray
            beta = min(beta, newScore[0])
            if alpha >= beta:
                break
        return minVal


###################################################################################
board = build_board()
print(board, '\n')
player1 = True

pygame.init()
screenSize = 600
size  = screenSize, screenSize
radius = 18
squaresize = math.floor(screenSize / (BOARD_SIZE))
padding = math.floor(squaresize / 2)
screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

while game:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if player1 and game:
                print('player1 turn')
                posX = event.pos[0]
                posY = event.pos[1]
                col = int(math.floor(posX / squaresize))
                row = int(math.floor(posY / squaresize))
                # print('col:', col, 'row: ', row)
                
                if board[row][col] == 0:
                    board[row][col] = PLAYER_PIECE
                    draw_board(board)
                    
                    if winning_move(board, PLAYER_PIECE):
                        print('player 1 won!')
                        game = False
                    player1 = False
           

    if player1 == False and game:
        start_timer = time.perf_counter()
        best_move = minimax(board, 2, -math.inf, math.inf, True)
        stop_timer = time.perf_counter()
        print("cycle time: ", round((stop_timer - start_timer), 3), 'seconds')
        print('best move: ', best_move)
        row, col = best_move[1], best_move[2]
        board[row][col] = BOT_PIECE
        draw_board(board)

        if winning_move(board, BOT_PIECE):
            print('player 2 won!')
            game = False
        player1 = True

        
    if not game:
        pygame.time.wait(5000)
