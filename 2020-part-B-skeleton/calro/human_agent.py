from alice.utils import string_to_tuple


class HumanAgent:

    def __init__(self, env):
        self.env = env

    def get_move(self):

        action = input("It's your turn now, your action : ")
        parts = action.split()

        def handle_action(action_parts):

            if action_parts[0] == "MOVE":
                while len(action_parts) != 4:
                    input_action = input("WRONG MOVE, plz enter again, your action : ")
                    action_parts = input_action.split()

                input_command = action_parts[0], int(action_parts[1]), \
                                string_to_tuple(action_parts[2]), string_to_tuple(action_parts[3])

            elif action_parts[0] == "BOOM":
                while len(action_parts) != 2:
                    input_action = input("WRONG BOOM, plz enter again, your action : ")
                    action_parts = input_action.split()

                input_command = action_parts[0], string_to_tuple(action_parts[1])
            else:
                input_action = input("WRONG COMMAND, plz enter again, your action : ")
                action_parts = input_action.split()
                return handle_action(action_parts)

            if input_command[0] == 'MOVE':
                (move, n, before, after) = input_command
                input_command = (move, (n, before, after))

            return input_command

        command = handle_action(parts)
        result = self.env.get_move_from_command(command)

        return result