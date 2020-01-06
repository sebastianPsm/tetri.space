import pytest
from tetrispace import rest

@pytest.fixture
def client():
  client = rest.create_app().test_client()
  yield client
  del client

def test_create_unsuccessful(client):
  rv = client.get("/v1.0/create_instance")
  assert rv.status_code == 404

def test_create(client):
  rv = client.get("/v1.0/create_instance/6/22/12")
  assert rv.status_code == 200
  assert rv.json["instance_id"]
  assert rv.json["field_keys"]
  assert len(rv.json["field_keys"]) == 6

def test_list_instances(client):
  rv = client.get("/v1.0/list_instances")
  start = len(rv.json)
  client.get("/v1.0/create_instance/6/22/12")
  client.get("/v1.0/create_instance/6/22/12")
  client.get("/v1.0/create_instance/6/22/12")

  rv = client.get("/v1.0/list_instances")
  end = len(rv.json)
  assert rv.status_code == 200
  assert end == start + 3

def test_delete_instance(client):
  # create
  rv = client.get("/v1.0/create_instance/6/22/12")
  assert rv.status_code == 200

  instance_id = rv.json["instance_id"]

  # delete
  rv = client.get(f"/v1.0/delete_instance/{instance_id}")
  assert rv.status_code == 200

def test_set_ready(client):
  n = 6

  # create
  rv = client.get(f"/v1.0/create_instance/{n}/22/12")
  assert rv.status_code == 200

  instance_id = rv.json["instance_id"]
  field_keys = rv.json["field_keys"]


  # set ready
  for idx in range(n):
    rv = client.get(f"/v1.0/set_ready/{instance_id}/{field_keys[idx]}")
    assert rv.status_code == 200

    # test for ready state
    rv = client.get(f"/v1.0/get_instance/{instance_id}")
    assert rv.status_code == 200
    
    if idx < n-1:
      assert rv.json["states"][idx] == 2
  
  # test for steady state
  for idx in range(n):
    assert rv.json["states"][idx] == 3
    