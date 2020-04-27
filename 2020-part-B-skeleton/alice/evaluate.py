from statistics import stdev, mean
from utils import get_clusters, speedy_manhattan, print_board,\
    cluster_boom_zone, merge_lists, boom_zone, boom_affected, lists_to_tuples, boom_affected_count
from math import tanh

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


def prime_eval(board, next_turn):
    """
    a simple eval method that return the value for a current board

    this is the first version

    :param previous_board: the board before move
    :param board: the board after move
    :param next_turn: the color that's going to move in this board configuration(the move after board)
    :return: the value of the board
    """
    # current_turn = 'white' if next_turn == 'black' else 'black'

    white_stacks = board['white']
    black_stacks = board['black']

    if not white_stacks and black_stacks:
        return -1
    if not black_stacks and white_stacks:
        return 1
    if not black_stacks and not black_stacks:
        return 0

    white_pieces_num = sum([n for n, x, y in white_stacks])
    black_pieces_num = sum([n for n, x, y in black_stacks])

    is_white_turn = (next_turn == "white")

    # white_cluster_safety = cluster_safety(white_stacks, black_stacks, is_white_turn)
    # black_cluster_safety = cluster_safety(black_stacks, white_stacks, not is_white_turn)

    if len(white_stacks) == 1:
        white_stacking_mean = white_stacks[0][0]
        white_stacking_stdev = 0
    else:
        white_stacking_mean = mean([n if n < 8 else 8 for n, x, y in white_stacks])
        white_stacking_stdev = stdev([n if n < 8 else 8 for n, x, y in white_stacks])

    if len(black_stacks) == 1:
        black_stacking_mean = black_stacks[0][0]
        black_stacking_stdev = 0
    else:
        black_stacking_mean = mean([n if n<8 else 8 for n, x, y in black_stacks])
        black_stacking_stdev = stdev([n if n<8 else 8 for n, x, y in black_stacks])

    white_stacking_score = (5*white_stacking_mean) - white_stacking_stdev
    black_stacking_score = (5*black_stacking_mean) - black_stacking_stdev

    board_score = 5.0*((white_pieces_num/12.0) - (black_pieces_num/12.0)) \
                  + (white_stacking_score/40.0) - (black_stacking_score/40.0)
                  # + ((white_cluster_safety/12.0) - (black_cluster_safety/12.0))

    # print('pieces left : ' + str(2.0*((white_pieces_num/12.0) - (black_pieces_num/12.0))))
    # print('stacking score : ' + str((white_stacking_score/40.0) - (black_stacking_score/40.0)))

    # print("white cluster safety: " + str(white_cluster_safety))
    # print("black cluster safety: " + str(black_cluster_safety))
    # print('safety score : ' + str(((white_cluster_safety/12.0) - (black_cluster_safety/12.0))))

    board_score = tanh(board_score)
    # print('total score : ' + str(board_score))
    return board_score


def mobility_eval(board, next_turn, is_soft=False):
    """
    a simple eval method that return the value for a current board

    evaluate by mobility

    :param board: the board after move
    :param next_turn: the color that's going to move in this board configuration(the move after board)
    :param is_soft: is it a soft eval so that I can speed things up
    :return: the value of the board
    """
    # current_turn = 'white' if next_turn == 'black' else 'black'

    white_stacks = board['white']
    black_stacks = board['black']

    white_pieces_num = sum([n for n, x, y in white_stacks])
    black_pieces_num = sum([n for n, x, y in black_stacks])

    if not white_stacks and black_stacks:
        return -1
    if not black_stacks and white_stacks:
        return 1
    if not black_stacks and not black_stacks:
        return 0

    white_mobility_score = mobility_score(white_stacks, black_stacks, is_soft=is_soft)
    black_mobility_score = mobility_score(black_stacks, white_stacks, is_soft=is_soft)

    final_score = 5*((white_pieces_num - black_pieces_num)/float(12)) + white_mobility_score - black_mobility_score

    return tanh(final_score)


def mobility_score(stacks, blocks, is_soft=False):

    all_pieces = [("s", n, x, y) for n, x, y in stacks] + [("b", n, x, y) for n, x, y in blocks]
    block_positions = [(x, y) for n, x, y in blocks]

    def mobile_test(s):
        n, x, y = s
        points = 0
        ps = []

        def is_valid_position(position):
            x, y = position
            return 0 <= x <= 7 and 0 <= y <= 7 and (x, y) not in block_positions

        def valid_positions(positions):
            return [p for p in positions if is_valid_position(p)]

        for i in range(1, n+1):
            ps += valid_positions(([x, y+i], [x, y-i], [x+i, y], [x-i, y]))

        for p in ps:
            if is_soft: # soft eval, take it easy
                points += n
            else:
                dic = {'s':0, 'b':0}
                boom_affected_count(p, all_pieces.copy(), dic)
                # print(dic)
                if dic['b'] != 0:
                    diff = dic['b']-dic['s']

                    # you can't move more than diff to that position, otherwise you will be losing more than b
                    points += diff if diff>0 else 0
                else:
                    points += n

        return points

    score = 0
    for stack in stacks:
        stack_score = mobile_test(stack)
        # print("point for stack : " + str(stack) + " is " + str(stack_score))
        score += stack_score

    # 168 = 12 * 14, the maximum mobility of a party can have (one stack with 12 pieces)
    return score/float(168)


def cluster_safety(stacks, blocks, is_stack_turn):

    clusters = get_clusters(stacks[:])
    safety_score = 0
    for cluster in clusters:
        cluster_positions = [s[1::] for s in cluster]
        danger_area = cluster_boom_zone(cluster_positions)

        shortest_d, position = 18, []
        for pos in danger_area:
            for b in blocks:
                d = speedy_manhattan(pos, b)
                shortest_d, position = (d, pos) if d < shortest_d else (shortest_d, position)

        cluster_stacks = len(cluster)
        cluster_pieces = sum([c[0] for c in cluster])

        if is_stack_turn:
            moving_room = float(shortest_d)/float(cluster_stacks)
        else:
            moving_room = float(shortest_d) / float(cluster_stacks)

        moving_room = 1 if moving_room > 1 else moving_room

        safety_score += cluster_pieces * moving_room

    return safety_score


def points_safety(stacks, blocks, is_stack_turn):
    dangerous_points = set()
    stacks_position = [s[1::] for s in stacks]
    for stack in stacks:
        dangerous_points = dangerous_points.union(set(lists_to_tuples(boom_zone(stack[1::], exclude_self=True, check_valid=True))))

    print(dangerous_points)
    dangerous_points = [[x, y] for x, y in dangerous_points if [x, y] not in stacks_position]

    total_lose = []

    for point in dangerous_points:
        directly_affected, indirectly_affected = boom_affected(point, stacks)
        total_affected = directly_affected + indirectly_affected
        lta = len(total_affected)
        lda = len(directly_affected)

        if lda == 1 and not indirectly_affected and directly_affected[0][0]==1:
            continue # those point are harmless

        step_to_point = min([speedy_manhattan(point, b) for b in blocks])

        if is_stack_turn:
            step_to_point += 1 # since we can move first, we have 1 move advantage

        if step_to_point >= 4: # those are a relatively safe so we don't care
            continue

        leave_behind = lda - step_to_point
        if leave_behind > 0:
            # that means something can't be moved in time,
            # we try to lose the least, (noted: directly_affected is sorted)
            lose_pieces = sum([p[0] for p in total_affected[:leave_behind]])

            total_lose.append(lose_pieces)

    return dangerous_points


# shortest_d will represent how many moves needed to go to your current location,
#  you have to leave before they get to you, (and depends on who's turn next)

old_board = {'white': [[1, 0, 0], [1, 1, 0], [2, 1, 1], [4, 4, 0], [4, 6, 1]],
             'black': [[1, 0, 7], [1, 1, 7], [1, 3, 2], [1, 3, 7], [1, 4, 6], [1, 7, 7], [2, 6, 4], [4, 6, 7]]}
#
print_board(old_board)
#
print(mobility_eval(old_board, "white"))

old_board = {'white': [[1, 0, 0], [1, 1, 0], [2, 1, 1], [4, 3, 1]],
             'black': [[1, 0, 7], [1, 1, 7], [1, 3, 7], [1, 4, 7], [1, 6, 7], [1, 7, 7], [5, 6, 6]]}
#
print_board(old_board)
#
print(mobility_eval(old_board, "white"))


#
# stacks = [[1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 3, 0], [1, 4, 0], [2, 3, 3], [2, 6, 0], [2, 6, 1]]
# blocks = [[1, 0, 7], [1, 1, 7], [1, 3, 7], [1, 4, 7], [1, 6, 6], [1, 6, 7], [1, 7, 6], [1, 7, 7], [4, 1, 6]]
#
# print(mobility_score(blocks, stacks))
# a = points_safety([[1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1], [1, 3, 0], [1, 4, 0], [2, 3, 3], [2, 6, 0], [2, 6, 1]],
#                   [[1, 0, 7], [1, 1, 7], [1, 3, 7], [1, 4, 7], [1, 6, 6], [1, 6, 7], [1, 7, 6], [1, 7, 7], [4, 1, 6]], True)
#
# print(a)
#
# # prime_eval(old_board, 'black')
#
# old_board = {'white': [[1, 0, 0], [1, 1, 0], [2, 1, 1], [1, 3, 0], [1, 4, 0], [2, 3, 3], [2, 6, 0], [2, 6, 1]], 'black': [[1, 0, 7], [1, 1, 7], [1, 3, 7], [1, 4, 7], [1, 6, 6], [1, 6, 7], [1, 7, 6], [1, 7, 7], [4, 1, 6]]}
# print_board(old_board)
#
# prime_eval(old_board, 'black')
