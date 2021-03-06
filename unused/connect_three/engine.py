import chess
import os
import random
import time
from socket import *

BOLD = '\033[1m'
CEND = '\033[0m'
CRED = '\033[31m'
CGRAY = '\033[90m'


def send(sock, move):
    sendData = move
    sock.send(sendData.encode('utf-8'))


def receive(sock):
    recvData = sock.recv(1024)
    decodeMove = recvData.decode('utf-8')
    return decodeMove


def print_board(board):
    symbol = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
    j = 7
    k = 0
    print("8"+"   ", end='')
    for i in board.board_fen():
        if i == '/':
            print()
            print(j, "  ", end='')
            j = j-1
        elif (i in symbol) is True:
            if i.islower() is True:
                print(CRED+BOLD+i+CEND, "", end='')
            else:
                print(i, "", end='')
        else:
            for k in range(0, int(i)):
                print("- ", end='')
            k = 0
    print()
    print()
    print("    "+"a b c d e f g h")


# pick color randomly
if random.choice([1, 2]) is 1:
    p1_turn = True
    p2_turn = False
    white_port = 8080
    black_port = 8081
else:
    p2_turn = True
    p1_turn = False
    white_port = 8081
    black_port = 8080

# connect model1 - engine - model2
# p1's port = 8080 // p2's port = 8081

white_socket = socket(AF_INET, SOCK_STREAM)
white_socket.bind(('', white_port))
white_socket.listen(1)
print(" Connect to White Player...")
white_connect, white_addr = white_socket.accept()
print(" connect to white complete port number:", str(white_addr))

black_socket = socket(AF_INET, SOCK_STREAM)
black_socket.bind(('', black_port))
black_socket.listen(1)
print(" Connect to Black Player...")
black_connect, black_addr = black_socket.accept()
print(" connect to black complete port number:", str(black_addr))

turn = chess.WHITE
gameover = False
board = chess.Board()

print_board(board)

while True:
    if turn == chess.WHITE:
        if board.move_stack == []:
            send(white_connect, 'start')
        white_move = receive(white_connect)
        board.push(chess.Move.from_uci(white_move))
        if board.is_game_over() is True:
            send(black_connect, white_move)
            os.system('clear')
            print_board(board)
            break
        send(black_connect, white_move)
        # time.sleep(0.5)
        turn = chess.BLACK
    else:
        black_move = receive(black_connect)
        board.push(chess.Move.from_uci(black_move))
        if board.is_game_over() is True:
            send(white_connect, black_move)
            os.system('clear')
            print_board(board)
            break
        send(white_connect, black_move)
        # time.sleep(0.5)
        turn = chess.WHITE
    os.system('clear')
    print_board(board)

if board.is_game_over() is True:
    print(board.result())
    if board.result() == "1-0":
        print('\nWHITE win\n')
    elif board.result() == "0-1":
        print('\nBLACK win\n')
    elif board.result() == "1/2-1/2":
        print('\nDraw!\n')
