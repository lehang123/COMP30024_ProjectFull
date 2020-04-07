from boby.utils import make_nodes


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

        white_init = [[1, x, y] for x in range(0,8) for y in range(0,2) if (x != 2 and x != 5)]
        black_init = [[1, x, y] for x in range(0,8) for y in range(6,8) if (x != 2 and x != 5)]
        self.game_state = {'white': white_init, 'black': black_init}
        self.me = colour
        if self.me == 'white':
            self.oppo = 'black'
        else :
            self.oppo = 'white'

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
        actions = make_nodes(self.game_state, self.me, self.oppo)

        # TODO: minimax and alpha beta pruning here


        return ("BOOM", (0, 0))


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
