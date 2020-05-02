from alice import environment
from alice.evaluate import mobility_eval
from alice.minimax_agent import MinimaxAgent
from alice.utils import nodes_to_move


class ExamplePlayer:
    def __init__(self, colour):
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your
        program will play as (White or Black). The value will be one of the
        strings "white" or "black" correspondingly.
        """
        self.environment = environment.Environment()
        self.agent = MinimaxAgent(self.environment, mobility_eval, minimax_depth=2, sort_eval=mobility_eval)

    def action(self):
        """
        This method is called at the beginning of each of your turns to request
        a choice of action from your program.

        Based on the current state of the game, your player should select and
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """

        move = self.agent.get_move()
        command = nodes_to_move(self.environment.get_board(), move, self.environment.get_turn())

        return command


    def update(self, colour, action):
        """
        This method is called at the end of every turn (including your player’s
        turns) to inform your player about the most recent action. You should
        use this opportunity to maintain your internal representation of the
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (White or Black). The value will be one of the strings "white" or
        "black" correspondingly.

        The parameter action is a representation of the most recent action
        conforming to the spec's instructions for representing actions.

        You may assume that action will always correspond to an allowed action
        for the player colour (your method does not need to validate the action
        against the game rules).
        """
        if action[0] == 'MOVE':
            (move, n, before, after) = action
            action = (move, (n, before, after))

        move = self.environment.get_move_from_command(action)
        self.environment.make_move(move)

