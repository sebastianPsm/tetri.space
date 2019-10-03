import pytest
from rest import rest

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

def test_list_instances(client):
  client.get("/v1.0/create_instance/6/22/12")
  client.get("/v1.0/create_instance/6/22/12")
  client.get("/v1.0/create_instance/6/22/12")

  rv = client.get("/v1.0/list_instances")
  assert rv.status_code == 200
  assert len(rv.json) == 3