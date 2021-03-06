import chess
import random
import pickle
import sys
import copy
import datetime

REPEAT = 500

class LinkedList:
    class Node:
        def __init__(self, move, state):
            self.move = move
            self.reward = 0.5
            self.next = []
            self.state = state
    def __init__(self):
        self.head = self.Node(None, None)
        self.search_list = []
        for _ in range(33):
            self.search_list.append([])
        self.size = 0
        self.accumulated_play = 0
    def insert(self, move, p, state):
        new_node = self.Node(move, state)
        p.next.append(new_node)
        counting_result = counting(state)
        self.search_list[counting_result].append(new_node)
        self.size += 1
    def search(self, new_state, current_node):
        counting_result = counting(new_state)
        for i in self.search_list[counting_result]:
            if(str(i.state) == str(new_state) and i.state.turn == new_state.turn):
                print("aaaa")
                current_node.next.append(i)
                return True
        return False

def counting(board):
    count = 0
    for i in range(len(str(board))):
        if str(board)[i] != '.' and str(board)[i] != '\n' and str(board)[i] != ' ':
            count += 1
    return count

log = open("log.txt", 'a')
log.write("\n\nStart: " + str(datetime.datetime.now()) + "\n")
log.close()

try:
    data = open('data.pickle', 'rb')
except FileNotFoundError:
    print("Make new List (Error: FileNotFoundError)")
    chess_model = LinkedList()
else:
    with open('data.pickle', 'rb') as f:
        data = pickle.load(f)
    chess_model = data

sys.setrecursionlimit(10**7)

# main
for i in range(REPEAT):
    board = chess.Board()
    chess_model.head.state = copy.deepcopy(board)
    current_node = chess_model.head
    record_list = []
    record_list.append(current_node)
    print(str(chess_model.accumulated_play))

    if 0.99999**chess_model.accumulated_play >= 0.2:
        epsilon = 0.99999**chess_model.accumulated_play # epsilon의 확률로 랜덤, 0.99999^x 곡선으로 epsilon 변화
    else:
        epsilon = 0.2

    while True:
        legal_list = []
        for i in board.legal_moves:
            legal_list.append(str(i))

        # epsilon의 확률로 랜덤
        random_value = random.random()
        
        if not current_node.next: # next가 비어있는 경우 랜덤
            random_move = random.choice(legal_list)
            selected_move = chess.Move.from_uci(random_move)
            board.push(selected_move)
                
            state = copy.deepcopy(board)
            search_result = chess_model.search(state, current_node)

            if search_result is True:
                current_node = current_node.next[-1]
            else:
                chess_model.insert(random_move, current_node, state)
                current_node = current_node.next[-1]

        elif epsilon <= random_value: # 최선의 수 선택
            current_node = current_node.next[0]
            selected_move = chess.Move.from_uci(current_node.move)
            board.push(selected_move)

        else: # 탐험
            random_move = random.choice(legal_list)
            find = False

            for i in current_node.next:
                if random_move == i.move:
                    find = True
                    current_node = i
                    break
            
            if find is True:
                selected_move = chess.Move.from_uci(current_node.move)
                board.push(selected_move)
            else:
                selected_move = chess.Move.from_uci(random_move)
                board.push(selected_move)
                
                state = copy.deepcopy(board)
                search_result = chess_model.search(state, current_node)

                if search_result is True:
                    current_node = current_node.next[-1]
                else:
                    chess_model.insert(random_move, current_node, state)
                    current_node = current_node.next[-1]

        record_list.append(current_node)
        if board.is_game_over() is True:
            break

    winner = record_list[-1].state.turn
    stack_size = len(record_list)
    while record_list:
        my_index = len(record_list)
        pop_node = record_list.pop()

        if board.result() == "1/2-1/2":
            before_reward = copy.deepcopy(pop_node.reward)
            pop_node.reward = pop_node.reward*2/3 + (-0.5)*(my_index/stack_size)/3

        elif pop_node.state.turn is winner:
            before_reward = copy.deepcopy(pop_node.reward)
            pop_node.reward = pop_node.reward*2/3 + 1*(my_index/stack_size)/3
        else:
            before_reward = copy.deepcopy(pop_node.reward)
            pop_node.reward = pop_node.reward*2/3 + (-1)*(my_index/stack_size)/3

        if record_list:
            if record_list[-1].next[0] == pop_node and before_reward-pop_node.reward > 0:
                # max_reward = copy.deepcopy(pop_node.reward)
                tmp = []
                temp = None
                for i in record_list[-1].next:
                    tmp.append(i.reward)
                found_index = tmp.index(max(tmp))
                # record_list[-1].next[found_index], pop_node = pop_node, record_list[-1].next[found_index]
                temp = record_list[-1].next[found_index]
                record_list[-1].next[found_index] = pop_node
                pop_node = temp
            elif pop_node.reward > record_list[-1].next[0].reward:
                # pop_node, record_list[-1].next[0] = record_list[-1].next[0], pop_node
                temp = record_list[-1].next[found_index]
                record_list[-1].next[found_index] = pop_node
                pop_node = temp

    chess_model.accumulated_play += 1
    # if chess_model.accumulated_play%10 == 0:
    log = open("log.txt", 'a')
    log.write(str(chess_model.accumulated_play) + ": " + str(datetime.datetime.now()) + "\n")
    log.close()

with open('data.pickle', 'wb') as f:
    pickle.dump(chess_model, f, pickle.HIGHEST_PROTOCOL)

log = open("log.txt", 'a')
log.write("End: " + str(datetime.datetime.now()) + "\n\n")
log.close()

print("OK")
