import numpy as np


def pieces_positions_vectorize(board, player, opponent, turn):
    """
    a simple vectorize method that keeping track on each piece and their position

    len of vector: 129 = 64(player's piece on each position of the board (range: 0~12, num of pieces))
                    + 64(opponent's piece on each position of the board (range: 0~12, num of pieces))
                    + 1(who's turn to move(range:0~1, 1 is player, 0 is opponent))

    the 64 len's position vector: from index 0 to 63, correspond to (0,0), (0,1), (0,2)... (7,7) on board

    :param board: the current board that we are going to vectorize
    :param player: the player's color
    :param opponent: the opponent's color
    :param turn: the color that's going to move in this board configuration
    :return: the vector
    """

    white_pieces = board[player]
    black_pieces = board[opponent]

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
    if turn == player:
        vector = np.append(vector, [1])
    else:
        vector = np.append(vector, [0])

    return vector