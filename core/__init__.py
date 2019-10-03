import random
import numpy as np

# Tetrominos: I, J, L, O, S, T, Z
#
# 1 01 10 11 110 111 011
# 1 01 10 11 011 010 110
# 1 01 10
# 1 11 11
# 
I = np.array([[1,1,1,1]])
J = np.array([[0,2],[0,2],[0,2],[2,2]])
L = np.array([[3,0],[3,0],[3,0],[3,3]])
O = np.array([[4,4],[4,4]])
S = np.array([[5,5,0],[0,5,5]])
T = np.array([[6,6,6],[0,6,0]])
Z = np.array([[0,7,7],[7,7,0]])
type_strings = ["I", "J", "L", "O", "S", "T", "Z"]

class Tetromino:
  def __init__(self, type_string, x, y, rotations=0):
    self.type_string = type_string
    if type_string == "I":
      self.type = I
    elif type_string == "J":
      self.type = J
    elif type_string == "L":
      self.type = L
    elif type_string == "O":
      self.type = O
    elif type_string == "S":
      self.type = S
    elif type_string == "T":
      self.type = T
    elif type_string == "Z":
      self.type = Z
    else:
      raise ValueError(f"Unknown type string {type_string}")
    
    self.x = x
    self.y = y
    for idx in range(rotations):
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
    if cmd == 1:
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
    if cmd == 1:
      self.y += 1
    elif cmd == 2:
      self.x -= 1
    elif cmd == 3:
      self.x += 1
    elif cmd == 4:
      self.rotate()
    else:
      raise AttributeError(f"{cmd} is not supported")
  
  def rotate(self):
    self.type = np.rot90(self.type, k=-1)
  
  def set_in_middle(self, field_width):
    pos = np.where(self.type)
    x_size = np.max(pos[1])-np.min(pos[1])
    self.x = int(field_width/2+0.5)-int(x_size/2+0.5)

class Core:
  def __init__(self, fields, field_height, field_width):
    if fields < 1:
      raise ValueError(f"You need fields ({fields} > 0)")
    if field_height < 4:
      raise ValueError(f"field_height must be greater than 3 ({field_height} > 3)")
    if field_width < 4:
      raise ValueError(f"field_width must be greater than 3 ({field_width} > 3)")

    self.fields = fields
    self.field_height = field_height
    self.field_width = field_width
    self.step_queue = [[] for field in range(fields)]
    self.field = np.zeros((fields, field_height, field_width), dtype=np.int)

    self.stat_count_moves = 0
    self.stat_count_tetrominos = 0
    
    self.current_tetrominos = [self.tetromino_generator(self.field_width) for idx in range(self.fields)]
    self.next_tetrominos = [self.tetromino_generator(self.field_width) for idx in range(self.fields)]
  
  def tetromino_generator(self, width):
    type_strings = ["I","J","L","O","S","T","Z"]
    rotations = [0,1,2,3]
    tetromino = Tetromino(random.choice(type_strings), 0, 0, random.choice(rotations))
    tetromino.set_in_middle(width)
    
    return tetromino
  
  def __str__(self):
    tetrominos = np.zeros((self.fields, self.field_height, self.field_width), dtype=np.int)
    for (idx, tetromino) in enumerate(self.current_tetrominos):
      if not tetromino:
        continue

      # get tetromino boundaries
      left, right, top, bottom = tetromino.get_boundaries()
      tetrominos[idx, top:bottom, left:right] = tetromino.type

    return console_viz.out(self.field+tetrominos)
  
  def add_step(self, field_id, cmd, front=False):
    """ Adds a step into the step_queue """
    if len(self.step_queue) < field_id:
      raise LookupError()
    
    if not front:
      self.step_queue[field_id].append(cmd)
    else:
      self.step_queue[field_id].insert(0, cmd)
  
  def test(self, field_id, cmd):
    """ Test if a step in a certain direction will touch the field
    cmd: 0 (no move), 1 (down move), 2 (left move), 3 (right move), 4 (rotate)"""
    return self.current_tetrominos[field_id].test_move(cmd, self.field[field_id])
  
  def move_tetromino(self, field_id, cmd):
    """ Move a tetromino in a certain direction : 0 (no move), 1 (down move), 
    2 (left move), 3 (right move), 4 (rotate)"""
    if not self.current_tetrominos[field_id]:
      print("No tetromino")
      return

    if not self.test(field_id, cmd):
      if cmd == 1: # down move
        teromino = self.current_tetrominos[field_id]
        left, right, top, bottom = teromino.get_boundaries()
        self.field[field_id, top:bottom, left:right] += teromino.type
        self.current_tetrominos[field_id] = self.next_tetrominos[field_id]
        self.next_tetrominos[field_id] = self.tetromino_generator(self.field_width)
        return
      return
    self.current_tetrominos[field_id].move(cmd)
    
    self.stat_count_moves += 1
  
  def step(self):
    field_order = list(range(self.fields))
    random.shuffle(field_order)
    
    for field_id in field_order:
      if not self.step_queue[field_id]:
        continue
      
      while self.step_queue[field_id]:
        cmd = self.step_queue[field_id].pop(0)
        self.move_tetromino(field_id, cmd)

if __name__ == "__main__":
  import sys
  import console_viz
  np.set_printoptions(threshold=sys.maxsize)

  c = Core(4, field_width=int(12), field_height=int(22))
  c.step()
  print(c)
  
  cmd_array = []
  while True:
    if not len(cmd_array):
      cmd_array = list(input("(d)own / (l)eft / (r)ight / (t)rotate / (f)inalize / (q)uit"))
    if not cmd_array:
      continue
    cmd = cmd_array.pop(0)
    if cmd == "d": #down
      c.add_step(0, 1)
    elif cmd == "l": #left
      c.add_step(0, 2)
    elif cmd == "r": #right
      c.add_step(0, 3)
    elif cmd == "t": # rotate
      c.add_step(0, 4)
    elif cmd == "f": # finalize tetromino
      c.add_step(0,5)
    elif cmd == "e": # eval
      c.add_step(0,6)
    elif cmd == "q": # quit
      break

    c.step()
    print(c)