import numpy as np
from utils import boom_zone

def pieces_positions_vectorize(board, turn):
    """
    a simple vectorize method that keeping track on each piece and their position

    len of vector: 129 = 64(white's piece on each position of the board (range: 0~12, num of pieces))
                    + 64(black's piece on each position of the board (range: 0~12, num of pieces))
                    + 1(who's turn to move(range:0~1, 1 is player, 0 is opponent))

    the 64 len's position vector: from index 0 to 63, correspond to (0,0), (0,1), (0,2)... (7,7) on board

    :param board: the current board that we are going to vectorize
    :param turn: the color that's going to move in this board configuration
    :return: the vector
    """

    white_pieces = board['white']
    black_pieces = board['black']

    white_vector = np.zeros(64, dtype=int)
    black_vector = np.zeros(64, dtype=int)

    for (w_num, w_x, w_y) in white_pieces:
        white_vector[w_x * 8 + w_y] = w_num

    for (b_num, b_x, b_y) in black_pieces:
        black_vector[b_x * 8 + b_y] = b_num

    # checking for valid board
    for i in range(64):
        if white_vector[i] != 0:
            assert black_vector[i] == 0
        elif black_vector[i] != 0:
            assert white_vector[i] == 0

    vector = np.concatenate([white_vector, black_vector])

    if turn == 'white':
        vector = np.append(vector, [1])
    else:
        vector = np.append(vector, [0])

    vector = vector.reshape(1, vector.shape[0])

    return vector


def characteristic_vectorize(board, turn):
    """
    a simple vectorize method that keeping track on mobility, exchange ability, and pieces left

    len of vector: 5 = 1 (white pieces left) - 1 (black pieces left) + 1 (white's mobility) - 1 (black's mobility)

                    + 1 (best exchange score)

                    to add:  distance

    the 64 len's position vector: from index 0 to 63, correspond to (0,0), (0,1), (0,2)... (7,7) on board

    :param board: the current board that we are going to vectorize
    :param turn: the color that's going to move in this board configuration
    :return: the vector
    """

    white_pieces = board['white']
    black_pieces = board['black']

    characteristic_vector = np.zeros(5, dtype=int)

    w_nums = 0
    b_nums = 0

    white_mobility = 0
    black_mobility = 0

    for (w_num, w_x, w_y) in white_pieces:
        w_nums += w_num
        white_mobility += mobility(w_num, [w_x, w_y], black_pieces)

    for (b_num, b_x, b_y) in black_pieces:
        b_nums += b_num
        black_mobility += mobility(b_num, [b_x, b_y], white_pieces)

    def exchange_nums(position, blacks_exploded, whites_exploded, start=True):
        result = 0

        boom_zones = boom_zone(position)

        b_xes = [black_piece for black_piece in black_pieces
                 if (black_piece[1::] in boom_zones) and (black_piece not in blacks_exploded)]
        s_xes = [white_piece for white_piece in white_pieces
                 if (white_piece[1::] in boom_zones) and (white_piece not in whites_exploded)]

        blacks_exploded.extend(b_xes)
        whites_exploded.extend(s_xes)

        bo = (turn == 'white' and b_xes) or (turn == 'black' and s_xes)

        if bo or not start:
            result += sum([n for n, x, y in b_xes])
            result -= sum([n for n, x, y in s_xes])
            result += sum([exchange_nums(b[1::], blacks_exploded, whites_exploded, False)
                           for b in b_xes if b[1::] != position])

            result += sum([exchange_nums(w[1::], blacks_exploded, whites_exploded, False)
                           for w in s_xes if w[1::] != position])

        return result

    if turn == 'white':
        seq = [exchange_nums(white_piece[1::], [], []) for white_piece in white_pieces]
        best_exchange_score = max(seq) if seq else -13
        # print("pieces_positions_vectorize : exchange score for white : " + str(best_exchange_score))
    else:
        seq = [exchange_nums(black_piece[1::], [], []) for black_piece in black_pieces]
        best_exchange_score = min(seq) if seq else 13
        # print("pieces_positions_vectorize : exchange score for black : " + str(best_exchange_score))

    characteristic_vector[0] = w_nums
    characteristic_vector[1] = -b_nums
    characteristic_vector[2] = white_mobility
    characteristic_vector[3] = -black_mobility
    characteristic_vector[4] = best_exchange_score

    characteristic_vector = characteristic_vector.reshape(1, characteristic_vector.shape[0])

    characteristic_vector = np.divide(characteristic_vector, 100) # divide this by 100 so the tanh() would work


    return characteristic_vector


def mobility(num, position, blocks):
    """
    get score of mobility for a stack, in here, we calculate coverage

    :param num: number of pieces in the position
    :param position: the position
    :param blocks: blocks that can't step on
    :return:
    """
    (x, y) = position
    l = []
    for i in range(1, num+1):
        l += [[x+i, y], [x-i, y], [x, y+i], [x, y-i]]

    blocks = [b[1::] for b in blocks]

    def in_board(p):
        x, y = p
        return (0 <= x <= 7) and (0 <= y <= 7) and (p not in blocks)
    score = 0

    for p in l:
        if in_board(p):
            score += 1

    return (score * num)


