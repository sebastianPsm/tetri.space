import time
import uuid
from concurrent import futures
from random_word import RandomWords
import logging
import grpc
import tetrispace_pb2
import tetrispace_pb2_grpc
import core

class TetrispaceService(tetrispace_pb2_grpc.TetrispaceServicer):
    def __init__(self):
        self.INSTANCES = {}
        self.RANDOM_WORDS = {}
        self.FIELD_KEY = {}
        self.r = RandomWords()

    def CreateInstance(self, request, context):
        print(f"CreateInstance, {request.fields}, {request.height}, {request.width}")

        instance_id = str(uuid.uuid4())
        random_word = "tetri." + self.r.get_random_word(includePartOfSpeech="noun", maxLength=5)
        self.RANDOM_WORDS[random_word] = instance_id
        self.INSTANCES[instance_id] = {
            "max_fields": request.fields,
            "fields": 0,
            "field_keys": {},
            "set_ready": [],
            "height": request.height,
            "width": request.width,
            "random_word": random_word,
            "core": None
        }        
    
        #field_keys_dict = self.INSTANCES[instance_id].field_keys
        #field_keys = [item[0] for item in sorted(field_keys_dict.items(), key=lambda item: item[1])]
        #for key in field_keys:
        #    self.FIELD_KEY[key] = instance_id
        
        #instance_id = tetrispace_pb2.InstanceIdentifier(uuid=instance_id)

        #random_word = "tetri." + self.r.get_random_word(includePartOfSpeech="noun", maxLength=5)

        return tetrispace_pb2.InstanceIdentifier(uuid=instance_id, random_word=random_word)
    
    def _getInstance(self, field_id):
        instance = self.INSTANCES[field_id]
        return tetrispace_pb2.Instance(instance_id=tetrispace_pb2.InstanceIdentifier(uuid=field_id),
                                       fields=instance.fields,
                                       states=instance.states,
                                       height=instance.field_height,
                                       width=instance.field_width,
                                       stat_count_moves=instance.stat_count_moves,
                                       stat_count_tetrominos=instance.stat_count_tetrominos,
                                       stat_count_steps=instance.stat_count_steps,
                                       current_tetrominos=list(map(lambda t: t.type_string, instance.current_tetrominos)),
                                       current_tetrominos_x=list(map(lambda t: t.x, instance.current_tetrominos)),
                                       current_tetrominos_y=list(map(lambda t: t.y, instance.current_tetrominos)),
                                       next_tetrominos=list(map(lambda t: t.type_string, instance.next_tetrominos)))

    def ListInstances(self, request, context):
        print(f"ListInstances")

        return tetrispace_pb2.Instances(list=list(map(lambda x: self._getInstance(x), self.INSTANCES)))

    def GetInstance(self, request, context):
        print(f"GetInstance, {request.uuid}")

        return self._getInstance(request.uuid)

    def DeleteInstance(self, request, context):
        print(f"DeleteInstance, {request.uuid}")

        if request.uuid:
            self.INSTANCES.pop(request.uuid, 0)

        return tetrispace_pb2.DeleteInstanceReturn()

    def GetField(self, request, context):
        print(f"GetField, {request.random_word}")

        random_word = request.random_word
        instance_key = self.RANDOM_WORDS[random_word]
        field_key = str(uuid.uuid4())

        # no more space left
        if self.INSTANCES[instance_key]["fields"] == self.INSTANCES[instance_key]["max_fields"]:
            return tetrispace_pb2.FieldKey()

        self.INSTANCES[instance_key]["field_keys"][field_key] = self.INSTANCES[instance_key]["fields"]
        self.INSTANCES[instance_key]["fields"] += 1
        self.FIELD_KEY[field_key] = instance_key

        return tetrispace_pb2.FieldKey(uuid=field_key)

    def CloseField(FieldKey):
        pass

    def _fillFieldStatus(self, instance, field_key):
        print(instance["set_ready"])
        field_status = tetrispace_pb2.FieldStatus(max_fields=instance["max_fields"],
                                                  set_ready_fields=len(instance["set_ready"]),
                                                  fields=instance["fields"],
                                                  height=instance["height"],
                                                  width=instance["width"])
        if(instance["core"]):
            pass
            #fields, others, current_tetromino, next_tetromino = instance["core"].get_field(field_key)

            #data = []
            #for row in fields.tolist():
            #    data += row
            
            #other_data = []
            #for other in others.tolist():
            #    for row in other:
            #        other_data += row
            
            
            #field_status.current_tetromino = current_tetromino.type_string
            #field_status.current_tetromino_x = current_tetromino.x
            #field_status.current_tetromino_y = current_tetromino.y
            #field_status.next_tetromino = next_tetromino.type_string
            #field_status.data = data
            #field_status.others = other_data
        
        return field_status

    def GetFieldStatusStream(self, request, context):
        print(f"GetFieldStatusStream, {request.uuid}")
        instance_id = self.FIELD_KEY[request.uuid]

        while True:
            time.sleep(1)
            if instance_id in self.INSTANCES:
                res = self._fillFieldStatus(self.INSTANCES[instance_id], request.uuid)
            else:
                res = tetrispace_pb2.FieldStatus(game_over="Because game creator has left")
            yield res

    def SetReady(self, request, context):
        print(f"SetReady, {request.uuid}")

        assert request.uuid in self.FIELD_KEY
        instance_key = self.FIELD_KEY[request.uuid]
        instance = self.INSTANCES[instance_key]

        if not request.uuid in instance["set_ready"]:
            instance["set_ready"].append(request.uuid)
        
        if len(instance["set_ready"]) == instance["fields"]:
            instance["core"] = core.Core(instance["fields"], instance["height"], instance["width"])

        return tetrispace_pb2.Status()

if __name__ == "__main__":
    port = 5000
    logging.basicConfig()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    tetrispace_pb2_grpc.add_TetrispaceServicer_to_server(TetrispaceService(), server)
    server.add_insecure_port(f"[::]:{port}")
    print(f"Start tetri.space server on port {port}")
    server.start()
    server.wait_for_termination()