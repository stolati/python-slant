
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


GameParams = namedtuple('GameParams', ['w', 'h', 'd'])

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


  def generate_slant(self):
    choices = [SolutionEnum.SLASH, SolutionEnum.BACKSLASH]
    # Fill the solution with random values
    # TODO : can be improved by using bytes from random integer

    for y in range(self._h):
      for x in range(self._w):
        val = self._random_gen.choice(choices)

        self._sol[y][x] = val
         



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
      print(y)
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


