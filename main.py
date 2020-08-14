
from collections import namedtuple
import random
from enum import Enum, IntEnum
from disjoint_set import DisjointSet


class DifficultyEnum(IntEnum):
    EASY = 1
    HARD = 2

class SolutionEnum(Enum):
  SLASH = '/'
  BACKSLASH = '\\'
  NONE = ' '

  def invert(self):
    if self == SolutionEnum.SLASH:
      return SolutionEnum.BACKSLASH
    if self == SolutionEnum.BACKSLASH:
      return SolutionEnum.SLASH
    if self == SolutionEnum.NONE:
      return SolutionEnum.NONE
    raise Exception("")
  
  def isNone(self):
    return self == SolutionEnum.NONE

EMPTY_CLUE = '.'




GameParams = namedtuple('GameParams', ['w', 'h', 'd'])
# Separate both to avoid using one instead of the other
SolPos = namedtuple('SolPos', ['sol_x', 'sol_y'])
CluePos = namedtuple('CluePos', ['clue_x', 'clue_y'])

ClueSouroud = namedtuple('ClueSouroud', ['linked', 'unlinked', 'empty'])


class LoopChecks:
  # TODO use DisjointSet instead

  def __init__(self):
    self._links = {}

  def __str__(self):
    return str({self._links})

  def create_loop(self, a, b):
    a_set = self._links.get(a)
    b_set = self._links.get(b)
    return a_set is b_set and a_set is not None

  def add(self, a, b):
    if self.create_loop(a, b):
      return False

    a_set = self._links.get(a)
    b_set = self._links.get(b)

    if a_set is None and b_set is None:
      ab_set = {a, b}
      self._links[a] = ab_set
      self._links[b] = ab_set
      return True

    if a_set is b_set:
      assert False

    if a_set is None:
      ab_set = self._links[b]
      ab_set.add(a)
      self._links[a] = ab_set
      return True

    if b_set is None:
      ab_set = self._links[a]
      ab_set.add(b)
      self._links[b] = ab_set
      return True

    # Worst case, need to add everything from a and b
    if b_set > a_set:
      b_set, a_set = a_set, b_set

    a_set.update(b_set)
    for e in b_set:
      self._links[e] = a_set
    return True

class SlantBoard(object):

  def __init__(self, w, h):
    self._w, self._h = w, h
    self._W, self._H = self._w + 1, self._h + 1

    self._sol = [[SolutionEnum.NONE for _ in range(self._w)] for _ in range(self._h)]
    self._clues = [[EMPTY_CLUE for _ in range(self._W)] for _ in range(self._H)]

  def no_sol_copy(self):
    new_board = SlantBoard(self._w, self._h)
    new_board._clues = self._clues
    return new_board

  def get_sol(self, sol_pos):
    if sol_pos.sol_y < 0 or sol_pos.sol_x < 0:
      raise IndexError("no negative index")
    return self._sol[sol_pos.sol_y][sol_pos.sol_x]

  def get_clue(self, clue_pos):
    if clue_pos.clue_y < 0 or clue_pos.clue_x < 0:
      raise IndexError("no negative index")
    return self._clues[clue_pos.clue_y][clue_pos.clue_x]

  def get_link_sol(self, clue_pos):
    return []

  
  def _sol_connections(self, sol_pos, sol=None):
    if sol == None:
      sol = self.get_sol(sol_pos)
    if sol == SolutionEnum.NONE:
      return ()
    if sol == SolutionEnum.SLASH:
      return (
        CluePos(clue_x=sol_pos.sol_x+1, clue_y=sol_pos.sol_y),
        CluePos(clue_x=sol_pos.sol_x, clue_y=sol_pos.sol_y+1),
      )
    if sol == SolutionEnum.BACKSLASH:
      return (
        CluePos(clue_x=sol_pos.sol_x, clue_y=sol_pos.sol_y),
        CluePos(clue_x=sol_pos.sol_x+1, clue_y=sol_pos.sol_y+1),
      )
    raise Exception("_connections")
  
  def clue_info(self, clue_pos):

    params = [ # delta x, delta y, connection value
      (0, 0, SolutionEnum.BACKSLASH), # bottom right
      (-1, 0, SolutionEnum.SLASH), # bottom left
      (0, -1, SolutionEnum.SLASH), # top right
      (-1, -1, SolutionEnum.BACKSLASH), # top left
    ]

    linked, unlinked, empty = [], [], []

    for delta_x, delta_y, connect_if in params:
      sol_pos = SolPos(sol_x=clue_pos.clue_x+delta_x, sol_y=clue_pos.clue_y+delta_y)

      try:
        sol_val = self.get_sol(sol_pos)
      except IndexError:
        continue # Outside the map

      if sol_val.isNone():
        empty.append((sol_pos, connect_if)) # Put the value of what would be connection
      elif sol_val == connect_if:
        linked.append((sol_pos, sol_val))
      elif sol_val == connect_if.invert():
        unlinked.append((sol_pos, sol_val))
      else:
        assert False

    return ClueSouroud(
      linked=linked,
      unlinked=unlinked,
      empty=empty,
    )

  def loop_sol(self):
    for y in range(self._h):
      for x in range(self._w):
        yield SolPos(sol_x=x, sol_y=y)
  
  def loop_clues(self):
    for y in range(self._H):
      for x in range(self._W):
        yield CluePos(clue_x=x, clue_y=y)

  def set_sol(self, sol_pos, val):
    self._sol[sol_pos.sol_y][sol_pos.sol_x] = val
  
  def set_clue(self, clue_pos, val):
    self._clues[clue_pos.clue_y][clue_pos.clue_x] = val

         
  def __str__(self):

    def _str_clue_line(clue_line):
      return ' '.join((' ' if c == EMPTY_CLUE else str(c)) for c in clue_line)
    
    def _str_sol_line(sol_line):
      return ' ' + ' '.join(s.value for s in sol_line)

    res = []
    for y in range(self._h):
      res.append(_str_clue_line(self._clues[y]))
      res.append(_str_sol_line(self._sol[y]))
    res.append(_str_clue_line(self._clues[-1]))

    return '\n'.join(res)

  def is_solved(self):
    # Loop checks, and that we filled everything
    loop_checks = LoopChecks()
    for sol_pos in self.loop_sol():
      sol_val = self.get_sol(sol_pos)
      if sol_val.isNone():
        return False

      con_a, con_b = self._sol_connections(sol_pos, sol_val)
      if loop_checks.create_loop(con_a, con_b):
        return False

      is_valid = loop_checks.add(con_a, con_b)
      assert is_valid

    # Clues checks
    for clue_pos in self.loop_clues():
      clue_info = self.clue_info(clue_pos)
      clue_val = self.get_clue(clue_pos)

      if clue_val == EMPTY_CLUE:
        continue
      
      if len(clue_info.empty) != 0:
        return False
      
      if len(clue_info.linked) != clue_val:
        return False
    
    return True




class SlantGame(SlantBoard):

  def __init__(self, game_params, random_seed):
    w, h, self.d = game_params
    super().__init__(w, h)
    self._random_gen = random.Random(random_seed)

  def generate_slant(self):
    choices = [SolutionEnum.SLASH, SolutionEnum.BACKSLASH]
    # Fill the solution with random values
    # TODO : can be improved by using bytes from random integer

    loop_checks = LoopChecks()

    for sol_pos in self.loop_sol():
      val = self._random_gen.choice(choices)

      con_a, con_b = self._sol_connections(sol_pos, val)

      valid = loop_checks.add(con_a, con_b)
      if not valid:
        val = val.invert()
    
      con_a, con_b = self._sol_connections(sol_pos, val)
      valid = loop_checks.add(con_a, con_b)

      self.set_sol(sol_pos, val)
    
    # Fill the complete set of clues
    for clue_pos in self.loop_clues():
      num_links = len(self.clue_info(clue_pos).linked)
      self.set_clue(clue_pos, num_links)

  def new_game(self):
    self.generate_slant()
    self.try_remove_elements()
    assert self.is_solvable()
  
  def try_remove_elements(self):
    all_clues = [clue_pos for clue_pos in self.loop_clues()]
    self._random_gen.shuffle(all_clues)
    for clue_pos in all_clues:
      clue_val = self.get_clue(clue_pos)
      if clue_val == EMPTY_CLUE:
        continue # Already removed
      
      self.set_clue(clue_pos, EMPTY_CLUE)

      if not self.is_solvable():
        self.set_clue(clue_pos, clue_val)


  def is_solvable(self):
    copy_board = self.no_sol_copy()

    board_solver_simple_count(copy_board)

    return copy_board.is_solved()


def board_solver_simple_count(board):
  had_change = True

  while had_change:
    had_change = False
  
    # For every elements, try to find if we can simply solve it
    for clue_pos in board.loop_clues():
      clue_info = board.clue_info(clue_pos)
      clue_val = board.get_clue(clue_pos)
  
      if clue_val == EMPTY_CLUE:
        continue
  
      # Already solved
      if len(clue_info.empty) == 0:
        continue
  
      free_spots = len(clue_info.empty)
      rest_linked = clue_val - len(clue_info.linked)
  
      # Case when we only have connection left
      if free_spots == rest_linked:
        for sol_pos, val in clue_info.empty:
          board.set_sol(sol_pos, val)
        had_change = True
  
      # Only unlink to have
      if rest_linked == 0:
        for sol_pos, val in clue_info.empty:
          board.set_sol(sol_pos, val.invert())
        had_change = True
  


def main():
  game_params = GameParams(20, 10, DifficultyEnum.EASY)

  sg = SlantGame(game_params, random_seed=42)
  sg.new_game()

  print(sg)

if __name__ == '__main__':
  main()


# Next steps :

# There is an easy mode and a hard mode.
# In easy mode, we don't care and parse everything the same
# In hard mode, we try to remove all the obvious starting points
# - 0, 4
# - on the border 2
# - on the corner 1
# but we can generalize with number of possible choice = number, or 0


# 

