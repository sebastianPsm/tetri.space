import os

def out(field, states):
  res = ""
  fields = field.shape[0]
  width = field.shape[2]
  height = field.shape[1]
  
  for y in range(height):
    for field_id in range(fields):
      res += "#"
      for x in range(width):
        field_entry = field[field_id,y,x]
        if field_entry == 0:
          res += " "
        else:
          res += "x"
      res += "# "
    res += os.linesep

  for field_id in range(fields):
    res += "#"
    for x in range(width):
      res += "#"
    res += "# "
  res += os.linesep
  
  res += " "
  for field_id in range(fields):
    res += f'{states[field_id]}'.center(width, ' ') + "   "

  return res