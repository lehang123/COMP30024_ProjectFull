import random
from collections import Counter


class RandomAgent:
    def __init__(self, env):
        self.env = env

    def get_move(self):
        legal_moves = self.env.get_legal_moves(include_boom=False)
        move = random.choice(legal_moves)
        return move

    def test(self, agent):
        white_counter = Counter()
        for _ in range(10):
            agent.env.reset()
            reward = agent.env.play([agent, self])
            white_counter.update([reward])

        black_counter = Counter()
        for _ in range(10):
            agent.env.reset()
            reward = agent.env.play([self, agent])
            black_counter.update([reward])

        results = [white_counter[1], white_counter[0], white_counter[-1],
                   black_counter[-1], black_counter[0], black_counter[1]]

        return results
