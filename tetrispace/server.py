import uuid
from concurrent import futures
import logging
import grpc
import tetrispace_pb2
import tetrispace_pb2_grpc
import core

class TetrispaceService(tetrispace_pb2_grpc.TetrispaceServicer):
    def __init__(self):
        self.INSTANCES = {}
        self.FIELD_KEY = {}

    def CreateInstance(self, request, context):
        instance_id = str(uuid.uuid4())

        self.INSTANCES[instance_id] = core.Core(request.fields, request.height, request.width)

        print(f"CreateInstance, {request.fields}, {request.height}, {request.width}")
    
        field_keys_dict = self.INSTANCES[instance_id].field_keys
        field_keys = [item[0] for item in sorted(field_keys_dict.items(), key=lambda item: item[1])]
        for key in field_keys:
            self.FIELD_KEY[key] = instance_id
        
        instance_id = tetrispace_pb2.InstanceIdentifier(uuid=instance_id)
        return tetrispace_pb2.InstanceAndFields(instance_id=instance_id, field_keys=field_keys)
    
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
        self.INSTANCES[request.uuid].delete()
        self.INSTANCES.pop(request.uuid, 0)
        print(f"DeleteInstance, {request.uuid}")
        return tetrispace_pb2.DeleteInstanceReturn()

    def GetField(self, request, context):
        field_key = request.uuid
        instance_key = self.FIELD_KEY[field_key]
        instance = self.INSTANCES[instance_key]
        fields, others, current_tetromino, next_tetromino = instance.get_field(field_key)

        data = []
        for row in fields.tolist():
            data += row
        
        other_data = []
        for other in others.tolist():
            for row in other:
                other_data += row

        print(f"GetField, {request.uuid}")
        return tetrispace_pb2.Field(fields=instance.fields, 
                                    height=instance.field_height,
                                    width=instance.field_width,
                                    current_tetromino=current_tetromino.type_string,
                                    current_tetromino_x=current_tetromino.x,
                                    current_tetromino_y=current_tetromino.y,
                                    next_tetromino=next_tetromino.type_string,
                                    data=data,
                                    others=other_data)

    def SetReady(self, request, context):
        instance_id = request.instance_id.uuid
        for field_key in request.field_keys:
            self.INSTANCES[instance_id].ready(field_key)
        print(f"SetReady, {request.uuid}")
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