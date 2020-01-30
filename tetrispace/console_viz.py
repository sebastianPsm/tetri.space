import os
import time
import threading
import curses
import core

import grpc
import tetrispace_pb2
import tetrispace_pb2_grpc

class ConsoleViz:
  def __init__(self, core):
    self.core = core
    self.field_keys = [item[0] for item in sorted(self.core.field_keys.items(), key=lambda item: item[1])]
    self.screen = curses.initscr()
    self.fields = []

    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
    self.screen.keypad(True)

    self.num_rows, self.num_cols = self.screen.getmaxyx()
    if self.num_rows < self.core.field_height:
      raise OverflowError("Console window has not enough lines")
    if self.num_cols < self.core.field_width:
      raise OverflowError("Console window has not enough columns")

    # show input info text
    self.screen.addstr(0, 0, f"tetri.space test client", curses.A_STANDOUT)
    self.screen.addstr(self.num_rows-1, 0, f"Left/Right/Down/Rotate: ←/→/↓/↑       Finalize: [space]       Set ready: s       Quit: [q]", curses.A_STANDOUT)

    self.screen.refresh()

    # make main fields
    for idx in range(self.core.fields):
      h, l = self.core.field_height, self.core.field_width
      x, y = 1 + (self.core.field_width+2) * idx, 2
      win = curses.newwin(h+2, l+2, y, x)
      win.erase()
      win.box(curses.ACS_VLINE, curses.ACS_HLINE)
      win.addstr(0, 1, f" Field: {idx} ")
      win.addstr(h+1, 1, f" {self.core.states[idx].name} ")
      win.refresh()
      
      self.fields.append(win)

    # background functions
    def thread_fcn():
      while True:
        start = time.time()
        self.core.step(time.time())
        end = time.time()

        time.sleep(30/1000)
        for field_idx in range(self.core.fields):
          self.update_field(field_idx)
        self.screen.addstr(1, 0, f" turnaround: {(end-start)*1000000} µs                ")
        self.screen.refresh()
    daemon = threading.Thread(target=thread_fcn, daemon=True)
    daemon.start()
  
  def exit(self):
    curses.nocbreak()
    self.screen.keypad(False)
    curses.echo()
    curses.endwin()
  
  def update_field(self, field_idx):
    self.fields[field_idx].erase()
    self.fields[field_idx].box(curses.ACS_VLINE, curses.ACS_HLINE)

    fields = self.core.field.shape[0]
    width = self.core.field.shape[2]
    height = self.core.field.shape[1]
  
    field = self.core.get_field(self.field_keys[field_idx])
    for y in range(height):
        for x in range(width):
          field_entry = field[y, x]
          if not field_entry == 0:
            self.fields[field_idx].addstr(y+1, x+1, "█", curses.color_pair(field_entry))
    
    self.fields[field_idx].addstr(0, 2, f" Field: {field_idx} ")
    self.fields[field_idx].addstr(height+1, 2, f" {self.core.states[field_idx].name} ")
    self.fields[field_idx].refresh()

  def start(self):
    counter = 0
    c = self.screen.getch()
    while not c is ord('q'):
      counter += 1
      if c == curses.KEY_DOWN: # down
        self.core.add_step(self.field_keys[0], 1)
      elif c == curses.KEY_LEFT: # left
        self.core.add_step(self.field_keys[0], 2)
      elif c == curses.KEY_RIGHT: # right
        self.core.add_step(self.field_keys[0], 3)
      elif c == curses.KEY_UP: # rotate
        self.core.add_step(self.field_keys[0], 4)
      elif c is ord(' '): # finalize
        self.core.add_step(self.field_keys[0], 5)
      elif c is ord('s'): # set ready
        for key in self.field_keys:
          self.core.ready(key)

      c = self.screen.getch()

    self.exit()

if __name__ == "__main__":
  channel = grpc.insecure_channel("localhost:5000")
  stub = tetrispace_pb2_grpc.TetrispaceStub(channel)

  instanceAndFields = stub.CreateInstance(tetrispace_pb2.InstanceParameter(fields=6, height=24, width=12))
  print(instanceAndFields)

  instance_id = instanceAndFields.instance_id
  print(stub.GetInstance(instance_id))

  print(stub.ListInstances(tetrispace_pb2.ListInstancesParams()))

  print(stub.GetField(instance_id))
  stub.SetReady(instanceAndFields)
  