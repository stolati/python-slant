
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




GameParams = namedtuple('GameParams', ['w', 'h', 'd'])
# Separate both to avoid using one instead of the other
SolPos = namedtuple('SolPos', ['sol_x', 'sol_y'])
CluePos = namedtuple('CluePos', ['clue_x', 'clue_y'])


class LoopChecks:
  # TODO use DisjointSet instead

  def __init__(self):
    self._links = {}

  def __str__(self):
    return str({self._links})

  def add(self, a, b):
    a_set = self._links.get(a)
    b_set = self._links.get(b)

    if a_set is None and b_set is None:
      ab_set = {a, b}
      self._links[a] = ab_set
      self._links[b] = ab_set
      return True

    if a_set is b_set:
      return False # This is going to make a loop

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



class SlantGame:

  def __init__(self, game_params, random_gen):
    self._w, self._h, self.d = game_params
    self._W, self._H = self._w + 1, self._h + 1
    self._random_gen = random_gen

    self._sol = [[SolutionEnum.NONE for _ in range(self._w)] for _ in range(self._h)]
    self._clues = [[-1 for _ in range(self._W)] for _ in range(self._H)]

    #int w = params->w, h = params->h, W = w+1, H = h+1;
    #signed char *soln, *tmpsoln, *clues;
    #int *clueindices;
    #struct solver_scratch *sc;
    #int x, y, v, i, j;
    #char *desc;

    #soln = snewn(w*h, signed char);
    #tmpsoln = snewn(w*h, signed char);
    #clues = snewn(W*H, signed char);
    #clueindices = snewn(W*H, int);
    #sc = new_scratch(w, h);
  
  def new_game(self):
    self.generate_slant()

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
  
  def _clue_adjacent(self, clue_pos):

    def _calculate_sol(delta_x, delta_y, connect_if_is):

      sol_pos = SolPos(sol_x=clue_pos.clue_x+delta_x, sol_y=clue_pos.clue_y+delta_y)

      try:
        sol_val = self.get_sol(sol_pos)
        return {
          'val':sol_val,
          'pos':sol_pos,
          'connected': (connect_if_is is sol_val),
        }
      except IndexError:
        return None
    
    params = [ # delta x, delta y, connection value
      (0, 0, SolutionEnum.BACKSLASH), # bottom right
      (-1, 0, SolutionEnum.SLASH), # bottom left
      (0, -1, SolutionEnum.SLASH), # top right
      (-1, -1, SolutionEnum.BACKSLASH), # top left
    ]

    return list(filter(None, [
      _calculate_sol(*param) for param in params
    ]))

  
  def _col_adjacent_count_links(self, clue_pos):
    return len([x for x in self._clue_adjacent(clue_pos) if x['connected']])

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

  def generate_slant(self):
    choices = [SolutionEnum.SLASH, SolutionEnum.BACKSLASH]
    # Fill the solution with random values
    # TODO : can be improved by using bytes from random integer

    loop_checks = LoopChecks()

    for sol_pos in self.loop_sol():
      val = self._random_gen.choice(choices)

      connections = self._sol_connections(sol_pos, val)

      valid = loop_checks.add(*connections)
      if not valid:
        val = val.invert()
    
      connections = self._sol_connections(sol_pos, val)
      valid = loop_checks.add(*connections)

      self.set_sol(sol_pos, val)
    
    # Fill the complete set of clues
    for clue_pos in self.loop_clues():
      num_links = (self._col_adjacent_count_links(clue_pos))
      self.set_clue(clue_pos, num_links)
         
  def __str__(self):

    def _str_clue_line(clue_line):
      return ' '.join((' ' if c == -1 else str(c)) for c in clue_line)
    
    def _str_sol_line(sol_line):
      return ' ' + ' '.join(s.value for s in sol_line)

    res = []
    for y in range(self._h):
      res.append(_str_clue_line(self._clues[y]))
      res.append(_str_sol_line(self._sol[y]))
    res.append(_str_clue_line(self._clues[-1]))

    return '\n'.join(res)


  



def main():
  random_gen = random.Random(42)
  game_params = GameParams(20, 10, DifficultyEnum.EASY)

  sg = SlantGame(game_params, random_gen)
  sg.new_game()

  print(sg)


if __name__ == '__main__':
  main()


