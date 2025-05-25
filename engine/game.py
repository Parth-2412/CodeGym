from pathlib import Path
import json
from .agent import Agent
from .map import Map
from .env import dev

class State:

    def __init__(self, start : tuple[int,int]):
        self.position = start
        self.points = 0
        self.teleported_chains = []
        self.current_chain_index = 1
        self.next_tile_index = 1
        self.chain_active = False

order = ["TERMINATE", "TELEPORT", "MOVE", "LAY"]

class Game:

    def __init__(self, id, agents : list[Agent], map : Map, turns = 150):
        self.id = id
        self.agents = agents
        self.n_agents = len(self.agents)
        self.map = map
        self.M = turns
        self.game_log = []
        self.state : list[State] = []
        self.amplifiers = []
        for agent in self.agents:
            f1 = agent.send_message
            agent.send_message = (lambda f1=f1, agent_id=agent.id: 
                                lambda message: self.log_output(f1(message), agent_id))()

            f2 = agent.get_action
            agent.get_action = (lambda f2=f2, agent_id=agent.id: 
                                lambda: self.log_input(" ".join(f2()), agent_id).split(" "))()


    # send locations of amplifiers to the agents
    def send_amplifiers(self):
        amplifiers = self.map.get_amplifiers()
        self.amplifiers = amplifiers
        self.send_to_all(f"AMPLIFIERS {len(amplifiers)}")
        for a in amplifiers:
            self.send_to_all(f"{a[0]} {a[1]}")

    def start(self):
        spawn_points = self.map.get_spawn_points(self.n_agents)
        self.state = []
        # randomly place the bots on the map
        for i in range(self.n_agents):
            (x,y) = spawn_points[i]
            self.agents[i].send_message(f"START")
            self.agents[i].send_message(f"SIZE {self.map.size}")
            self.agents[i].send_message(f"{x} {y}")
            self.state.append(State((x,y)))
        self.send_amplifiers()
        for i in range(self.n_agents):
            self.lay(i)

    def update_agents(self):
        coords = self.map.search(r"^-")
        for x,y in coords:
            cell = self.map.cell(x,y)
            self.map.mark_seen(x,y)
            for i in range(self.n_agents):
                if i == int(cell.split(".")[2]):
                    continue
                self.agents[i].send_message(f"UPDATE TILE {x} { y}")
    def play(self):
        self.start()
        turn = 0
        while turn < self.M:
            k = self.map.get_k(turn)
            if turn > 0 and turn %k == 0:
                self.update_agents()

            i = turn % self.n_agents 
            agent = self.agents[i]
            invalid_move = self.invalid_move(i)
            action = agent.get_action()
            if(len(action) == 0):
                raise invalid_move
            if dev and action[0] == "SHOW":
                self.map.show()
                turn -= 1
            elif action[0] == "INFO":
                x,y = self.state[i].position
                cell = self.map.is_occupied_by_enemy(x,y,i)
                if not cell:
                    raise invalid_move
                
                self.state[i].points -= 4
                # TODO: send some info
                # for now index will suffice
                agent.send_message(f"HINT {cell[1]}")

            elif action[0] == "DESTROY":
                x,y = self.state[i].position
                cell = self.map.is_occupied_by_enemy(x,y,i)
                if not cell:
                    raise invalid_move
                if cell[1] != 1:
                    agent.send_message("FAILED")
                    self.state[i].points -= 8
                else:
                    if self.state[cell[2]].current_chain_index == cell[0]:
                        self.terminate(cell[2])
                    coords = self.map.destroy_chain(cell[0],cell[2])
                    length = len(coords)
                    self.state[i].points += 3*length
                    agent.send_message(f"DESTROYED {length}")
                    for (x,y) in coords:
                        agent.send_message(f"{x} {y}")
                    self.agents[cell[2]].send_message(f"UPDATE DESTROYED {x} {y}")
                    if len(self.map.search(fr"[1-9]+\.[1-9]+\.{cell[2]}$")) == 0:
                        break
            else:
                ind = -1
                while len(action) > 0:
                    a = action.pop(0)
                    remaining = order[ind+1:]
                    if a in remaining:
                        if a == "TERMINATE":
                            if not self.terminate(i):
                                raise invalid_move
                        elif a == "TELEPORT":
                            if len(action) == 0:
                                raise invalid_move
                            tile_index: str = action.pop(0)
                            if not tile_index.isdigit():
                                raise invalid_move
                            self.teleport(i,int(tile_index))
                        elif a == "MOVE":
                            if len(action) == 0:
                                raise invalid_move
                            direction : str = action.pop(0)
                            self.move(i,direction)
                            x,y = self.state[i].position
                            if self.map.is_empty_at(x,y):
                                agent.send_message("EMPTY")
                            elif self.map.is_occupied_by_enemy(x,y,i):
                                
                                agent.send_message("TILE")
                                if self.terminate(i):
                                    agent.send_message("TERMINATED")
                                if not self.map.is_seen(x,y):
                                    self.map.mark_seen(x,y)
                                    break
                            
                        elif a == "LAY":
                            self.lay(i)
                        else:
                            raise invalid_move
                        ind = remaining.index(a)
                    else:
                        raise invalid_move
            agent.send_message("TURNOVER")
            turn += 1       
        self.send_to_all("GAMEOVER")
        points_arr : list[tuple[int,int]] = []
        for i in range(self.n_agents):
            points_arr.append((self.calculate_total_points(i),i))
        points_arr.sort(key=lambda p: p[0])
        return self.agents[points_arr[-1][1]]
    def lay(self,i:int):
        agent = self.agents[i]
        x,y = self.state[i].position
        cell = self.map.cell(x,y)
        if self.map.is_empty_at(x,y):

            chain = self.state[i].current_chain_index
            # guaranteed greater than 1 if chain is active
            next = self.state[i].next_tile_index
            new_chain = not self.state[i].chain_active or not (Map.is_adjacent(self.state[i].position, self.map.search(Map.get_search_rep((chain,next-1,i)))[0] ))
            if new_chain:
                self.terminate(i)
            info = (-self.state[i].current_chain_index, self.state[i].next_tile_index, i)
            self.map.place_tile((x,y), info)
            self.state[i].next_tile_index += 1
            self.state[i].chain_active = True
            if cell == "T":
                self.terminate(i)
                agent.send_message("TERMINATED")
        elif self.map.is_occupied_by_enemy(x,y,i) and cell.startswith("-"):
            self.map.mark_seen(x,y)
            agent.send_message("TILE")
        else:
            raise self.invalid_move(i)
    
    def teleport(self,i : int, index : int):
        x,y = self.state[i].position
        cell = self.map.is_occupied_by_self(x,y,i)
        invalid_move = self.invalid_move(i)
        if not cell:
            raise invalid_move
        chain,_,agent = cell
        if chain in self.state[i].teleported_chains:
            raise invalid_move
        search = self.map.search(Map.get_search_rep((chain,index,agent)))
        if len(search) == 0:
            raise invalid_move
        self.state[i].position = search[0]
        self.state[i].teleported_chains.append(chain)

    def terminate(self,i : int):
        if self.state[i].chain_active:
            self.state[i].current_chain_index += 1
            self.state[i].next_tile_index = 1
            self.state[i].chain_active = False
            return True
        return False
    
    def move(self,i : int,direction : str):
        invalid_move = self.invalid_move(i)
        x,y = self.state[i].position
        if direction == "U":
            if x == 1:
                raise invalid_move
            x -= 1
        elif direction == "D":
            if x == self.map.size:
                raise invalid_move
            x += 1
        elif direction == "L":
            if y == 1:
                raise invalid_move
            y -= 1
        elif direction == "R":
            if y == self.map.size:
                raise invalid_move
            y += 1
        else:
            raise invalid_move

        self.state[i].position = (x,y)

    def calculate_total_points(self,i : int):
        total = self.state[i].points
        my_tiles = self.map.search(fr"[1-9]+\.[1-9]+\.{i}$")
        total += 2*len(my_tiles)
        chains = dict()
        for r, c in my_tiles:
            val = str(self.map.cell(r,c))
            chain_id, tile_id, _ = map(abs,map(int, val.split('.')))
            chains.setdefault(chain_id, []).append((r, c, tile_id))

        for tiles in chains.values():
            # Find the tail (tile_id == 1)
            tail_tile = next(((r, c) for r, c, t_id in tiles if t_id == 1), None)
            if tail_tile and tail_tile in self.amplifiers:
                total += len(tiles)
        
        return total
    def log_output(self, message : str, id : str):
        self.game_log.append(f"To Agent {id}: {message}")
        return message
    def log_input(self, message : str, id : str):
        self.game_log.append(f"From Agent {id}: {message}")
        return message
    def send_to_all(self, message : str):
        for agent in self.agents:
            agent.send_message(message)

    def invalid_move(self,i : int):
        return Exception(f"Invalid move by Agent {self.agents[i].id}")
    
    def save(self):
        log_path = f"logs/game_log_{self.id}.txt"
        Path("logs").mkdir(exist_ok=True)
        with open(log_path, "w") as f:
            json.dump(self.game_log, f, indent=2)
        return log_path