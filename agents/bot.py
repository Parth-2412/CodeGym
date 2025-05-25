import pandas as pd
import numpy as np
import re
import sys
from tabulate import tabulate

class Bot:

    def __init__(self):
        # get start input
        self.get_input()
        self.directions = [("U", (-1,0)), ("D", (1,0)), ("L", (0,-1)),("R", (0,1))]
        _,size = self.get_input()
        self.size = size
        self.map = pd.DataFrame([["E"]*size  for _ in range(size)])
        self.position = tuple(self.get_input())
        self.used_teleports = set()
        self.next = (1,1)
        self.active_chain = False
        self.place_tile(*self.position)
        self.points = 0
        # Read amplifier data
        header = self.get_input()
        if header[0] == "AMPLIFIERS":
            _, L = header
            for _ in range(L):
                r, c = self.get_input()
                self.set_cell(r,c,'A')

        self.play()

    def set_cell(self,x : int,y : int, val : str):
        self.map.iat[x - 1, y - 1] = val
    
    def get_cell(self, x:int, y:int) -> str:
        return self.map.iat[x - 1, y - 1] 

    @staticmethod
    def is_adjacent(coord1 : tuple[int,int],coord2 : tuple[int,int]):
        x1,y1 = coord1
        x2,y2 = coord2
        return (x1 == x2 and abs(y1-y2) == 1) or (y1==y2 and abs(x1-x2) == 1)
    
    def place_tile(self, x:int, y:int):

        result = self.search(fr"{self.next[0]}.{self.next[1]-1}")
        if self.active_chain and len(result) == 0:
            raise Exception(self.show())
        if self.active_chain and not Bot.is_adjacent(self.position, result[0] ):
            self.terminate()

        self.set_cell(x,y, f"{self.next[0]}.{self.next[1]}")
        self.next = (self.next[0], self.next[1] + 1)
        self.active_chain = True
    
    def __get_coords(self, matches : pd.DataFrame) -> list[tuple[int,int]]:
        coords = [(int(a),int(b)) for (a,b) in (zip(*matches.to_numpy().nonzero()))]
        return [tuple(map(int, x)) for x in (np.array(coords) + 1)]
    def search(self, pattern:str):
        mask = self.map.map(lambda x: bool(re.search(pattern, str(x))))
        return self.__get_coords(mask)
    

    
    def destroy_chain(self,chain : int):
        coords = self.search(fr"{chain}\.[1-9]+$")
        rows, cols = zip(*coords)
        rows = np.array(rows) - 1
        cols = np.array(cols) - 1
        self.map.values[rows, cols] = "E"
        return coords
    
    def terminate(self):
        if self.active_chain:
            self.next = (self.next[0] +1 , 1)
            self.active_chain = False
            return True
        return False

    def update_position(self, dr : int, dc : int):
        self.position = (self.position[0] + dr, self.position[1] + dc)

    def get_input(self):
        inp = input()
        return[int(a) if a.isdigit() else a for a in inp.split()]
    
    def send_message(self,message:str):
        print(message)
        sys.stdout.flush()

    def show(self):
        return tabulate(self.map, headers='keys', tablefmt='psql')
    def decide(self) -> str:
        raise Exception("You are supposed to implement this function in the subclass")
    
    def play(self):
        while True:
            instruction_type, *inp = self.get_input()
            if instruction_type == "GAMEOVER":
                break
            elif instruction_type =="TURN":
                move = self.decide()
                self.send_message(move)
                while (inp := self.get_input())[0] != "TURNOVER":
                    instruction_type, *inp = inp
                    if instruction_type == "DESTROYED":
                        n, = inp
                        for _ in range(n):
                            r,c = self.get_input()
                            self.set_cell(r,c,"E")
                    elif instruction_type == "TILE":
                        self.set_cell(*self.position, 'U')
                    elif instruction_type == "EMPTY":
                        self.set_cell(*self.position, 'E')
                    elif instruction_type == "HINT":
                        i,= inp
                        self.set_cell(*self.position, f"U.{i}")
                    elif instruction_type == "FAILED":
                        self.points -= 8
                    elif instruction_type == "TERMINATED":
                        self.terminate()
            elif instruction_type == "UPDATE":
                update_type,x,y = inp
                if update_type == "TILE":
                    self.set_cell(x,y,'U')
                elif update_type == "DESTROYED":
                    cell = self.get_cell(x,y)
                    chain = int(cell.split(".")[0])
                    if chain == self.next[0]:
                        self.terminate()
                    self.destroy_chain(chain)
                
