from environment import Environment
from utils import string_to_tuple

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
        self.environment = Environment()


    def action(self):
        """
        This method is called at the beginning of each of your turns to request
        a choice of action from your program.

        Based on the current state of the game, your player should select and
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """
        # TODO: Decide what action to take, and return it

        # make a all the possible actions that I can take
        # actions = make_nodes(self.game_state, self.colour, self.oppo)

        # TODO: minimax and alpha beta pruning here
        action = input("It's your turn now, your action : ")
        parts = action.split()

        if parts[0] == "MOVE":
            return parts[0], int(parts[1]), string_to_tuple(parts[2]), string_to_tuple(parts[3])
        else:
            return parts[0], string_to_tuple(parts[1])


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
        # TODO: Update state representation in response to action.
        if action[0] == 'MOVE':
            (move, n, before, after) = action
            action = (move, (n, before, after))

        move = self.environment.get_move_from_command(action)
        self.environment.make_move(move)

