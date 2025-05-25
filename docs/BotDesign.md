# How does the engine interact with the bots

## Supported languages for bots (BONUS TASK)
- Python - should end with `.py` - built on `python3`
- C++ - should end with `.cpp` - built for C++17
- Java - should end with `.java`
- Javascript - should end with `.js`
- C - should end with `.c`


## Notation
-  A cell is represented by its coordinates `r c` where r is the row and c is the column of the cell. 
   - Indexing is 1 based
## START
- The engine sends the message `n` where `nxn` is the size of the map grid
- Then coordinates `r c` of the starting position of the bot
-  Then the engine sends the message `AMPLIFIERS L`, where L is the number of chain amplifier tiles
   -  The next L lines include `r c`
   -  These L lines are the coordinates of the L cells which have chain amplifier tiles on them
  
## PLAY
- Whenever it is the bots turn to play, the engine sends a message `TURN` and waits for the bot to reply with its move
- The bot replies with its move (a timeout of 2 seconds is implemented)
  - Possible moves are explained in GameDesign.md
  - If the move is invalid, the engine raises an error and quits the game
    - Moves are invalid if the following occurs
      - The bot tries terminate without having an active chain
      - The bot tries to teleport without standing on its own tile or if the bot has already used the chain he is standing on to teleport
      - The bot tries to move outside of the map
      - The bot tries to lay a tile on a cell which the bot is already let known has a tile 
      - The bot uses `INFO` on a cell which does not have the opponent's tile
      - The bot uses `DESTROY` on a cell which does not have the opponent's tile
  - After a `MOVE DIRECTION` command from the bot,the engine replies, with either
    - `EMPTY` if the new cell is empty
    - `TILE` if there is a tile placed by the enemy on that cell
      - In this case, if the bot has also added a `LAY` command after the above corresponding `MOVE` command, and the bot isn't already let known that the cell holds a tile, the `LAY` command is ignored
  - If while the bot has an active chain and it either, lands on an opponent's tile or tries to lay a tile on a chain terminating tile, it receives a `TERMINATED` message
  - On a valid `INFO` command, the engine replies with `HINT i`, i being the index of the tile in its chain
  - On a `DESTROY` command, the engine replies with
    - `FAILED` if the command is not used on the tail
    - `DESTROYED L` on success where L is the length of the chain destroyed, followed by L lines of coordinates of all the cells included in the chain
    - The bot whose chain has been destroyed is sent an update `UPDATE DESTROYED r c` where (r,c) are the coordinates of the tail of the chain which has just been destroyed
  - After every turn the engine sends `TURNOVER` to the bot which just played
- After every k turns, the engine sends `UPDATE TILE r c` to every bot for every coordinates of cells which have tiles that each bot doesn't know about

## END
- On game completion, the engine sends a `GAMEOVER` message to both bots and automatically kills the processes of both the bots