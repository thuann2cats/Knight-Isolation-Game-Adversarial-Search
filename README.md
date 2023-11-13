# Game Playing Agent for Knight Isolation

In this project, I experimented with adversarial search techniques such as minimax, alpha-beta pruning and iterative deepening to build an agent to play Knight Isolation - based on starting code and game-playing module from an assignment in Udacity's Artificial Intelligence course.

The provided agent in the starting code uses minimax search up to depth 3. The agent I wrote uses A/B pruning and iterative deepening and was able to beat the provided agent 75-80% of the time.

I've also modified the code so that matches can be viewed more easily, with "our player" appearing in green while the opponent showing in red - regardless of which player moves first. In the `tests` folder, please run:
```
python run_match.py
```

NOTE: In Knight Isolation, each player can move like a knight in chess. The graphic below was from the Udacity instruction [here](Udacity_instructions.md).

![viz.gif](viz.gif)