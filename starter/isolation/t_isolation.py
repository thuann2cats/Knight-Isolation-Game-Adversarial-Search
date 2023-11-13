from enum import IntEnum
from typing import NamedTuple

# board array dimensions and bitboard size
_WIDTH = 11
_HEIGHT = 9
_SIZE = (_WIDTH + 2) * _HEIGHT - 2

# Build the prototype bitboard, which is a bitstring
_BLANK_BOARD = 0
row = ((1 << _WIDTH) - 1)
for _ in range(_HEIGHT):
    _BLANK_BOARD = (_BLANK_BOARD << (_WIDTH + 2)) | row

# declare constants describing the bit-wise offsets for each cardinal direction
S, N, W, E = -_WIDTH - 2, _WIDTH + 2, 1, -1


class Action(IntEnum):
    """The eight L-shaped steps that a knight can move in chess"""
    NNE = N + N + E
    ENE = E + N + E
    ESE = E + S + E
    SSE = S + S + E
    SSW = S + S + W
    WSW = W + S + W
    WNW = W + N + W
    NNW = N + N + W


_ACTIONSET = set(Action)

nt = NamedTuple('Isolation', [('board', int),
                         ('ply_count', int),
                         ('locs', int)])


class Isolation(nt):
    """Bitboard implementation of knight's Isolation game state.

    Subclasssing NamedTuple makes the states (effectively) immutable and hashtable. Using immutable states can help avoid errors that can arise with in-place state updates. Hashable states allow the state to be used as the key to a look-up table.

    Attributes:
        board: int
        Bitboard representation of isolation game state. Bits that are ones represent open cells; bits thtat are zeros represent blocked cells

        ply_count: int
        Cumulative count of the number of actions applied to the board

        locs: tuple
        A pair of values defining the location of each player. Default for each player is None while the player has not yet placed their piece on the board; otherwise an integer.
        """
    def __new__(cls, board=_BLANK_BOARD, ply_count=0, locs=(None, None)):
        return super(Isolation, cls).__new__(cls, board, ply_count, locs)

    def actions(self):
        """
        Return a list of the legal actions in the current state.
        Note that players can choose any open cell on the opening move, but all later moves MUST be one of the values in Actions.
        :return:
        list
        A list containing the endpoints of all legal moves for the active player on the board
        """
        loc = self.locs[self.player()]
        if loc is None:
            return self.liberties(loc)
        return [a for a in Action if (a + loc) >= 0 and (self.board & (1 << (a + loc)))]

    def player(self):
        """
        Return the id (zero for the first player, one for the second player) of player currently holding initiative(i.e., the active player)
        """
        return self.ply_count % 2

    def result(self, action):
        """
        Return the resulting game state after applying the action specified to the current game state.
        Note that players can choose any open cell on the opening move, but all later moves MUST be one of the values in Actions.
        :param action: int - an index indicating the next position for the active player
        :return:
        Isolation
            A new state object with the input move applied.
        """
        player_location = self.locs[self.player()]
        assert player_location is None or action in _ACTIONSET, f"{action} is not a valid action from set {list(Action)}"
        if player_location is None:
            player_location = 0
        player_location = int(action) + player_location
        if not (self.board & (1 << player_location)):
            raise RuntimeError("Invalid move: target cell blocked")
        # update the board to block the ending cell from the new move
        board = self.board ^ (1 << player_location)
        locs = (self.locs[0], player_location) if self.player() else (player_location, self.locs[1])
        return Isolation(board=board, ply_count=self.ply_count + 1, locs=locs)


    def terminal_test(self):
        """
        Return True if either player has no legal moves, otherwise False
        :return:
        bool
            True if either player has no legal moves, otherwise False
        """
        return not (self._has_liberties(0) and self._has_liberties(1))

    def utility(self, player_id):
        """
        Returns the utility of the current game state from the perspective of the specified player
                    / +infinity, "player_id" wins
        utility =  | -infinity, "player_id" loses
                    \       0,  otherwise
        :param player_id: int - the 0-indexed id number of the player whose perspective is used for the utility calculation.
        :return: float - the utility value of the current game state for the specified player. The game has a utility of +inf if the player has won, a value of -inf if the player has lost, and a value of 0 otherwise.
        """
        if not self.terminal_test():
            return 0
        player_id_is_active = (player_id == self.player())
        active_has_liberties = self._has_liberties(self.player())
        player_id_wins = (active_has_liberties == player_id_is_active)
        return float("inf") if player_id_wins else float("-inf")

    def liberties(self, loc):
        """
        Return a list of "liberties" - open cells in the neighborhood of 'loc'

        :param loc: int - A position on the current board to use as the anchor point for available liberties (i.e., open cells neighboring the anchor point)
        :return: list - a list containing the position of open liberties in the neighborhood of the starting position.
        """
        cells = range(_SIZE) if loc is None else (loc + a for a in Action)
        return [c for c in cells if c >= 0 and self.board & (1 << c)]

    def _has_liberties(self, player_id):
        """
        Return True if the player has any legal moves in the given state.
        """
        return any(self.liberties(self.locs[player_id]))


class DebugState(Isolation):
    """
    Extend the Isolation game state class with utility methods for debugging & visualizing the fields in the data structure
    Examples
    --------
    >>> board = Isolation()
    >>> debug_board = DebugState.from_state(board)
    >>> print(debug_board.bitboard_string)
    1111111111100111111111110011111111111001111111111100111111111110011111111111001111111111100111111111110011111111111
    >>> print(debug_board)
    + - + - + - + - + - + - + - + - + - + - + - +
    |   |   |   |   |   |   |   |   |   |   |   |
    + - + - + - + - + - + - + - + - + - + - + - +
    |   |   |   |   |   |   |   |   |   |   |   |
    + - + - + - + - + - + - + - + - + - + - + - +
    |   |   |   |   |   |   |   |   |   |   |   |
    + - + - + - + - + - + - + - + - + - + - + - +
    |   |   |   |   |   |   |   |   |   |   |   |
    + - + - + - + - + - + - + - + - + - + - + - +
    |   |   |   |   |   |   |   |   |   |   |   |
    + - + - + - + - + - + - + - + - + - + - + - +
    |   |   |   |   |   |   |   |   |   |   |   |
    + - + - + - + - + - + - + - + - + - + - + - +
    |   |   |   |   |   |   |   |   |   |   |   |
    + - + - + - + - + - + - + - + - + - + - + - +
    |   |   |   |   |   |   |   |   |   |   |   |
    + - + - + - + - + - + - + - + - + - + - + - +
    |   |   |   |   |   |   |   |   |   |   |   |
    + - + - + - + - + - + - + - + - + - + - + - +

    """
    player_symbols = ['1', '2']

    @staticmethod
    def from_state(gamestate):
        return DebugState(gamestate.board, gamestate.ply_count, gamestate.locs)

    @property
    def bitboard_string(self):
        return f"{self.board:b}"

    @classmethod
    def ind2xy(cls, ind):
        """
        Convert from board index value to xy coordinates

        The coordinate frame is 0 in the bottom right corder, with x increasing along the columns progressing towards the left, and y increasing along the rows progressing towards the top
        :param ind:
        :return: a tuple
        """
        return ind % (_WIDTH + 2), ind // (_WIDTH + 2)

    def __str__(self):
        """
        Generates a string representation of the current game state, marking the location of each player and indicating which cells have been blocked, and which remain open
        :return: str - the string representation
        """
        import os
        from io import StringIO
        OPEN = " "
        CLOSED = "X"
        cell = "| {} "
        rowsep = "+ - " * _WIDTH + "+"
        out = StringIO()
        out.write(rowsep + os.linesep)

        board = self.board << 2
        for loc in range(_SIZE + 2):
            if loc > 2 and loc % (_WIDTH + 2) == 0:
                out.write("|" + os.linesep + rowsep + os.linesep)
            if loc % (_WIDTH + 2) == 0 or loc % (_WIDTH + 2) == 1:
                continue
            sym = OPEN if (board & (1 << loc)) else CLOSED
            if loc - 2 == self.locs[0]:
                sym = self.player_symbols[0]
            if loc - 2 == self.locs[1]:
                sym = self.player_symbols[1]
            out.write(cell.format(sym))
        out.write("|" + os.linesep + rowsep + os.linesep)
        return '\n'.join(l[::-1] for l in out.getvalue().split('\n')[::-1]) + os.linesep


# test code
# initial_state = Isolation()
# state = initial_state.result(57).result(0)
# print(DebugState.from_state(state).bitboard_string)
# print(DebugState.ind2xy(57))
# print(state.actions()[0])
# print(DebugState.ind2xy(state.actions()[0]))
#
# dbstate = DebugState.from_state(state)
# str_rep = str(dbstate)
# print(str_rep)
# print(state)
# print(state.ply_count)
# print(state.locs)
# print(state.actions())
# print(state.player())
# initial_state = Isolation()
# print(initial_state.terminal_test())
# print(initial_state.utility(initial_state.player()))
# while not state.terminal_test():
#     state = state.result(state.actions()[0])
# print(DebugState.from_state(state))
# print(state.terminal_test())
# print(state.utility(initial_state.player()))
# print(state.utility(1))
