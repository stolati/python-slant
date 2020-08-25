import random

from slant import loop_check, board, solvers


class SlantGame(board.SlantBoard):

  def __init__(self, game_params, random_seed):
    w, h, self.d = game_params
    super().__init__(w, h)
    self._random_gen = random.Random(random_seed)
  
  def _fill_solution(self):
    # Fill the solution with random values
    # TODO : can be improved by using bytes from random integer
    choices = [board.SolutionEnum.SLASH, board.SolutionEnum.BACKSLASH]

    loop_checks = loop_check.LoopChecks()

    for sol_pos in self.loop_sol():
      try:
        self.get_sol(sol_pos)
      except IndexError:
        continue # Don't fill the one that are invalids

      val = self._random_gen.choice(choices)

      con_a, con_b = self._sol_connections(sol_pos, val)

      valid = loop_checks.add(con_a, con_b)
      if not valid:
        val = val.invert()
    
      con_a, con_b = self._sol_connections(sol_pos, val)
      valid = loop_checks.add(con_a, con_b)

      self.set_sol(sol_pos, val)
  
  def _fill_clues(self):
    # Fill the complete set of clues
    for clue_pos in self.loop_clues():
      num_links = len(self.clue_info(clue_pos).linked)
      self.set_clue(clue_pos, num_links)

  def generate_slant(self):
    self._fill_solution()
    self._fill_clues()

    assert self.is_solvable()

  def new_game(self):
    self.generate_slant()
    self.try_remove_elements()
    assert self.is_solvable()
  
  def try_remove_elements(self):
    all_clues = list(self.loop_clues())
    self._random_gen.shuffle(all_clues)
    for clue_pos in all_clues:
      clue_val = self.get_clue(clue_pos)
      if clue_val == board.EMPTY_CLUE:
        continue # Already removed
      
      self.set_clue(clue_pos, board.EMPTY_CLUE)

      if not self.is_solvable():
        self.set_clue(clue_pos, clue_val)


  def is_solvable(self):
    copy_board = self.copy(with_sol=False)

    solvers.all_solvers(copy_board)

    return copy_board.is_solved()




class SlantGameRandomHoles(SlantGame):

  def __init__(self, game_params, random_seed, num_holes):
    self._num_holes = num_holes
    super().__init__(game_params, random_seed)

  def _create_invalids(self):
    all_clue_pos = list(self.loop_sol())
    clue_sample = self._random_gen.sample(all_clue_pos, self._num_holes)

    for sol_pos in clue_sample:
      self.set_sol(sol_pos, board.SolutionEnum.INVALID)

  def generate_slant(self):
    self._create_invalids()

    self._fill_solution()
    self._fill_clues()

    assert self.is_solvable()


class SlantGameBigHole(SlantGame):

  def __init__(self, game_params, random_seed):
    super().__init__(game_params, random_seed)

  def _create_invalids(self):
    w, h = self.sol_size()
    for x in range(w // 2, w):
      for y in range(h // 2, h):
        pos = board.SolPos(x, y)
        self.set_sol(pos, board.SolutionEnum.INVALID)

  def generate_slant(self):
    self._create_invalids()

    self._fill_solution()
    self._fill_clues()

    assert self.is_solvable()