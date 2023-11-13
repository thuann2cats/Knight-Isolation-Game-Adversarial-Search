
from sample_players import DataPlayer


class CustomPlayer(DataPlayer):
    """ Implement your own agent to play knight's Isolation

    The get_action() method is the only required method for this project.
    You can modify the interface for get_action by adding named parameters
    with default values, but the function MUST remain compatible with the
    default interface.

    **********************************************************************
    NOTES:
    - The test cases will NOT be run on a machine with GPU access, nor be
      suitable for using any other machine learning techniques.

    - You can pass state forward to your agent on the next turn by assigning
      any pickleable object to the self.context attribute.
    **********************************************************************
    """
    def get_action(self, state):
        """ Employ an adversarial search technique to choose an action
        available in the current state calls self.queue.put(ACTION) at least

        This method must call self.queue.put(ACTION) at least once, and may
        call it as many times as you want; the caller will be responsible
        for cutting off the function after the search time limit has expired.

        See RandomPlayer and GreedyPlayer in sample_players for more examples.

        **********************************************************************
        NOTE: 
        - The caller is responsible for cutting off search, so calling
          get_action() from your own code will create an infinite loop!
          Refer to (and use!) the Isolation.play() function to run games.
        **********************************************************************
        """
        # TODO: Replace the example implementation below with your own search
        #       method by combining techniques from lecture
        #
        # EXAMPLE: choose a random move without any search--this function MUST
        #          call self.queue.put(ACTION) at least once before time expires
        #          (the timer is automatically managed for you)
        import random
        self.queue.put(random.choice(state.actions()))
        max_depth = 2
        best_move = None
        # best_score = -2**30

        # for this value of max_depth
        while True:
            # call minimax function for this depth limit
            best_move = self.minimax(state, max_depth)
            # put in the action queue
            self.queue.put(best_move)
            # print(best_move)
            # increment max_depth parameter and continue
            # print(f"Finished searching through depth {max_depth}")
            max_depth += 1

    def minimax(self, state, max_depth):
        best_val, best_move = self.get_max(state, float("-inf"), float("inf"), max_depth)
        return best_move

    def score_state(self, state, player_id):
        the_other_player = 1 - player_id
        num_my_moves = state.liberties(state.locs[player_id])
        num_opponent_moves = state.liberties(state.locs[the_other_player])
        return len(num_my_moves) - len(num_opponent_moves)

    def get_max(self, state, alpha, beta, remaining_depth):
        # if this is terminal state, then return the utility
        if state.terminal_test():
            util = state.utility(player_id=self.player_id)
            if util > 0:
                # our player wins
                import random
                return util, random.choice(state.actions())
            else:
                return util, None

        # if no more depth allowed, then compute the score and return
        if remaining_depth == 0:
            return self.score_state(state=state, player_id=self.player_id), None
        current_max_value = None
        current_max_move = None
        # loop through possible next actions
        for action in state.actions():
            next_state = state.result(action)
            min_value, _ = self.get_min(next_state, alpha, beta, remaining_depth - 1)
            # get the max move so far
            if current_max_value is None or min_value > current_max_value:
                current_max_value = min_value
                current_max_move = action
            # update alpha/beta
            if current_max_value > alpha:
                alpha = current_max_value
            # exit early if necessary (AB pruning)
            if current_max_value >= beta:
                return current_max_value, current_max_move
        return current_max_value, current_max_move

    def get_min(self, state, alpha, beta, remaining_depth):
        # the_other_player = 1 - self.player_id
        if state.terminal_test():
            return state.utility(player_id=self.player_id), None
        if remaining_depth == 0:
            return self.score_state(state=state, player_id=self.player_id), None
        current_min_value = None
        current_min_move = None
        # loop through possible next actions:
        for action in state.actions():
            next_state = state.result(action)
            max_value, _ = self.get_max(next_state, alpha, beta, remaining_depth - 1)
            if current_min_value is None or max_value < current_min_value:
                current_min_value = max_value
                current_min_move = action
            if current_min_value < beta:
                beta = current_min_value
            if current_min_value <= alpha:
                return current_min_value, current_min_move
        return current_min_value, current_min_move

