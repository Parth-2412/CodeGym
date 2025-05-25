# Game design
- Explained in docs/GameDesign.md
# Instructions on how to make bots
- Explained in docs/BotDesign.md

# BONUS Tasks
- I have implemented support for multiple languages
- I have also included a map generator script
- For the case of multithreading, since each game has its own object, parallel processing can be easily implemented

# Design Decisions
- I have implemented a very scalable game as all elements of it are modelled as classes
- Each map could have its own spawning points and rules of visibility
- Each game could have its own number of turns after which it ends
- 
# How to run the engine
- You need a unix system
- And need the following languages/compilers installed in your system
  - Clang
  - Python3
  - Node.js
  - Java
  - GCC

# How the Game is logged
- A list of messages to and fro between the bots and the engine in order, from the engine's perspective is added as a json array to `logs/game_log_GAME_ID.txt`
# How to generate maps
- Run `python3 scripts/generate_map.py`
- And enter the size of the map, number of chain terminating and chain amplifier tiles and th script will generate a random map
# Usage
- In root directory, run `python3 -m engine --map MAP_PATH --agent1 AGENT1_PATH --agent2 AGENT2_PATH --id GAME_ID`
- To run an agent through your own terminal, use agent path as `terminal.terminal`
- Game Id is optional

# Bots
- I have implemented a naive bot which moves in any direction available to it
- It lays a tile if it lands on an empty cell
- It uses `INFO` it it lands on an enemy cell
- It uses `DESTROY` if it knows its on an enemy's tail
- You can find the bot in agents/naive.py