from utils import string_to_tuple


class HumanAgent:

    def __init__(self, env):
        self.env = env

    def get_move(self):
        action = input("It's your turn now, your action : ")
        parts = action.split()
        # print(parts)

        if parts[0] == "MOVE":
            while len(parts) != 4:
                action = input("plz enter again, your action : ")
                parts = action.split()

            command = parts[0], int(parts[1]), string_to_tuple(parts[2]), string_to_tuple(parts[3])

        else:
            command = parts[0], string_to_tuple(parts[1])

        if command[0] == 'MOVE':
            (move, n, before, after) = command
            command = (move, (n, before, after))

        result = self.env.get_move_from_command(command)
        # print(result)

        return result