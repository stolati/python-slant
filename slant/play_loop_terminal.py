import curses

from slant import board, solvers

def _play_loop(game_param, stdscr):
  stdscr.clear()

  cur_pos_x, cur_pos_y = 0, 0
  state = game_param.copy(with_sol=False)
  w, h = state.sol_size()

  while True:

    cur_state_str = str(state) + '\n' + f'({cur_pos_x}, {cur_pos_y})   '
    stdscr.leaveok(False)
  
    stdscr.addstr(0, 0, cur_state_str) 
    stdscr.refresh()

    cur_pos_y = cur_pos_y % h
    cur_pos_x = cur_pos_x % w
    sol_pos = board.SolPos(sol_x=cur_pos_x, sol_y=cur_pos_y)

    win_pos_y = cur_pos_y * 2 + 1
    win_pos_x = cur_pos_x * 2 + 1
  
    stdscr.move(win_pos_y, win_pos_x)

    c = stdscr.getch()
    if c == ord('e'):
        break
    if c == ord('j') or c == curses.KEY_DOWN: # down
      cur_pos_y += 1
    if c == ord('k') or c == curses.KEY_UP: # up
      cur_pos_y -= 1
    if c == ord('h') or c == curses.KEY_LEFT: # left
      cur_pos_x -= 1
    if c == ord('l') or c == curses.KEY_RIGHT: # right
      cur_pos_x += 1
    if c == ord('s'):
      solvers.all_solvers(state)
    if c == ord(' '):
      existing_val = state.get_sol(sol_pos)
      new_val = existing_val.loop_forward()
      state.set_sol(sol_pos, new_val)
      if state.is_solved():
        break
    if c == curses.KEY_ENTER:
      existing_val = state.get_sol(sol_pos)
      new_val = existing_val.loop_backward()
      state.set_sol(sol_pos, new_val)
      if state.is_solved():
        break


def play_terminal(state):
  curses.wrapper(lambda stdscr : _play_loop(state, stdscr))

