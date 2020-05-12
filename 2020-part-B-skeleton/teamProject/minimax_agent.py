from teamProject.book_of_moves import is_terrible_move, terrific_move
from teamProject.utils import make_nodes


class MinimaxAgent:
    def __init__(self, env, eval_fun, minimax_depth, sort_eval=None):
        self.env = env
        self.eval_fun = eval_fun
        self.minimax_depth = minimax_depth
        self.sort_eval = sort_eval

    def get_move(self):
        """
        Get changes on the board
        :return: the move
        """
        white_num = self.env.get_white_num()
        black_num = self.env.get_black_num()

        is_white_turn = self.env.get_turn() == 'white'
        if is_white_turn:
            turn_count = self.env.get_white_turn_count()
        else:
            turn_count = self.env.get_black_turn_count()

        move = terrific_move(self.env.get_board(), self.env.get_turn(), turn_count)

        search_depth = self.minimax_depth
        total_token = (white_num + black_num)

        if 5 < total_token < 16:
            search_depth = 3
        elif 0 < total_token <= 5:
            search_depth = 4

        if not move:
            value, move = self.minimax_alphabeta(self.env.get_board(), search_depth, -1.0, 1.0,
                                                 is_white_turn, with_move=True)

        return move

    def minimax_alphabeta(self, node, depth, α, β, maximizing, with_move=False):
        """
        minimax_alphabeta cut off search, used to eval all possible child nodes of the current state and get back the value,
        then we choose the node that has the highest value

        :param node: the node that we are evaluating
        :param depth: the cut-off depth
        :param α: alpha (in minimizing, the value used to cut-off loop if we find a value smaller than alpha)
        :param β: beta (in maximizing, the value used to cut-off loop if we find a value greater than beta)
        :param maximizing: is it maximizing now
        :param with_move: does return move as well?
        :return: the ultimate value of the node, and the leaf node for the value
        """

        turn_to = "white" if maximizing else "black"

        if self.env.get_reward() is not None:
            value = self.env.get_reward()

            if with_move:
                return value, node
            else:
                return value
        elif depth == 0:
            value = self.eval_fun(node, turn_to)

            if with_move:
                return value, node
            else:
                return value  # the eval value of node

        move = node

        children = make_nodes(node, turn_to)
        children = self.filter(node, children, turn_to)
        if maximizing:
            value = -1.0
            for child in children:
                new_value = self.minimax_alphabeta(child, depth - 1, α, β, False)
                if new_value >= value:
                    value = new_value
                    move = child
                α = max(α, value)
                if α >= β:
                    break  # (*β cut - off *)

        else:
            value = 1.0
            for child in children:
                new_value = self.minimax_alphabeta(child, depth - 1, α, β, True)
                if new_value <= value:
                    value = new_value
                    move = child
                β = min(β, value)
                if α >= β:
                    break  # (*α cut - off *)

        if with_move:
            return value, move
        else:
            return value

    def filter(self, current_board, available_moves, turn):
        """
        to filter and sorted moves in order the improve our speed of
            alpha beta pruning(hopefully)

        :param current_board: the current board which we use to evaluate the current situation
        :param available_moves: the move that we have so we can filter or sort in order the improve our speed of
            alpha beta pruning
        :param turn: who's turn is it
        :return: the filtered moves
        """
        available_moves = [x for x in available_moves if not is_terrible_move(current_board, x, turn)]

        def eval_sort(eval_move):
            return self.sort_eval(eval_move, turn, is_soft=True)

        """
        sort moves by current evaluate function, if we have good ordering, we can prune more for the alpha beta,
        since the difference from state the state is keeping to minial due to the TD lambda nature, I hope this is
        a good enough approximation

        note : sort does help in improving the alpha beta search, however, the sorting taking extra time, and
         it's not a perfect eval_fun, so in total, it's not a very good improvement, I suspect that if we can improve
         more for our eval_fun, this could get better as well.
        """

        is_maximizing = turn == 'white'
        available_moves = sorted(available_moves, key=eval_sort, reverse=is_maximizing)

        return available_moves
