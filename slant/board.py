
from collections import namedtuple
from enum import Enum, IntEnum

from slant import loop_check

class DifficultyEnum(IntEnum):
    EASY = 1
    HARD = 2

class SolutionEnum(Enum):
  SLASH = '/'
  BACKSLASH = '\\'
  NONE = ' '
  INVALID = '#'

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

  def loop_forward(self):
    if self == SolutionEnum.SLASH:
      return SolutionEnum.BACKSLASH
    if self == SolutionEnum.BACKSLASH:
      return SolutionEnum.NONE
    if self == SolutionEnum.NONE:
      return SolutionEnum.SLASH
    assert False

  def loop_backward(self):
    if self == SolutionEnum.BACKSLASH:
      return SolutionEnum.SLASH
    if self == SolutionEnum.NONE:
      return SolutionEnum.BACKSLASH
    if self == SolutionEnum.SLASH:
      return SolutionEnum.NONE
    assert False


EMPTY_CLUE = '.'




GameParams = namedtuple('GameParams', ['w', 'h', 'd'])
# Separate both to avoid using one instead of the other
SolPos = namedtuple('SolPos', ['sol_x', 'sol_y'])
CluePos = namedtuple('CluePos', ['clue_x', 'clue_y'])

ClueSouroud = namedtuple('ClueSouroud', ['linked', 'unlinked', 'empty'])



class SlantBoard(object):

  def __init__(self, w, h):
    self._w, self._h = w, h
    self._W, self._H = self._w + 1, self._h + 1

    self._sol = [[SolutionEnum.NONE for _ in range(self._w)] for _ in range(self._h)]
    self._clues = [[EMPTY_CLUE for _ in range(self._W)] for _ in range(self._H)]

  def sol_size(self):
    return (self._w, self._h)

  def copy(self, with_sol=True):
    new_board = SlantBoard(self._w, self._h)
    new_board._sol = [l[:] for l in self._sol]
    if not with_sol:
      self.clear_sol()
    new_board._clues = [l[:] for l in self._clues]
    return new_board

  def clear_sol(self):
    for sol_pos in list(self.loop_sol()):
      self.set_sol(sol_pos, SolutionEnum.NONE)

  def get_sol(self, sol_pos):
    if sol_pos.sol_y < 0 or sol_pos.sol_x < 0:
      raise IndexError("no negative index")
    sol_val =self._sol[sol_pos.sol_y][sol_pos.sol_x]
    if sol_val == SolutionEnum.INVALID:
      raise IndexError("Outside border")
    return sol_val

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
        pos = SolPos(sol_x=x, sol_y=y)
        try:
          self.get_sol(pos)
        except IndexError:
          continue
        yield SolPos(sol_x=x, sol_y=y)
  
  def loop_clues(self):
    for y in range(self._H):
      for x in range(self._W):
        pos = CluePos(clue_x=x, clue_y=y)
        try:
          self.get_clue(pos)
        except IndexError:
          continue
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
    loop_checks = loop_check.LoopChecks()
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

