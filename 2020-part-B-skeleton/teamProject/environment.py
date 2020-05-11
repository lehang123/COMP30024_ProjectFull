from enum import Enum
from random import choice

import numpy as np

from teamProject.utils import tuples_to_lists, print_board, make_nodes, board_dict_to_tuple, boom


class Environment:
    def __init__(self):
        self.board = Board()

    def reset(self):
        """
        reset the board
        """
        self.board = Board()

    def get_board(self):
        state = self.board.state
        return {"white": tuples_to_lists(state[0]), "black": tuples_to_lists(state[1])}

    def get_turn(self):
        return self.board.get_turn()

    def get_white_turn_count(self):
        return self.board.white_turn_count

    def get_black_turn_count(self):
        return self.board.black_turn_count

    def make_move(self, board_dict):
        """
        :param board_dict the board configuration after move
        player makes move to the environment
        """
        (whites, blacks) = board_dict_to_tuple(board_dict)
        move = tuple(sorted(whites)), tuple(sorted(blacks))
        self.board.push(move)

    def get_white_num(self):
        """
        get number of whites left in the board
        :return: num of tokens
        """
        state = self.board.state
        white_num = sum([n for n, x, y in state[0]])
        return white_num

    def get_black_num(self):
        """
        get number of whites left in the board
        :return: num of tokens
        """
        state = self.board.state
        black_num = sum([n for n, x, y in state[1]])
        return black_num

    def get_legal_moves(self, include_boom=True):
        return self.board.get_legal_moves(include_boom = include_boom)

    def make_random_move(self, include_boom=False):
        moves = self.get_legal_moves(include_boom=include_boom)

        move_tups = []
        for move in moves:
            [whites, blacks] = board_dict_to_tuple(move)
            tup = tuple(sorted(whites)), tuple(sorted(blacks))
            move_tups.append(tup)

        move = choice(move_tups)

        self.board.push(move)
        # print("I KNOW THIS LOOKS STUPID BUT THIS IS A RANDOM MOVE !!!")
        return {'white': move[0], 'black': move[1]}

    def get_reward(self):
        """
        according to the board to determine the result
        :return : the reward value
        """
        result = self.board.get_result()
        if result == Board.Result.DRAWS:
            return 0
        elif result == Board.Result.WHITE_WINS:
            return 1
        elif result == Board.Result.BLACK_WINS:
            return -1
        else:
            return None

    def play(self, players, random_move=False):
        """
        simulating the play ground,

        :param players: the two players, player[0] is white, player[1] is black
        :return: the reward (in here we always refer to white)
        """
        reward = self.get_reward()
        self.reset()
        while reward is None:

            player = players[self.board.turn.value]

            move = player.get_move()
            if random_move and np.random.rand() < 0.1 :
                self.make_random_move()
            else:
                self.make_move(move)

            reward = self.get_reward()

        return reward

    def get_move_from_command(self, move):
        """
        the user input command convert it to a push of the board
        :param move: the move made on board, format : ('MOVE', (n, (xa, ya), (xb, yb))),
                                                    or ('BOOM', (x, y))
        """
        assert self.board.game_result == Board.Result.ON_GOING

        (action, param) = move

        # check if move is legal
        legal_move = False

        new_stacks = []
        color = int(self.board.turn.value)

        if color == 0:
            block_color = 1
        else:
            block_color = 0

        color_dict = {0: 'white', 1: "black"}

        blocks = self.board.state[block_color]

        stacks = self.board.state[color]

        if action == 'MOVE':
            (n, (b_x, b_y), (a_x, a_y)) = param
            # assert move inbound
            assert 0 <= b_x <= 7 and 0 <= b_y <= 7 and 0 <= a_x <= 7 and 0 <= a_y <= 7 and ((b_x, b_y)!=(a_x, a_y))

            for stack in stacks:
                if stack[1::] == (b_x, b_y):
                    # start moving
                    legal_move = True
                    step_on_opponent = (a_x, a_y) in [b[1::] for b in blocks]

                    in_move_range = ((b_x == a_x) and (abs(a_y-b_y)<=stack[0])) \
                                    or ((a_y == b_y) and (abs(a_x-b_x)<=stack[0]))

                    assert (not step_on_opponent) and in_move_range and n<=stack[0]

                    if stack[0]-n != 0: # if not moving all pieces from before
                        new_stack = (stack[0]-n, b_x, b_y)
                        new_stacks.append(new_stack)
                    if (a_x, a_y) not in [s[1::] for s in stacks]: # if after position is new
                        new_stacks.append((n, a_x, a_y))

                elif stack[1::] != (a_x, a_y): # if stack is neither in before or after, keep it the same
                    new_stacks.append(stack)
                else: # if the stack is in after, update the stack
                    new_stack = (stack[0]+n, a_x, a_y)
                    new_stacks.append(new_stack)
            assert legal_move

            # self.state[color] = tuple(new_stacks)
            return {color_dict[color]: tuples_to_lists(new_stacks), color_dict[block_color]: tuples_to_lists(blocks)}

        elif action == 'BOOM':
            (boom_x, boom_y) = param
            assert 0 <= boom_x <= 7 and 0 <= boom_x <= 7 and ((boom_x, boom_y) in [s[1::] for s in stacks])
            boom_dict = {color_dict[color]: tuples_to_lists(stacks), color_dict[block_color]:tuples_to_lists(blocks)}

            # boom action, the 1 is just an placeholder, doesn't matter
            boom((1, boom_x, boom_y), boom_dict)

            return boom_dict

    def show_board(self):
        self.board.show_board()


class Board:

    class Result(Enum):
        WHITE_WINS = 1
        BLACK_WINS = 2
        DRAWS = 3
        ON_GOING = 4

    class Turn(Enum):
        WHITE = 0
        BlACK = 1

    def __init__(self):
        white_init = tuple([(1, x, y) for x in range(0, 8) for y in range(0, 2) if (x != 2 and x != 5)])
        black_init = tuple([(1, x, y) for x in range(0, 8) for y in range(6, 8) if (x != 2 and x != 5)])
        self.state = [white_init, black_init]
        # each player have their 250th move count as draw
        self.white_turn_count = 0
        self.black_turn_count = 0

        # white is the one first to move
        self.turn = Board.Turn.WHITE

        self.game_result = Board.Result.ON_GOING

        # check the configuration of the board if one configuration occurs 4 times, game draw
        self.config_record = {}

    def push(self, move):
        """
        push a move to the board
        :param move: the move made on board, format : ('move or boom', ('how many','from', 'to') or 'boom at')
        """
        assert self.game_result == Board.Result.ON_GOING

        legal_moves = self.get_legal_moves(turn_to_tuple=True)
        (whites, blacks) = move
        sorted_move = tuple(sorted(whites)), tuple(sorted(blacks))
        assert sorted_move in legal_moves

        self.state = sorted_move

        color = int(self.turn.value)

        if color == 0:
            self.white_turn_count += 1
            self.turn = Board.Turn.BlACK
        else:
            self.black_turn_count += 1
            self.turn = Board.Turn.WHITE

        self.update_game()
        # self.show_board()

    def get_legal_moves(self, include_boom=True, turn_to_tuple=False):
        """
        get current board's legal moves
        :return: legal moves
        """
        board_dict = {'white': tuples_to_lists(self.state[0]), 'black': tuples_to_lists(self.state[1])}
        legal_move_dicts = make_nodes(board_dict, self.get_turn(), include_boom)

        if turn_to_tuple:
            legal_moves_list = []
            for lmd in legal_move_dicts:
                [whites, blacks] = board_dict_to_tuple(lmd)
                tup = tuple(sorted(whites)), tuple(sorted(blacks))
                legal_moves_list.append(tup)
            return legal_moves_list
        else:
            return legal_move_dicts

    def get_turn(self):
        return 'white' if self.turn == Board.Turn.WHITE else 'black'

    def update_game(self):
        """
        update the game result
        """

        white_lives = self.state[0]
        black_lives = self.state[1]

        if white_lives and black_lives:
            reach_max_turn = self.white_turn_count >= 250 and self.black_turn_count >= 250
            self.config_record[tuple(self.state)] = self.config_record.get(tuple(self.state), 0) + 1
            # draw when hit 4 same configurations or reach to max turn
            if reach_max_turn or (self.config_record[tuple(self.state)] == 4):
                self.game_result = Board.Result.DRAWS

        elif black_lives and not white_lives:
            self.game_result = Board.Result.BLACK_WINS
        elif white_lives and not black_lives:
            self.game_result = Board.Result.WHITE_WINS
        else:
            self.game_result = Board.Result.DRAWS

    def show_board(self):
        board_dict = {'white': tuples_to_lists(self.state[0]), 'black': tuples_to_lists(self.state[1])}
        print_board(board_dict)
        print(board_dict)
        print("turn to: " + str(self.turn))
        print("game_result : " + str(self.game_result))
        print("white moved : " + str(self.white_turn_count))
        print("black moved : " + str(self.black_turn_count))

    def get_result(self):
        """
        check result of the board
        :return: the result of the board (who wins or draws)
        """
        return self.game_result
