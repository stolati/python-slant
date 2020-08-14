
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
    ab_set = a_set | b_set
    for e in ab_set:
      self._links[e] = ab_set
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
    return self._sol[sol_pos.sol_y][sol_pos.sol_x]

  def get_clue(self, clue_pos):
    return self._clues[clue_pos.clue_y][clue_pos.clue_x]

  def get_link_sol(self, clue_pos):
    return []

  
  def _connections(self, sol_pos, sol=None):
    if sol == None:
      sol = self._get_sol(sol_pos)
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

      connections = self._connections(sol_pos, val)

      valid = loop_checks.add(*connections)
      if not valid:
        val = val.invert()
    
      connections = self._connections(sol_pos, val)
      valid = loop_checks.add(*connections)

      self.set_sol(sol_pos, val)
    
    # Fill the complete set of clues
    for clue_pos in self.loop_clues():

      self.set_clue(clue_pos, 0)



         



  #fs = (dsf_canonify(connected, y*W+x) ==
  #      dsf_canonify(connected, (y+1)*W+(x+1)));
  #bs = (dsf_canonify(connected, (y+1)*W+x) ==
  #      dsf_canonify(connected, y*W+(x+1)));
  #
  #assert(!(fs && bs));
  #
  #v = fs ? +1 : bs ? -1 : 2 * random_upto(rs, 2) - 1;
  #fill_square(w, h, x, y, v, soln, connected, NULL);
  #   }
  #
  #   sfree(indices);
  #   sfree(connected);
  #
  #
  #   pass
  

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


