import sys
import uuid
import random
import enum
import numpy as np

# Tetrominos: I, J, L, O, S, T, Z
#
# 1   1 1  11 11  111  11
# 1   1 1  11  11  1  11 
# 1  11 11 
# 1
# 
I = np.array([[1,1,1,1]])
J = np.array([[0,2],[0,2],[2,2]])
L = np.array([[3,0],[3,0],[3,3]])
O = np.array([[4,4],[4,4]])
S = np.array([[5,5,0],[0,5,5]])
T = np.array([[6,6,6],[0,6,0]])
Z = np.array([[0,7,7],[7,7,0]])
type_strings = {"I":I, "J":J, "L":L, "O":O, "S":S, "T":T, "Z":Z}

class Tetromino:
  def __init__(self, type_string, x, y, rotations=0):
    self.type_string = type_string
    self.type = type_strings[self.type_string]
    
    self.x = x
    self.y = y
    for _ in range(rotations):
      self.rotate()
  
  def get_boundaries(self):
    left = self.x
    right = left + self.type.shape[1]
    top = self.y
    bottom = top + self.type.shape[0]
    return left, right, top, bottom
  
  def test_move(self, cmd, field):
    field_height = field.shape[0]
    field_width = field.shape[1]

    x = self.x
    y = self.y

    _type = self.type
    if cmd == 0:
      pass
    elif cmd == 1 or cmd == 5:
      y += 1
      if y + _type.shape[0] > field_height:
        return False
    elif cmd == 2:
      x -= 1
      if x < 0:
        return False
    elif cmd == 3:
      x += 1
      if x + _type.shape[1] > field_width:
        return False
    elif cmd == 4:
      _type = np.rot90(_type)
      if x + _type.shape[1] > field_width:
        return False
      if y + _type.shape[0] > field_height:
        return False
    else:
      raise AttributeError(f"{cmd} is not supported")

    c = np.zeros((field_height, field_width), dtype=np.int)

    left = x
    right = left + _type.shape[1]
    top = y
    bottom = top + _type.shape[0]

    c[top:bottom, left:right] = _type

    # find intersections with existing field
    return not np.any(np.logical_and(field, c))
  
  def move(self, cmd):
    if cmd == 1 or cmd == 5: # down
      self.y += 1
    elif cmd == 2: # left
      self.x -= 1
    elif cmd == 3: # right
      self.x += 1
    elif cmd == 4: # rotate
      self.rotate()
    else:
      raise AttributeError(f"{cmd} is not supported")
  
  def rotate(self):
    self.type = np.rot90(self.type, k=-1)
  
  def finalize(self):
    pass
  
  def set_in_middle(self, field_width):
    pos = np.where(self.type)
    x_size = np.max(pos[1])-np.min(pos[1])
    self.x = int(field_width/2+0.5)-int(x_size/2+0.5)

class FieldState(enum.IntEnum):
  NotReady = 1 # Field isn't ready yet
  Ready = 2 # Field is ready
  Steady = 3 # Field is in short waiting state
  Go = 4 # field is running
  Lost = 5 # field has lost

class Core:
  def __init__(self, fields, field_height, field_width, steady_time_ms=2000, step_time_ms=600):
    if fields < 1:
      raise ValueError(f"You need fields ({fields} > 0)")
    if field_height < 4:
      raise ValueError(f"field_height must be greater than 3 ({field_height} > 3)")
    if field_width < 4:
      raise ValueError(f"field_width must be greater than 3 ({field_width} > 3)")

    self.fields = fields
    self.field_height = field_height
    self.field_width = field_width
    self.step_queue = [[] for idx in range(fields)]
    self.states = [FieldState.NotReady] * fields
    self.states_not_ready_cnt = fields
    self.field = np.zeros((fields, field_height, field_width), dtype=np.int)
    self.field_keys = { str(uuid.uuid4()):field for field in range(fields) }
    self.steady_time_ms = steady_time_ms
    self.steady_since_s = 0
    self.step_time_ms = step_time_ms
    self.last_step_time_s = [0] * fields

    # statistic values
    self.stat_count_moves = 0
    self.stat_count_tetrominos = 0
    self.stat_count_steps = 0
    self.stat_removed_lines = [0] * fields
    
    self.current_tetrominos = [self.tetromino_generator_(self.field_width) for idx in range(self.fields)]
    self.next_tetrominos = [self.tetromino_generator_(self.field_width) for idx in range(self.fields)]
  
  def delete(self):
    pass
  
  def tetromino_generator_(self, width):
    rotations = [0,1,2,3]
    tetromino = Tetromino(random.choice(list(type_strings.keys())), 0, 0, random.choice(rotations))
    tetromino.set_in_middle(width)
    
    return tetromino
  
  def get_field(self, key):
    field_id = self.get_fieldid_from_key_(key)

    tetrominos = np.zeros((self.field_height, self.field_width), dtype=np.int)

    current_tetromino = self.current_tetrominos[field_id]
    # get tetromino boundaries
    left, right, top, bottom = current_tetromino.get_boundaries()
    tetrominos[top:bottom, left:right] = current_tetromino.type
    
    return self.field[field_id]+tetrominos
  
  def get_fieldid_from_key_(self, key):
    if not key in self.field_keys:
      raise KeyError(f"No field found for key {key}")
    return self.field_keys[key]

  def ready(self, key):
    field_id = self.get_fieldid_from_key_(key)

    if not self.states[field_id] is FieldState.NotReady:
      return
    self.states[field_id] = FieldState.Ready

    # if all fields ready, then switch to steady state
    self.states_not_ready_cnt -= 1
    if self.states_not_ready_cnt == 0:
      self.states = [FieldState.Steady] * self.fields
  
  def add_step_(self, field_id, cmd, front=False):
    if not front:
      self.step_queue[field_id].append(cmd)
    else:
      self.step_queue[field_id].insert(0, cmd)

  def add_step(self, key, cmd, front=False):
    """ Adds a step into the step_queue """
    field_id = self.get_fieldid_from_key_(key)
    self.add_step_(field_id, cmd, front)

  def test_(self, field_id, cmd):
    """ Test if a step in a certain direction will touch the field
    cmd: 0 (no move), 1 (down move), 2 (left move), 3 (right move), 4 (rotate)"""
    return self.current_tetrominos[field_id].test_move(cmd, self.field[field_id])

  def move_tetromino_(self, field_id, cmd):
    """ Move a tetromino in a certain direction : 0 (no move), 1 (down move), 
    2 (left move), 3 (right move), 4 (rotate), 5 (finalize)"""
    if not self.current_tetrominos[field_id]:
      print("No tetromino")
      return

    if not self.test_(field_id, cmd):
      if cmd == 1 or cmd == 5: # down move
        teromino = self.current_tetrominos[field_id]
        left, right, top, bottom = teromino.get_boundaries()
        self.field[field_id, top:bottom, left:right] += teromino.type
        self.current_tetrominos[field_id] = self.next_tetrominos[field_id]
        self.next_tetrominos[field_id] = self.tetromino_generator_(self.field_width)
        
        # check if game is lost
        if not self.test_(field_id, 0):
          self.states[field_id] = FieldState.Lost
        return
      return

    self.current_tetrominos[field_id].move(cmd)
    self.stat_count_moves += 1

  def step(self, now_s):
    self.stat_count_steps += 1
    
    # set steady since time
    if self.states[0] == FieldState.Steady and self.steady_since_s == 0:
      self.steady_since_s = now_s
    
    # steady to go transition
    if self.states[0] == FieldState.Steady and self.steady_since_s != 0 and now_s - self.steady_since_s > self.steady_time_ms / 1000:
      self.states = [FieldState.Go] * self.fields

    field_order = list(range(self.fields))
    random.shuffle(field_order)

    # process fields randomly
    for field_id in field_order:
      # if field is not in 'go'-state, then continue
      if not self.states[field_id] is FieldState.Go:
        continue

      time_is_up = now_s - self.last_step_time_s[field_id] > self.steady_time_ms / 1000
      if time_is_up and self.states[field_id] is FieldState.Go:
        self.add_step_(field_id, 1, front=True)
        self.last_step_time_s[field_id] = now_s

      # if there's no step queued, then continue
      if not self.step_queue[field_id]:
        continue

      # process stepps from queue
      while self.step_queue[field_id]:
        cmd = self.step_queue[field_id].pop(0)

        if cmd == 5: # finalize
          while True:
            old = self.stat_count_moves
            self.move_tetromino_(field_id, cmd)
            if old == self.stat_count_moves:
              break
        else:
          self.move_tetromino_(field_id, cmd)
        
    # remove completed lines
    (completed_lines_field, completed_lines_pos) = np.nonzero((self.field != 0).all(axis=2))
    for cl_field, cl_pos in zip(completed_lines_field, completed_lines_pos):
      self.stat_removed_lines[cl_field] += 1
      self.field[cl_field, 0:cl_pos, :]

      self.field[cl_field,:cl_pos+1,:] = np.vstack((np.zeros(self.field_width), self.field[cl_field,:cl_pos,:]))

#if __name__ == "__main__":
#  import time
#  import threading
#  import console_viz
#
#  c = Core(16, field_width=int(12), field_height=int(22))
#  cv = console_viz.ConsoleViz(c)
#  cv.start()