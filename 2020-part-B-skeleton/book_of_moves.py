"""
a "book" that keep record of tactics in game of Expendibots
"""
from utils import lists_to_tuples, nodes_to_move, boom_zone, clusters_count, print_board, boom_affected_count

def is_terrible_move(board, move, turn):
    """
    these are the terrible moves, you should NEVER CONSIDER IT

    :param board: the current move
    :param move: the board after move
    :param turn: who's turn now
    :return: is this move bad
    """
    oppo_turn = 'black' if turn == 'white' else 'white'

    my_pieces = board[turn]
    oppo_pieces = board[oppo_turn]

    my_pieces_num = 0
    my_stacks_num = len(my_pieces)
    for mp in my_pieces:
        my_pieces_num += mp[0]


    oppo_pieces_num = 0
    oppo_stacks_num = len(oppo_pieces)
    for op in oppo_pieces:
        oppo_pieces_num += op[0]

    my_future_pieces = move[turn]
    my_future_pieces_num = 0
    my_future_stacks_num = len(my_future_pieces)
    for mfp in my_future_pieces:
        my_future_pieces_num += mfp[0]

    oppo_future_pieces = move[oppo_turn]
    oppo_future_pieces_num = 0
    oppo_future_stacks_num = len(oppo_future_pieces)
    for ofp in oppo_future_pieces:
        oppo_future_pieces_num += ofp[0]

    ########### after BOOM you lose more than your opponent  #############
    bad_trade = (oppo_pieces_num - oppo_future_pieces_num) < (my_pieces_num - my_future_pieces_num)

    if bad_trade and (oppo_future_pieces_num != 0):
        # this is a bad trade, don't do it
        return True
    ######### END OF CASE #########

    ################# you separate stack, or create chain reaction #################
    action = nodes_to_move(board, move, turn)
    if action[0] == 'MOVE':
        move_num, move_from, move_to = action[1], action[2], action[3]
        oppo_stacks_positions = [[x, y] for n, x, y in oppo_pieces]
        oppo_stacks_positions = lists_to_tuples(oppo_stacks_positions)
        move_from_boom_zones = lists_to_tuples(boom_zone(move_from))
        move_to_boom_zones = lists_to_tuples(boom_zone(move_to))

        enemy_around_from = set(oppo_stacks_positions).intersection(move_from_boom_zones)
        enemy_around_to = set(oppo_stacks_positions).intersection(move_to_boom_zones)

        move_from_num = 0

        for (n, x , y) in my_pieces:
            if (x, y) == move_from:
                move_from_num = n
                break

        dic = {'s':0, 'b':0}
        all_pieces = [("s", n, x, y) for n, x, y in my_future_pieces] \
                     + [("b", n, x, y) for n, x, y in oppo_future_pieces]
        boom_affected_count(move_to, all_pieces, dic)
        if dic['b'] != 0 and dic['s']>dic['b']:
            # you moving to a place that will makes you die more
            return True

        move_more_than_one = (move_from_num != move_num)
        if not enemy_around_from and not enemy_around_to and move_more_than_one:
            # you separate stack more than one not for killing or running away
            # todo: change to, if don't (kill) or (gain single stack control), wo don't separate
            return True

        if enemy_around_from and (move_from_num - move_num)>1 and not enemy_around_to:
            # you running away and leave more than one piece
            return True

        if enemy_around_to and move_num > 1 and not enemy_around_from:
            # you using too much to kill
            return True

        if my_future_stacks_num == my_stacks_num:
            my_stacks_positions = [[x, y] for n, x, y in my_pieces]

            my_future_stacks_positions = [[x, y] for n, x, y in my_future_pieces]

            cluster_before = clusters_count(my_stacks_positions)

            cluster_after = clusters_count(my_future_stacks_positions)

            if cluster_after<cluster_before:
                # you are creating chain explosion so your oppo can kill you much easier
                return True
    ######### END OF CASE #########

    return False


def terrific_move(board, turn, turn_num):
    """
    this is the terrific move, you should just do it right away

    :param board: the current move
    :param turn: who's turn now
    :param turn_num: which turn is it for the current player
    :return: the move, if there is one
    """

    oppo = "black" if turn == "white" else "white"
    stacks = board[turn]
    blocks = board[oppo]

    if turn == "white":
        if turn_num == 0:
            board["white"] = [[1, 0, 0], [1, 1, 0], [1, 0, 1], [1, 1, 1],
                              [1, 3, 0], [1, 4, 0], [2, 3, 1],
                              [1, 6, 0], [1, 7, 0], [1, 6, 1], [1, 7, 1]]

            return board
        elif turn_num == 1:
            board["white"] = [[1, 0, 0], [1, 1, 0], [2, 1, 1],
                              [1, 3, 0], [1, 4, 0], [2, 3, 1],
                              [1, 6, 0], [1, 7, 0], [1, 6, 1], [1, 7, 1]]

            return board
        elif turn_num == 2:
            board["white"] = [[1, 0, 0], [1, 1, 0], [2, 1, 1],
                              [1, 3, 0], [1, 4, 0], [2, 3, 1],
                              [1, 6, 0], [1, 7, 0], [2, 6, 1]]

            return board
        else:
            return None
    else:
        if turn_num == 0:
            board["black"] = [[1, 0, 7], [1, 1, 7], [1, 0, 6], [1, 1, 6],
                              [1, 3, 7], [1, 4, 7], [2, 3, 6],
                              [1, 6, 7], [1, 7, 7], [1, 6, 6], [1, 7, 6]]

            return board
        elif turn_num == 1:
            board["black"] = [[1, 0, 7], [1, 1, 7], [2, 1, 6],
                              [1, 3, 7], [1, 4, 7], [2, 3, 6],
                              [1, 6, 7], [1, 7, 7], [1, 6, 6], [1, 7, 6]]

            return board
        elif turn_num == 2:
            board["black"] = [[1, 0, 7], [1, 1, 7], [2, 1, 6],
                              [1, 3, 7], [1, 4, 7], [2, 3, 6],
                              [1, 6, 7], [1, 7, 7], [2, 6, 6]]

            return board
        else:
            return None


# now = {'white':[[1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 3, 0], [1, 3, 1], [1, 4, 0], [3, 4, 1], [1, 6, 0], [1, 7, 0], [1, 1, 5]],
#        'black':[[1, 0, 6], [1, 0, 7], [1, 1, 6], [1, 1, 7], [2, 3, 6], [2, 4, 7], [1, 6, 6], [1, 6, 7], [1, 7, 6], [1, 7, 7]]}
# print_board(now)
# future = {'white':[[1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 3, 0], [1, 3, 1], [1, 4, 0], [3, 4, 1], [1, 6, 0], [1, 7, 0]],
#        'black':[[2, 3, 6], [2, 4, 7], [1, 6, 6], [1, 6, 7], [1, 7, 6], [1, 7, 7]]}
# print_board(future)
# #
# print(is_terrible_move(now, future, 'white'))