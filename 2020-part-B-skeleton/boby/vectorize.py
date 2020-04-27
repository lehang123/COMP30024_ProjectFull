import numpy as np
from utils import boom_zone, clusters_count, speedy_manhattan
from statistics import stdev, mean

def pieces_positions_vectorize(board, turn):
    """
    a simple vectorize method that keeping track on each piece and their position

    len of vector: 128 = 64(white's piece on each position of the board (range: 0~12, num of pieces))
                    + 64(black's piece on each position of the board (range: 0~12, num of pieces))

    the 64 len's position vector: from index 0 to 63, correspond to (0,0), (0,1), (0,2)... (7,7) on board

    :param board: the current board that we are going to vectorize
    :param turn: the color that's going to move in this board configuration
    :return: the vector
    """

    # todo : do we give some stacking bouns ?

    white_pieces = board['white']
    black_pieces = board['black']

    white_vector = np.zeros(64, dtype=float)
    black_vector = np.zeros(64, dtype=float)

    for (w_num, w_x, w_y) in white_pieces:
        white_vector[w_x * 8 + w_y] = w_num + (w_num-1)/10.0

    for (b_num, b_x, b_y) in black_pieces:
        black_vector[b_x * 8 + b_y] = -b_num - (b_num-1)/10.0

    # checking for valid board
    for i in range(64):
        if white_vector[i] != 0:
            assert black_vector[i] == 0
        elif black_vector[i] != 0:
            assert white_vector[i] == 0

    vector = np.concatenate([white_vector, black_vector])

    vector = vector.reshape(1, vector.shape[0])

    return vector


def score_vectorize(board, turn):
    """

    len of vector: ? = 1 (white pieces and position score) - 1 (black pieces and position score)
                        + 1 (white pieces safety score) - 1 (black pieces safety score)

    :param board: the current board that we are going to vectorize
    :param turn: the color that's going to move in this board configuration
    :return: the vector
    """

    white_pieces = board['white']
    black_pieces = board['black']

    vector = np.zeros(2, dtype=float)

    for white_stack in white_pieces:
        vector[0] -= stack_score(white_stack, black_pieces)

    for black_stack in black_pieces:
        vector[1] += stack_score(black_stack, white_pieces)

    def exchange_nums(position, blacks_exploded, whites_exploded, start=True):
        result = 0

        boom_zones = boom_zone(position)

        b_xes = [black_piece for black_piece in black_pieces
                 if (black_piece[1::] in boom_zones) and (black_piece not in blacks_exploded)]
        s_xes = [white_piece for white_piece in white_pieces
                 if (white_piece[1::] in boom_zones) and (white_piece not in whites_exploded)]

        blacks_exploded.extend(b_xes)
        whites_exploded.extend(s_xes)

        bo = (turn == 'white' and s_xes) or (turn == 'black' and b_xes)

        if bo or not start:
            result += sum([n for n, x, y in b_xes])
            result -= sum([n for n, x, y in s_xes])
            result += sum([exchange_nums(b[1::], blacks_exploded, whites_exploded, False)
                           for b in b_xes if b[1::] != position])

            result += sum([exchange_nums(w[1::], blacks_exploded, whites_exploded, False)
                           for w in s_xes if w[1::] != position])

        return result

    if turn == 'white':
        # after white move, black try to boom
        seq = [exchange_nums(black_piece[1::], [], []) for black_piece in black_pieces]
        worst_trade_score = min(seq) if seq else -13
    else:
        # after black move, white try to boom
        seq = [exchange_nums(white_piece[1::], [], []) for white_piece in white_pieces]
        worst_trade_score = max(seq) if seq else 13

    worst_trade_score *= 0.7

    # white_safety = (safety_score(white_pieces[0], white_pieces[1::]) * 0.1) if white_pieces else -5.0
    # black_safety = (safety_score(black_pieces[0], black_pieces[1::]) * 0.1) if black_pieces else 5.0
    # vector[2] -= 1.0/white_safety
    # vector[3] += 1.0/black_safety
    # vector[2] += worst_trade_score

    vector = vector.reshape(1, vector.shape[0])

    return vector

position_scores = {(0, 7): 1.0, (7, 7): 1.0, (0, 0): 1.0, (7, 0): 1.0,

                  (0, 6): 2.0, (1, 7): 2.0, (7, 6): 2.0, (6, 7): 2.0,
                  (1, 0): 2.0, (0, 1): 2.0, (6, 0): 2.0, (7, 1): 2.0,

                  (5, 7): 3.0, (2, 7): 3.0, (7, 2): 3.0, (0, 2): 3.0,
                  (6, 6): 3.0, (1, 6): 3.0, (6, 1): 3.0, (1, 1): 3.0,
                  (7, 5): 3.0, (0, 5): 3.0, (5, 0): 3.0, (2, 0): 3.0,

                  (4, 7): 4.0, (3, 7): 4.0, (0, 3): 4.0, (7, 3): 4.0,
                  (7, 4): 4.0, (0, 4): 4.0, (3, 0): 4.0, (4, 0): 4.0,

                  (4, 6): 5.0, (2, 6): 5.0, (1, 3): 5.0, (4, 1): 5.0,
                  (5, 6): 5.0, (3, 6): 5.0, (1, 2): 5.0, (5, 1): 5.0,
                  (6, 5): 5.0, (1, 5): 5.0, (2, 1): 5.0, (6, 2): 5.0,
                  (6, 4): 5.0, (1, 4): 5.0, (3, 1): 5.0, (6, 3): 5.0,

                  (4, 5): 6.0, (2, 5): 6.0, (2, 3): 6.0, (4, 2): 6.0,
                  (5, 5): 6.0, (3, 5): 6.0, (2, 2): 6.0, (5, 2): 6.0,
                  (5, 4): 6.0, (2, 4): 6.0, (3, 2): 6.0, (5, 3): 6.0,

                  (3, 4): 7.0, (4, 4): 7.0, (3, 3): 7.0, (4, 3): 7.0}


def ultimate_vectorize(board, turn):
    """
    a simple vectorize method that keeping track on mobility, exchange ability, and pieces left

    len of vector: 15 = 1 (white's pieces) - 1 (black's pieces)

                        + 1 (average white's position score) + 1 (standard div of white's position score)
                        + 1 (average white's stacking score) + 1 (standard div of white's stacking score)

                        - 1 (average black's position score) - 1 (standard div of black's position score)
                        - 1 (average black's stacking score) - 1 (standard div of black's stacking score)

                        + enemies best's trade score


    :param board: the current board that we are going to vectorize
    :param turn: the color that's going to move in this board configuration
    :return: the vector
    """

    # score for each position on the board, hand made

    white_stacks = board['white']
    black_stacks = board['black']

    white_pieces = 0
    white_p_scores = []
    white_s_scores = []

    black_pieces = 0
    black_p_scores = []
    black_s_scores = []

    white_positions = []
    black_positions = []

    vector = np.zeros(11, dtype=float)

    for n, x, y in white_stacks:
        white_pieces += n
        white_positions.append([x, y])
        white_p_scores.append(position_scores[(x, y)])
        white_s_scores.append(n)

    for n, x, y in black_stacks:
        black_pieces += n
        black_positions.append([x, y])
        black_p_scores.append(position_scores[(x, y)])
        black_s_scores.append(n)

    white_p_mean = mean(white_p_scores) if len(white_p_scores)>1 else white_p_scores[0] if white_p_scores else 0.0
    white_p_stdev = stdev(white_p_scores) if len(white_p_scores)>1 else 0.0

    white_s_mean = 6*mean(white_s_scores) if len(white_s_scores)>1 else white_s_scores[0] if white_s_scores else 0.0
    white_s_stdev = stdev(white_s_scores) if len(white_s_scores)>1 else 0.0

    black_p_mean = mean(black_p_scores) if len(black_p_scores)>1 else black_p_scores[0] if black_p_scores else 0.0
    black_p_stdev = stdev(black_p_scores) if len(black_p_scores)>1 else 0.0

    black_s_mean = 6*mean(black_s_scores) if len(black_s_scores)>1 else black_s_scores[0] if black_s_scores else 0.0
    black_s_stdev = stdev(black_s_scores) if len(black_s_scores)>1 else 0.0

    def exchange_nums(position, blacks_exploded, whites_exploded, start=True):
        result = 0

        boom_zones = boom_zone(position)

        b_xes = [black_piece for black_piece in black_stacks
                 if (black_piece[1::] in boom_zones) and (black_piece not in blacks_exploded)]
        s_xes = [white_piece for white_piece in white_stacks
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
        # turn to white
        seq = [exchange_nums(white_piece[1::], [], []) for white_piece in white_stacks]
        best_trade_score = max(seq) if seq else 0.0
    else:
        # turn to black
        seq = [exchange_nums(black_piece[1::], [], []) for black_piece in black_stacks]
        best_trade_score = min(seq) if seq else 0.0

    vector[0] = white_pieces
    vector[1] = -black_pieces
    vector[2] = white_p_mean
    vector[3] = -white_p_stdev
    vector[4] = white_s_mean
    vector[5] = -white_s_stdev
    vector[6] = -black_p_mean
    vector[7] = black_p_stdev
    vector[8] = -black_s_mean
    vector[9] = black_s_stdev
    vector[10] = best_trade_score


    vector = vector.reshape(1, vector.shape[0])

    vector = np.divide(vector, 20.0) # divide this by 100 so the tanh() can capture better difference

    return vector


def characteristic_vectorize(board, turn):
    """
    a simple vectorize method that keeping track on mobility, exchange ability, and pieces left

    len of vector: 7 = 1 (white's pieces) - 1 (black's pieces) + 1 (white's mobility) - 1 (black's mobility)

                    + 1 (best exchange score) + 1 (vulnerability score for white) - 1 (vulnerability score for black)


    :param board: the current board that we are going to vectorize
    :param turn: the color that's going to move in this board configuration
    :return: the vector
    """

    white_pieces = board['white']
    black_pieces = board['black']

    characteristic_vector = np.zeros(5, dtype=float)

    w_nums = 0
    b_nums = 0

    white_mobility = 0
    black_mobility = 0

    for (w_num, w_x, w_y) in white_pieces:
        w_nums += w_num
        white_mobility += stack_score([w_num, w_x, w_y], black_pieces)

    for (b_num, b_x, b_y) in black_pieces:
        b_nums += b_num
        black_mobility += stack_score([b_num, b_x, b_y], white_pieces)

    def exchange_nums(position, blacks_exploded, whites_exploded, start=True):
        result = 0

        boom_zones = boom_zone(position)

        b_xes = [black_piece for black_piece in black_pieces
                 if (black_piece[1::] in boom_zones) and (black_piece not in blacks_exploded)]
        s_xes = [white_piece for white_piece in white_pieces
                 if (white_piece[1::] in boom_zones) and (white_piece not in whites_exploded)]

        blacks_exploded.extend(b_xes)
        whites_exploded.extend(s_xes)

        bo = (turn == 'white' and s_xes) or (turn == 'black' and b_xes)

        if bo or not start:
            result += sum([n for n, x, y in b_xes])
            result -= sum([n for n, x, y in s_xes])
            result += sum([exchange_nums(b[1::], blacks_exploded, whites_exploded, False)
                           for b in b_xes if b[1::] != position])

            result += sum([exchange_nums(w[1::], blacks_exploded, whites_exploded, False)
                           for w in s_xes if w[1::] != position])

        return result

    # w_vhs = vulnerability_heuristics_score(board, 'white')
    # b_vhs = vulnerability_heuristics_score(board, 'black')
    white_safety = (safety_score(white_pieces[0], white_pieces[1::]) * 0.1) if white_pieces else 0.0
    black_safety = (safety_score(black_pieces[0], black_pieces[1::]) * 0.1) if black_pieces else 0.0

    if turn == 'white':
        # turn to white
        seq = [exchange_nums(white_piece[1::], [], []) for white_piece in white_pieces]
        worst_trade_score = max(seq) if seq else 0.0
    else:
        # turn to black
        seq = [exchange_nums(black_piece[1::], [], []) for black_piece in black_pieces]
        worst_trade_score = min(seq) if seq else 0.0

    worst_trade_score *= 0.7

    characteristic_vector[0] = w_nums
    characteristic_vector[1] = -b_nums
    characteristic_vector[2] = white_mobility
    characteristic_vector[3] = -black_mobility
    characteristic_vector[4] = worst_trade_score

    characteristic_vector = characteristic_vector.reshape(1, characteristic_vector.shape[0])

    characteristic_vector = np.divide(characteristic_vector, 10) # divide this by 100 so the tanh() would work

    # print("c vector : " + str(characteristic_vector))
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

    if num > 8:
        num = 8
    stack_bonus = num/8.0 + 1.0
    return score * stack_bonus


def safety_score(piece, pieces, explode=False):
    # getting some idea about safety, if it's scatter and connected, consider not safe
    bz = boom_zone(piece[1::], exclude_self=True)
    safe_score = 0.0

    exploded = []
    before = len(pieces)
    for p in pieces:
        if p[1::] in bz:
            pieces.remove(p)
            exploded.append(p)

    if exploded:
        if not explode:
            deduct_point = (1.0/piece[0])
        else:
            deduct_point = 0
        deduct_point += sum([1.0/exp[0] for exp in exploded])
        safe_score -= deduct_point

    for e in exploded:
        safe_score += safety_score(e, pieces, True)

    after = len(pieces)

    chain_num = before-after
    safe_score -= ((chain_num**2) * 0.2)

    if pieces and not explode:
        # print("what's left : " + str(pieces))
        safe_score += safety_score(pieces[0], pieces[1::])

    return safe_score


def stack_score(stack, blocks):
    """

    :param stack: the stack we evaluating
    :param blocks: blocks that can't step on
    :return:
    """
    n, x, y = stack

    score = 0

    l = []
    for i in range(1, n+1):
        l += [(x + i, y), (x - i, y), (x, y + i), (x, y - i)]

    blocks = [(b_x, b_y) for (b_n, b_x, b_y) in blocks]

    def in_board(p):
        x, y = p
        return (0 <= x <= 7) and (0 <= y <= 7) and (p not in blocks)

    def p_score(position):
        x, y = position
        if x == 0 or y == 0 or x == 7 or y == 7:
            return 0.1
        elif x == 1 or y == 1 or x == 6 or y == 6:
            return 0.12
        elif x == 2 or y == 2 or x == 5 or y == 5:
            return 0.14
        else:
            return 0.16

    score += p_score((x, y))

    for p in l:
        if in_board(p):
            score += 0.1

    if n > 8:
        n = 8
    stack_bonus = (n-1)*0.6

    return score + stack_bonus



