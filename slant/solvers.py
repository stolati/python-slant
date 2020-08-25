
from slant import board


def all_solvers(game):
  _board_solver_simple_count(game)



def _board_solver_simple_count(game):
  had_change = True

  while had_change:
    had_change = False
  
    # For every elements, try to find if we can simply solve it
    for clue_pos in game.loop_clues():
      clue_info = game.clue_info(clue_pos)
      clue_val = game.get_clue(clue_pos)
  
      if clue_val == board.EMPTY_CLUE:
        continue
  
      # Already solved
      if len(clue_info.empty) == 0:
        continue
  
      free_spots = len(clue_info.empty)
      rest_linked = clue_val - len(clue_info.linked)
  
      # Case when we only have connection left
      if free_spots == rest_linked:
        for sol_pos, val in clue_info.empty:
          game.set_sol(sol_pos, val)
        had_change = True
  
      # Only unlink to have
      if rest_linked == 0:
        for sol_pos, val in clue_info.empty:
          game.set_sol(sol_pos, val.invert())
        had_change = True
