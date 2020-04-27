from utils import make_nodes
from book_of_moves import is_terrible_move, terrific_move
import time


class MinimaxAgent:
    def __init__(self, env, eval_fun, minimax_depth, sort_eval=None):
        self.env = env
        self.eval_fun = eval_fun
        self.minimax_depth = minimax_depth
        self.sort_eval = sort_eval

    def get_move(self):
        start = time.time()

        is_white_turn = self.env.get_turn() == 'white'
        if is_white_turn:
            turn_count = self.env.get_white_turn_count()
        else:
            turn_count = self.env.get_black_turn_count()

        move = terrific_move(self.env.get_board(), self.env.get_turn(), turn_count)

        if not move:
            value, move = self.minimax_alphabeta(self.env.get_board(), self.minimax_depth, -1.0, 1.0,
                                                 is_white_turn, with_move=True)
            print("value of this : " + str(value))

        end = time.time()
        print("time taken  :" + str(end - start))
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

            # print("final v : " + str(value))
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
            # children = make_nodes(node, self.env.get_turn())
            for child in children:
                new_value = self.minimax_alphabeta(child, depth - 1, α, β, False)
                if new_value >= value:
                    value = new_value
                    move = child
                # value = max(value, self.minimax_alphabeta(child, depth - 1, α, β, False))
                # show_move = nodes_to_move(node, child, 'white')
                # print("maxing with value : " + str(new_value) + " with move : "  + str(show_move))
                α = max(α, value)
                if α >= β:
                    break  # (*β cut - off *)

        else:
            value = 1.0
            # children = make_nodes(node, self.env.get_turn())
            for child in children:
                new_value = self.minimax_alphabeta(child, depth - 1, α, β, True)
                if new_value <= value:
                    value = new_value
                    move = child
                # value = min(value, self.minimax_alphabeta(child, depth - 1, α, β, True))
                # show_move = nodes_to_move(node, child, 'black')
                # print("maxing with value : " + str(new_value) + "with move : " + str(show_move))
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

        # filter_list(available_moves, (lambda x : not is_terrible_move(current_board, x, turn)), [])
        # before = len(available_moves)
        available_moves = [x for x in available_moves if not is_terrible_move(current_board, x, turn)]

        # after = len(available_moves)

        # print(before-after)

        def eval_sort(eval_move):
            return self.sort_eval(eval_move, turn, is_soft=True)

        # todo: make all boom action to the head of the moves as these are the most direct result to the score,
        # todo:  so they most likely to filter others by alpha beta (does the sort function help us with this already)

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
