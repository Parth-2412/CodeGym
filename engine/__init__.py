from .map import Map
from .agent import Agent
from .logger import info, error
from .parser import get_args
from .game import Game
from .env import dev


def main():
    args = get_args()
    
    agent1 : Agent = None
    agent2 : Agent = None
    game : Game = None
    try:
        info("Starting game engine...")
        game_map = Map(args["map"])
        game_map.load()
        info("Map loaded.")
        
        agent1 = Agent(1, args["agent1"],)
        agent1.launch()
        info(f"Agent {agent1.id} launched.")

        agent2 = Agent(2, args["agent2"])
        agent2.launch()
        info(f"Agent {agent2.id} launched.")

        
        game = Game(args["game_id"], [agent1,agent2], game_map)

        winner = game.play()    
        info(f"Winner is Agent {winner.id}")
    except Exception as e:
        if dev:
            print(e)
            print(f"AGENT 1: {game.state[0].position[0]} {game.state[0].position[1]}")
            print(f"AGENT 2: {game.state[1].position[0]} {game.state[1].position[1]}")
            game.map.show()
            print(agent1.stderror())
            print(agent2.stderror())
        else:
            error(str(e))
        
    finally:
        if agent1 and agent1.return_code() is None:
            agent1.kill()
        if agent2 and agent2.return_code() is None:
            agent2.kill()
        info(f"Game log saved to {game.save()}")




main()