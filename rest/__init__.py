import uuid
from flask import Flask, escape, request, jsonify, abort
import core

INSTANCES = {}

api_help = {
  "tetrinext": {
    "v1.0": [
      {
        "path": "/",
        "description": "REST-api description text",
        "arguments": None,
        "return": [
          "200 - Everything works as planned"
        ]
      },
      {
        "path": "/create",
        "description": "Create new TetriNext instance",
        "arguments": None,
        "return": [
          "200 - Everything works as planned - TetriNext instance id"
        ]
      },
      {

      }
    ]
  }
}

def create_app():
  app = Flask(__name__, instance_relative_config=True)
  #app.config.from_json()
  
  @app.route("/")
  def description():
    return api_help
  
  @app.route("/create_instance/<int:fields>/<int:field_height>/<int:field_width>")
  def create_instance(fields, field_height, field_width):
    instance_id = str(uuid.uuid4())

    try:
      INSTANCES[instance_id] = core.Core(fields, field_height, field_width)
    except ValueError as vee:
      return str(vee), 402

    return jsonify(instance_id)
  
  @app.route("/list_instances")
  def list_instance():
    return jsonify(list(map(lambda x: { 
      "id": x,
      "fields": INSTANCES[x].fields,
      "field_height": INSTANCES[x].field_height,
      "field_width": INSTANCES[x].field_width,
      "stat_count_moves": INSTANCES[x].stat_count_moves,
      "stat_count_tetrominos": INSTANCES[x].stat_count_tetrominos,
      "current_tetrominos": list(map(lambda t: t.type_string, INSTANCES[x].current_tetrominos)),
      "current_tetrominos_x": list(map(lambda t: t.x, INSTANCES[x].current_tetrominos)),
      "current_tetrominos_y": list(map(lambda t: t.y, INSTANCES[x].current_tetrominos)),
      "next_tetrominos": list(map(lambda t: t.type_string, INSTANCES[x].next_tetrominos))

     }, INSTANCES)))
  
  @app.route("/get_field/<uuid:instance_id>")
  def get_field(instance_id):
    return jsonify(INSTANCES[str(instance_id)].field.tolist())

  return app