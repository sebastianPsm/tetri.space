import uuid
import time
import threading
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
        "path": "/v1.0/get_instance",
        "description": "Get a certain instance",
        "arguments": ["tetri.space instance id"],
        "return": [
          "200 - Everything works as planned - A certain tetri.space instance"
        ]
      },
      {
        "path": "/v1.0/get_field",
        "description": "Return the whole teri.space field",
        "arguments": ["tetri.space instance id"],
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
      },
      {
        "path": "/v1.0/set_ready",
        "description": "Set field instance as ready",
        "arguments": ["tetri.space instance id", "field key"],
        "return": [
          "200 - Everything works as planned"
        ]
      }
    ]
  }
}

def thread_fcn():
  while True:
    for key in INSTANCES:
      INSTANCES[key].step(time.time())
    time.sleep(5/1000)

def create_app():
  app = Flask(__name__, instance_relative_config=True)
  #INSTANCES = {}
  daemon = threading.Thread(target=thread_fcn, daemon=True)
  daemon.start()
  
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
    
    field_keys_dict = INSTANCES[instance_id].field_keys
    field_keys = [item[0] for item in sorted(field_keys_dict.items(), key=lambda item: item[1])]

    return jsonify({"instance_id": instance_id, "field_keys": field_keys})
  
  @app.route("/v1.0/get_instance/<uuid:instance_id>")
  def get_instance(instance_id):
    instance = INSTANCES[str(instance_id)]
    return { 
      "id": instance_id,
      "fields": instance.fields,
      "states": instance.states,
      "field_height": instance.field_height,
      "field_width": instance.field_width,
      "stat_count_moves": instance.stat_count_moves,
      "stat_count_tetrominos": instance.stat_count_tetrominos,
      "stat_count_steps": instance.stat_count_steps,
      "current_tetrominos": list(map(lambda t: t.type_string, instance.current_tetrominos)),
      "current_tetrominos_x": list(map(lambda t: t.x, instance.current_tetrominos)),
      "current_tetrominos_y": list(map(lambda t: t.y, instance.current_tetrominos)),
      "next_tetrominos": list(map(lambda t: t.type_string, instance.next_tetrominos))
    }
  
  @app.route("/v1.0/list_instances")
  def list_instance():
    return jsonify(list(map(lambda x: get_instance(x), INSTANCES)))

  @app.route("/v1.0/get_field/<uuid:instance_id>")
  def get_field(instance_id):
    return jsonify(INSTANCES[str(instance_id)].field.tolist())
  
  @app.route("/v1.0/delete_instance/<uuid:instance_id>")
  def delete_instance(instance_id):
    INSTANCES[str(instance_id)].delete()
    INSTANCES.pop(str(instance_id), 0)
    return jsonify("OK")
  
  @app.route("/v1.0/set_ready/<uuid:instance_id>/<uuid:field_key>")
  def set_ready(instance_id, field_key):
    INSTANCES[str(instance_id)].ready(str(field_key))
    return jsonify("OK")

  return app    