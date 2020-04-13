

def make_nodes(board, turn, include_boom=True):
    """

    :param board: the current board
    :param turn: who's turn to move
    :param include_boom: include the boom action in nodes
    :return: all the legal moves
    """
    # all the white stacks are ours to move

    opponent = 'white' if turn == 'black' else 'black'
    stacks = board[turn]
    oppo_stacks = board[opponent]

    blocks = [stack[1:] for stack in oppo_stacks]

    # according to stacks(current state), to generate next moves(nodes)
    nodes = []
    for j in range(len(stacks)):
        stack = stacks[j]
        n = stack[0]
        for i in range(1, n + 1):
            for k in range(1, n + 1):
                moved_up_stacks = move_up(stack, i, k, blocks)
                if moved_up_stacks:
                    update_nodes(oppo_stacks, moved_up_stacks, stacks, nodes, j, turn, opponent)

                moved_down_stacks = move_down(stack, i, k, blocks)
                if moved_down_stacks:
                    update_nodes(oppo_stacks, moved_down_stacks, stacks, nodes, j, turn, opponent)

                moved_left_stacks = move_left(stack, i, k, blocks)
                if moved_left_stacks:
                    update_nodes(oppo_stacks, moved_left_stacks, stacks, nodes, j, turn, opponent)

                moved_right_stacks = move_right(stack, i, k, blocks)
                if moved_right_stacks:
                    update_nodes(oppo_stacks, moved_right_stacks, stacks, nodes, j, turn, opponent)

        if include_boom:
            node = board.copy()
            boom(stack, node)
            nodes.append(node)

    return nodes


def move_up(stack, ns, bs, blocks):
    """
    move up a stack
    :param stack: the stack that moves
    :param ns: number of pieces in stack wants to move
    :param bs: distance that wants to move
    :param blocks: opponent pieces that can't be stepped on
    :return: the result of moving
    """

    n, x, y = stack[0], stack[1], stack[2]
    yf = y + bs
    if 0 <= x <= 7 and 0 <= y <= 6 and n >= ns > 0:

        if n - ns != 0 and [x, yf] not in blocks and 0 <= yf <= 7:
            return [[ns, x, yf], [n - ns, x, y]]
        elif [x, yf] not in blocks and 0 <= yf <= 7:
            return [[ns, x, yf]]
        else:
            return []

    else:
        return []


def move_down(stack, ns, bs, blocks):
    """
    move down a stack
    :param stack: the stack that moves
    :param ns: number of pieces in stack wants to move
    :param bs: distance that wants to move
    :param blocks: opponent piece that can't be stepped on
    :return: the result of moving
    """

    n, x, y = stack[0], stack[1], stack[2]
    yf = y - bs
    if 0 <= x <= 7 and 1 <= y <= 7 and n >= ns > 0:

        if n - ns != 0 and [x, yf] not in blocks and 0 <= yf <= 7:
            return [[ns, x, yf]] + [[n - ns, x, y]]
        elif [x, yf] not in blocks and 0 <= yf <= 7:
            return [[ns, x, yf]]
        else:
            return []
    else:
        return []


def move_left(stack, ns, bs, blocks):
    """
    move left a stack
    :param stack: the stack that moves
    :param ns: number of pieces in stack wants to move
    :param bs: distance that wants to move
    :param blocks: opponent piece that can't be stepped on
    :return: the result of moving
    """

    n, x, y = stack[0], stack[1], stack[2]
    xf = x - bs
    if 1 <= x <= 7 and 0 <= y <= 7 and n >= ns > 0:

        if n - ns != 0 and [xf, y] not in blocks and 0 <= xf <= 7:
            return [[ns, xf, y]] + [[n - ns, x, y]]
        elif [xf, y] not in blocks and 0 <= xf <= 7:
            return [[ns, xf, y]]
        else:
            return []
    else:
        return []


def move_right(stack, ns, bs, blocks):
    """
    move right a stack
    :param stack: the stack that moves
    :param ns: number of pieces in stack wants to move
    :param bs: distance that wants to move
    :param blocks: opponent piece that can't be stepped on
    :return: the result of moving
    """

    n, x, y = stack[0], stack[1], stack[2]
    xf = x + bs
    if 0 <= x <= 6 and 0 <= y <= 7 and n >= ns > 0:

        if n - ns != 0 and [xf, y] not in blocks and 0 <= xf <= 7:
            return [[ns, xf, y]] + [[n - ns, x, y]]
        elif [xf, y] not in blocks and 0 <= xf <= 7:
            return [[ns, xf, y]]
        else:
            return []
    else:
        return []


def boom(origin, data):
    """
    explode the piece
    :param origin: the place that exploded
    :param data: the board information
    """
    white = data['white']
    black = data['black']

    affected_zone = boom_zone(origin[1::])

    affected_pieces = []
    unaffected_whites = []
    unaffected_blacks = []
    for stack in white:
        if stack[1::] in affected_zone:
            affected_pieces.append(stack)
        else:
            unaffected_whites.append(stack)

    for stack in black:
        if stack[1::] in affected_zone:
            affected_pieces.append(stack)
        else:
            unaffected_blacks.append(stack)

    data['white'] = unaffected_whites
    data['black'] = unaffected_blacks
    for piece in affected_pieces:
        boom(piece, data)


def boom_zone(stack, exclude_self=False):
    """
    where is going to be affected after the stack exploded
    :param stack: the stack that's going to exploded
    :param exclude_self: return boom zone including current location ?
    :return all the affected zone
    """
    x, y = stack
    # x = stack[0]
    # y = stack[1]

    if exclude_self:
        return [[x - 1, y + 1], [x, y + 1], [x + 1, y + 1], [x - 1, y], [x + 1, y], [x - 1, y - 1], [x, y - 1],
                [x + 1, y - 1]]
    else:
        return [[x - 1, y + 1], [x, y + 1], [x + 1, y + 1], [x - 1, y], [x, y], [x + 1, y], [x - 1, y - 1], [x, y - 1],
                [x + 1, y - 1]]


def update_nodes(oppo_nodes, action_stacks, stacks, nodes, index, me, oppo):
    """

    """
    node = {}
    my_nodes = action_stacks + stacks
    my_nodes.pop(index + len(action_stacks))  # pop up original position
    node_stack(my_nodes)
    node[me] = my_nodes
    node[oppo] = oppo_nodes
    nodes.append(node)


def node_stack(my_node):
    """
    something when pieces move, they stack on other my pieces, here is to stack
    :param my_node: the node that create and haven't check for stacks
    """
    for i in range(1, len(my_node)):
        if my_node[i][-2::] == my_node[0][-2::]:
            my_node[0][0] += my_node[i][0]
            my_node.pop(i)
            break


def count_pieces(_for, node):
    """
    get the number pieces for an player
    :param _for: opponent or player
    :param node: the current board
    :return: the number of pieces on board for that player
    """
    return sum((map((lambda x:x[0]), node[_for])))


def lists_to_tuples(lists):
    """
    as list is not hashable, sometime we need to cast it as a tuple.
    We deal with list of list a lot, so we need to do a folding like cast for our multi-dimension list
    :param lists: the lists that going to be casted
    """

    if isinstance(lists, list):
        # cast to tuple
        return tuple([lists_to_tuples(l) for l in lists])
    else:
        return lists


def tuples_to_lists(tuples):
    """
    work as the same as lists_to_tuples(lists), but this is backward
    """

    if isinstance(tuples, tuple):
        # cast to tuple
        return [tuples_to_lists(t) for t in tuples]
    else:
        return tuples

def first_max(tup1, tup2):
    return tup1 if tup1[0]>=tup2[0] else tup2



def print_board(board_dict, message="", unicode=False, compact=True, **kwargs):
    """
    For help with visualisation and debugging: output a board diagram with
    any information you like (tokens, heuristic values, distances, etc.).

    Arguments:
    board_dict -- A dictionary with (x, y) tuples as keys (x, y in range(8))
        and printable objects (e.g. strings, numbers) as values. This function
        will arrange these printable values on the grid and output the result.
        Note: At most the first 3 characters will be printed from the string
        representation of each value.
    message -- A printable object (e.g. string, number) that will be placed
        above the board in the visualisation. Default is "" (no message).
    unicode -- True if you want to use non-ASCII symbols in the board
        visualisation (see below), False to use only ASCII symbols.
        Default is False, since the unicode symbols may not agree with some
        terminal emulators.
    compact -- True if you want to use a compact board visualisation, with
        coordinates along the edges of the board, False to use a bigger one
        with coordinates alongside the printable information in each square.
        Default True (small board).

    Any other keyword arguments are passed through to the print function.
    """
    if unicode:
        if compact:
            template = """# {}
#    ┌───┬───┬───┬───┬───┬───┬───┬───┐
#  7 │{:}│{:}│{:}│{:}│{:}│{:}│{:}│{:}│
#    ├───┼───┼───┼───┼───┼───┼───┼───┤
#  6 │{:}│{:}│{:}│{:}│{:}│{:}│{:}│{:}│
#    ├───┼───┼───┼───┼───┼───┼───┼───┤
#  5 │{:}│{:}│{:}│{:}│{:}│{:}│{:}│{:}│
#    ├───┼───┼───┼───┼───┼───┼───┼───┤
#  4 │{:}│{:}│{:}│{:}│{:}│{:}│{:}│{:}│
#    ├───┼───┼───┼───┼───┼───┼───┼───┤
#  3 │{:}│{:}│{:}│{:}│{:}│{:}│{:}│{:}│
#    ├───┼───┼───┼───┼───┼───┼───┼───┤
#  2 │{:}│{:}│{:}│{:}│{:}│{:}│{:}│{:}│
#    ├───┼───┼───┼───┼───┼───┼───┼───┤
#  1 │{:}│{:}│{:}│{:}│{:}│{:}│{:}│{:}│
#    ├───┼───┼───┼───┼───┼───┼───┼───┤
#  0 │{:}│{:}│{:}│{:}│{:}│{:}│{:}│{:}│
#    └───┴───┴───┴───┴───┴───┴───┴───┘
# y/x  0   1   2   3   4   5   6   7"""
        else:
            template = """# {}
# ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
# │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │
# │ 0,7 │ 1,7 │ 2,7 │ 3,7 │ 4,7 │ 5,7 │ 6,7 │ 7,7 │
# ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
# │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │
# │ 0,6 │ 1,6 │ 2,6 │ 3,6 │ 4,6 │ 5,6 │ 6,6 │ 7,6 │
# ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
# │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │
# │ 0,5 │ 1,5 │ 2,5 │ 3,5 │ 4,5 │ 5,5 │ 6,5 │ 7,5 │
# ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
# │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │
# │ 0,4 │ 1,4 │ 2,4 │ 3,4 │ 4,4 │ 5,4 │ 6,4 │ 7,4 │
# ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
# │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │
# │ 0,3 │ 1,3 │ 2,3 │ 3,3 │ 4,3 │ 5,3 │ 6,3 │ 7,3 │
# ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
# │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │
# │ 0,2 │ 1,2 │ 2,2 │ 3,2 │ 4,2 │ 5,2 │ 6,2 │ 7,2 │
# ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
# │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │
# │ 0,1 │ 1,1 │ 2,1 │ 3,1 │ 4,1 │ 5,1 │ 6,1 │ 7,1 │
# ├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
# │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │ {:} │
# │ 0,0 │ 1,0 │ 2,0 │ 3,0 │ 4,0 │ 5,0 │ 6,0 │ 7,0 │
# └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘"""
    else:
        if compact:
            template = """# {}
#    +---+---+---+---+---+---+---+---+
#  7 |{:}|{:}|{:}|{:}|{:}|{:}|{:}|{:}|
#    +---+---+---+---+---+---+---+---+
#  6 |{:}|{:}|{:}|{:}|{:}|{:}|{:}|{:}|
#    +---+---+---+---+---+---+---+---+
#  5 |{:}|{:}|{:}|{:}|{:}|{:}|{:}|{:}|
#    +---+---+---+---+---+---+---+---+
#  4 |{:}|{:}|{:}|{:}|{:}|{:}|{:}|{:}|
#    +---+---+---+---+---+---+---+---+
#  3 |{:}|{:}|{:}|{:}|{:}|{:}|{:}|{:}|
#    +---+---+---+---+---+---+---+---+
#  2 |{:}|{:}|{:}|{:}|{:}|{:}|{:}|{:}|
#    +---+---+---+---+---+---+---+---+
#  1 |{:}|{:}|{:}|{:}|{:}|{:}|{:}|{:}|
#    +---+---+---+---+---+---+---+---+
#  0 |{:}|{:}|{:}|{:}|{:}|{:}|{:}|{:}|
#    +---+---+---+---+---+---+---+---+
# y/x  0   1   2   3   4   5   6   7"""
        else:
            template = """# {}
# +-----+-----+-----+-----+-----+-----+-----+-----+
# | {:} | {:} | {:} | {:} | {:} | {:} | {:} | {:} |
# | 0,7 | 1,7 | 2,7 | 3,7 | 4,7 | 5,7 | 6,7 | 7,7 |
# +-----+-----+-----+-----+-----+-----+-----+-----+
# | {:} | {:} | {:} | {:} | {:} | {:} | {:} | {:} |
# | 0,6 | 1,6 | 2,6 | 3,6 | 4,6 | 5,6 | 6,6 | 7,6 |
# +-----+-----+-----+-----+-----+-----+-----+-----+
# | {:} | {:} | {:} | {:} | {:} | {:} | {:} | {:} |
# | 0,5 | 1,5 | 2,5 | 3,5 | 4,5 | 5,5 | 6,5 | 7,5 |
# +-----+-----+-----+-----+-----+-----+-----+-----+
# | {:} | {:} | {:} | {:} | {:} | {:} | {:} | {:} |
# | 0,4 | 1,4 | 2,4 | 3,4 | 4,4 | 5,4 | 6,4 | 7,4 |
# +-----+-----+-----+-----+-----+-----+-----+-----+
# | {:} | {:} | {:} | {:} | {:} | {:} | {:} | {:} |
# | 0,3 | 1,3 | 2,3 | 3,3 | 4,3 | 5,3 | 6,3 | 7,3 |
# +-----+-----+-----+-----+-----+-----+-----+-----+
# | {:} | {:} | {:} | {:} | {:} | {:} | {:} | {:} |
# | 0,2 | 1,2 | 2,2 | 3,2 | 4,2 | 5,2 | 6,2 | 7,2 |
# +-----+-----+-----+-----+-----+-----+-----+-----+
# | {:} | {:} | {:} | {:} | {:} | {:} | {:} | {:} |
# | 0,1 | 1,1 | 2,1 | 3,1 | 4,1 | 5,1 | 6,1 | 7,1 |
# +-----+-----+-----+-----+-----+-----+-----+-----+
# | {:} | {:} | {:} | {:} | {:} | {:} | {:} | {:} |
# | 0,0 | 1,0 | 2,0 | 3,0 | 4,0 | 5,0 | 6,0 | 7,0 |
# +-----+-----+-----+-----+-----+-----+-----+-----+"""

    # convert to print format
    if 'white' in board_dict:
        board_dict = json_to_board(board_dict)

    # board the board string
    coords = [(x, 7 - y) for y in range(8) for x in range(8)]
    cells = []
    for xy in coords:
        if xy not in board_dict:
            cells.append("   ")
        else:
            cells.append(str(board_dict[xy])[:3].center(3))
    # print it
    print(template.format(message, *cells), **kwargs)


def json_to_board(data):
    """
    :param data: the data in json format which easy to be used to run
    :return: the data in the print_board required format to be used to print
    """
    dict = {}
    white = data['white']
    for p in white:
        position = (p[1], p[2])
        stack = 'w' + str(p[0])
        dict[position] = stack

    black = data['black']
    for p in black:
        position = (p[1], p[2])
        stack = 'b' + str(p[0])
        dict[position] = stack

    return dict


def board_dict_to_tuple(dic):
    """
    :param dic: dictionary that convert to tuple
    """
    white_pieces = dic['white']
    black_pieces = dic['black']

    return [lists_to_tuples(white_pieces), lists_to_tuples(black_pieces)]


def string_to_tuple(string):
    x, y = string.split(",")
    return int(x), int(y)


def nodes_to_move(before, after, color):
    """
    to convert the change of two node (before and after) to the user input command
    :param before: the node before (in dictionary form) {'white': xxx, 'black': xxx}
    :param after: the node after (in dictionary form) {'white': xxx, 'black': xxx}
    :param color: the color that moved
    :return: the user input command
    """

    cur_pieces = lists_to_tuples(before[color])
    nex_pieces = lists_to_tuples(after[color])

    cur_pieces_num = sum([w[0] for w in cur_pieces])
    nex_pieces_num = sum([w[0] for w in nex_pieces])
    if cur_pieces_num == nex_pieces_num:
        # nothing boom, it's an move action
        _before = set(cur_pieces).difference(nex_pieces)
        _after = set(nex_pieces).difference(cur_pieces)

        # the movement
        n_m, x_1, y_1, x_2, y_2 = (0, -1, -1, -1, -1)

        if len(_before) == len(_after):
            # no difference in positions, means move from stack to stack
            if len(_before) == 2:
                [(b_n, b_x, b_y), (_, b_x1, b_y1)] = _before
                for (n, x, y) in _after:
                    if x == b_x and y == b_y:
                        n_m = n-b_n
                if n_m>0:
                    x_1, y_1, x_2, y_2 = b_x1, b_y1, b_x, b_y
                else:
                    x_1, y_1, x_2, y_2 = b_x, b_y, b_x1, b_y1
            elif len(_before) == 1:
                # this moved a full stacks
                [(n_m, x_1, y_1)] = _before
                [(_, x_2, y_2)] = list(_after)
        else:
            _before_positions = lists_to_tuples([[x, y] for (n, x, y) in _before])
            _after_positions = lists_to_tuples([[x, y] for (n, x, y) in _after])

            move_from = set(_before_positions).difference(_after_positions)
            move_to = set(_after_positions).difference(_before_positions)

            if move_to:
                # move to some place new
                [(x_2, y_2)] = move_to
                for (n, x, y) in _after:
                    if x == x_2 and y == y_2:
                        n_m = n
                    else:
                        x_1, y_1 = x, y
            elif move_from:
                # move to an known place
                [(x_1, y_1)] = move_from
                for (n, x, y) in _before:
                    if x == x_1 and y == y_1:
                        n_m = n
                    else:
                        x_2, y_2 = x, y

        return 'MOVE', n_m, (x_1, y_1), (x_2, y_2)
        # print_move(n_m, x_1, y_1, x_2, y_2)

    elif nex_pieces_num<cur_pieces_num:
        # white become less, boomed
        (_, x, y) = list(set(cur_pieces).difference(nex_pieces))[0]
        # print_boom(x, y)
        return 'BOOM', (x, y)
    else:
        print("panic, growing number of whites")
        return None

