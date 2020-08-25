
import curses

from slant import board, solvers, game, play_loop_terminal

def main():
  game_params = board.GameParams(10, 5, board.DifficultyEnum.EASY)

  #sg = SlantGame(game_params, random_seed=42)
  #sg.new_game()
  #print(sg)

  #sg = SlantGameRandomHoles(game_params, random_seed=42, num_holes=20)
  #sg.new_game()
  #print(sg)

  sg = game.SlantGameBigHole(game_params, random_seed=42)
  sg.new_game()

  play_loop_terminal.play_terminal(sg)

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

