from enum import Enum
from boby.utils import lists_to_tuples, tuples_to_lists, boom, print_board

class Enviornment:
    def __init__(self):
        self.board = Board()


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

        (action, param) = move

        # check if move is legal
        legal_move = False

        new_stacks = []
        color = int(self.turn.value)

        if color == 0:
            block_color = 1
            self.white_turn_count +=1
            self.turn = Board.Turn.BlACK
        else:
            block_color = 0
            self.black_turn_count +=1
            self.turn = Board.Turn.WHITE

        blocks = self.state[block_color]

        stacks = self.state[color]

        if action == 'move':
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

            self.state[color] = tuple(new_stacks)

        elif action == 'boom':
            (boom_x, boom_y) = param
            assert 0 <= boom_x <= 7 and 0 <= boom_x <= 7 and ((boom_x, boom_y) in [s[1::] for s in stacks])
            color_dict = {0:'white', 1:"black"}
            boom_dict = {color_dict[color]: tuples_to_lists(stacks), color_dict[block_color]:tuples_to_lists(blocks)}

            # boom action, the 1 just an placeholder, doesn't matter
            boom((1, boom_x, boom_y), boom_dict)

            self.state = [lists_to_tuples(boom_dict['white']), lists_to_tuples(boom_dict['black'])]

        self.update_game()
        self.print_board()
        print("turn to: " + str(self.turn))
        print("game_result : " + str(self.game_result))
        print("white moved : " + str(self.white_turn_count))
        print("black moved : " + str(self.black_turn_count))
        print("config : " + str(self.config_record))

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


    def result(self):
        """
        check result of the board
        :return: the result of the board (who wins or draws)
        """
        return self.game_result

# b = Board()
# b.push(('move', (1, (0, 0), (1, 0))))
# b.push(('move', (1, (0, 7), (0, 6))))
# b.push(('move', (1, (1, 0), (0, 0))))
# b.push(('move', (1, (0, 6), (0, 7))))
#
# b.push(('move', (1, (0, 0), (1, 0))))
# b.push(('move', (1, (0, 7), (0, 6))))
# b.push(('move', (1, (1, 0), (0, 0))))
# b.push(('move', (1, (0, 6), (0, 7))))
#
# b.push(('move', (1, (0, 0), (1, 0))))
# b.push(('move', (1, (0, 7), (0, 6))))
# b.push(('move', (1, (1, 0), (0, 0))))
# b.push(('move', (1, (0, 6), (0, 7))))
#
# b.push(('move', (1, (0, 0), (1, 0))))
