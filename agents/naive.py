import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.bot import Bot
import random
class Agent1(Bot):
    def decide(self):
        cell = self.get_cell(*self.position)
        if cell == "U":
            return "INFO"
        elif cell == "U.1":
            return "DESTROY"
        elif cell == "E":
            self.place_tile(*self.position)
            return "LAY"
        else:
            original_posn = self.position
            random.shuffle(self.directions)
            i = 0
            valid_dir = None
            while i < 4:
                dir = self.directions[i]
                self.update_position(*dir[1])
                x,y = self.position
                valid = x >= 1 and x <= self.size and y >= 1 and y <= self.size
                if valid:
                    valid_dir = dir[0]
                    break
                else:
                    self.position = original_posn
                i += 1
            move = f"MOVE {valid_dir}"
            return move
        
agent = Agent1()
agent.play()