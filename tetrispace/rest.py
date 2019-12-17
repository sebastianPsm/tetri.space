import uuid
from flask import Flask, escape, request, jsonify, abort
from . import core

INSTANCES = {}

api_help = {
  "tetri.space": {
    "v1.0": [
      {
        "path": "/",
        "description": "REST-api description",
        "arguments": None,
        "return": [
          "200 - Everything works as planned"
        ]
      },
      {
        "path": "/v1.0/create_instance",
        "description": "Create new tetri.space instance",
        "arguments": ["Number of fields", "Field height", "Field width"],
        "return": [
          "200 - Everything works as planned - tetri.space instance id and so called field keys to control the fields"
        ]
      },
      {
        "path": "/v1.0/list_instances",
        "description": "List instances",
        "arguments": None,
        "return": [
          "200 - Everything works as planned - List of tetri.space instances"
        ]
      },
      {
        "path": "/v1.0/get_field",
        "description": "Return the whole teri.space field",
        "arguments": None,
        "return": [
          "200 - Everything works as planned - Matrix with shape: [#fields, height, width]"
        ]
      },
      {
        "path": "/v1.0/delete_instance",
        "description": "Delete a instance",
        "arguments": ["tetri.space instance id"],
        "return": [
          "200 - Everything works as planned"
        ]
      }
    ]
  }
}

def create_app():
  app = Flask(__name__, instance_relative_config=True)
  INSTANCES = {}
  #app.config.from_json()
  
  @app.route("/")
  def description():
    return api_help
  
  @app.route("/v1.0/create_instance/<int:fields>/<int:field_height>/<int:field_width>")
  def create_instance(fields, field_height, field_width):
    instance_id = str(uuid.uuid4())

    try:
      INSTANCES[instance_id] = core.Core(fields, field_height, field_width)
    except ValueError as vee:
      return str(vee), 402

    return jsonify({"instance_id": instance_id, "field_keys": INSTANCES[instance_id].field_keys})
  
  @app.route("/v1.0/list_instances")
  def list_instance():
    return jsonify(list(map(lambda x: { 
      "id": x,
      "fields": INSTANCES[x].fields,
      "states": INSTANCES[x].states,
      "field_height": INSTANCES[x].field_height,
      "field_width": INSTANCES[x].field_width,
      "stat_count_moves": INSTANCES[x].stat_count_moves,
      "stat_count_tetrominos": INSTANCES[x].stat_count_tetrominos,
      "current_tetrominos": list(map(lambda t: t.type_string, INSTANCES[x].current_tetrominos)),
      "current_tetrominos_x": list(map(lambda t: t.x, INSTANCES[x].current_tetrominos)),
      "current_tetrominos_y": list(map(lambda t: t.y, INSTANCES[x].current_tetrominos)),
      "next_tetrominos": list(map(lambda t: t.type_string, INSTANCES[x].next_tetrominos))
     }, INSTANCES)))
  
  @app.route("/v1.0/get_field/<uuid:instance_id>")
  def get_field(instance_id):
    return jsonify(INSTANCES[str(instance_id)].field.tolist())
  
  @app.route("/v1.0/delete_instance/<uuid:instance_id>")
  def delete_instance(instance_id):
    INSTANCES[str(instance_id)].delete()
    INSTANCES.pop(str(instance_id), 0)
    return jsonify("OK")

  return app    