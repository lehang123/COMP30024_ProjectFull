from enum import Enum
from boby.utils import lists_to_tuples, tuples_to_lists, boom, print_board, make_nodes, board_dict_to_tuple
from random import choice


class Environment:
    def __init__(self):
        self.board = Board()

    def reset(self):
        """
        reset the board
        """
        self.board = Board()

    def make_move(self, board_dict):
        """
        :param board_dict the board configuration after move
        player makes move to the environment
        """
        (whites, blacks) = board_dict_to_tuple(board_dict)
        move = tuple(sorted(whites)), tuple(sorted(blacks))
        self.board.push(move)

    def get_legal_moves(self):
        return self.board.get_legal_moves()

    def make_random_move(self):
        moves = self.get_legal_moves()
        move = choice(moves)
        self.board.push(move)

    def get_reward(self, player):
        """
        according to the board to determine the result
        :return : the reward value
        """
        result = self.board.get_result()
        if result == Board.Result.DRAWS:
            return 0
        if player == 'white':
            if result == Board.Result.WHITE_WINS:
                return 1
            if result == Board.Result.BLACK_WINS:
                return -1
        else:
            if result == Board.Result.BLACK_WINS:
                return 1
            if result == Board.Result.WHITE_WINS:
                return -1
        return None


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

        legal_moves = self.get_legal_moves()
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
        self.print_board()

    def get_legal_moves(self):
        """
        get current board's legal moves
        :return: legal moves
        """
        board_dict = {'white': tuples_to_lists(self.state[0]), 'black': tuples_to_lists(self.state[1])}
        if self.turn == Board.Turn.WHITE:
            legal_move_dicts = make_nodes(board_dict, 'white', 'black')
        else :
            legal_move_dicts = make_nodes(board_dict, 'black', 'white')

        legal_moves_list = []
        for lmd in legal_move_dicts:
            [whites, blacks] = board_dict_to_tuple(lmd)
            tup = tuple(sorted(whites)), tuple(sorted(blacks))
            legal_moves_list.append(tup)

        return legal_moves_list

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

    def print_board(self):
        print_board({'white': self.state[0], 'black': self.state[1]})
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

# e = Environment()
# b = e.board
# for i in range(250):
#     e.make_move(make_nodes({'white': tuples_to_lists(b.state[0]),
#      'black': tuples_to_lists(b.state[1])}, 'white', 'black')[0])
#     e.make_random_move()
#     b.push(b.get_legal_moves()[0])
