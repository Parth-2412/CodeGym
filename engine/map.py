import pandas as pd
import numpy as np
import re
from random import randint
from tabulate import tabulate
from .files import validate_file
K = 10

class Map:
    def __init__(self, map_path : str):
        validate_file("csv")(map_path)
        self.path = map_path            
    def load(self):
        self.map = pd.read_csv(self.path)
        n = min(self.map.shape)
        self.size = n
    
    def __get_coords(self, matches : pd.DataFrame) -> list[tuple[int,int]]:
        coords = [(int(a),int(b)) for (a,b) in (zip(*matches.to_numpy().nonzero()))]
        return [tuple(map(int, x)) for x in (np.array(coords) + 1)]

    def search(self, pattern:str):
        mask = self.map.map(lambda x: bool(re.search(pattern, str(x))))
        return self.__get_coords(mask)
    
    def destroy_chain(self,chain : int,i:int):
        coords = self.search(fr"{chain}\.[1-9]+\.{i}$")
        rows, cols = zip(*coords)
        rows = np.array(rows) - 1
        cols = np.array(cols) - 1
        self.map.values[rows, cols] = "E"
        return coords
    def get_spawn_points(self,n : int = 2):
        return [(randint(1,self.size), randint(1,3) if i & 1 == 0 else randint(self.size-2,self.size)) for i in range(n)]

    def get_k(self, turns):
        return K
    
    
    def place_tile(self,coords : tuple[int,int],info : tuple[int,int,int]):
        x,y = coords
        self.map.iat[x-1,y-1] =  f"-{Map.get_rep(info)}"

    @staticmethod
    def get_search_rep(info : tuple[int,int,int]):
        chain,tile,agent = info
        return fr"{chain}\.{tile}\.{agent}$"
    
    @staticmethod
    def get_rep(info : tuple[int,int,int]):
        chain,tile,agent = info
        return f"{chain}.{tile}.{agent}"
    

    def place_tile(self,coords : tuple[int,int], info : tuple[int,int,int]):
        x,y = coords
        self.map.iat[x-1,y-1] = Map.get_rep(info)

    @staticmethod
    def is_adjacent(coord1 : tuple[int,int],coord2 : tuple[int,int]):
        x1,y1 = coord1
        x2,y2 = coord2
        return (x1 == x2 and abs(y1-y2) == 1) or (y1==y2 and abs(x1-x2) == 1)
    def mark_seen(self,x:int,y:int):
        cell = self.cell(x,y)
        if cell.startswith("-"):
            self.map.iat[x-1,y-1] = cell[1:]
    
    def is_seen(self,x:int,y:int):
        return not self.cell(x,y).startswith("-")

    def is_occupied_by_enemy(self,x:int,y:int,i:int) -> list[int]:
        cell : str = self.cell(x,y)
        cell = cell.split(".")
        if len(cell) != 3 or int(cell[-1]) == i:
            return None
        cell = [abs(int(c)) for c in cell]
        return cell
    
    def is_occupied_by_self(self,x:int,y:int,i:int) -> list[int]:
        cell : str = self.cell(x,y)
        cell = cell.split(".")
        if len(cell) != 3 or int(cell[-1]) != i:
            return None
        cell = [abs(int(c)) for c in cell]
        return cell

    def get_amplifiers(self):
        return self.__get_coords(self.map == "A")
    
    def is_empty_at(self,x: int,y:int):
        cell = self.cell(x,y)
        return cell in ["E", "T", "A"]
    
    def cell(self,x : int,y : int) -> str:
        return self.map.iat[x-1,y-1]
    
    def get_chain_length(self,chain:int,i:int):
        return len(self.search(fr"{chain}\.[1-9]+\.{i}$"))

    # TODO: validate whether a map is valid
    def validate_map(self):
        valid_values = {"A", "E", "T"}
        invalid = ~self.map.map(lambda x: str(x) in valid_values)
        if invalid.values.any():
            raise Exception("Map is invalid")
    def show(self):
        print(tabulate(self.map, headers='keys', tablefmt='psql'))