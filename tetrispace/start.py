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

    def CreateInstance(self, request, context):
        instance_id = str(uuid.uuid4())

        self.INSTANCES[instance_id] = core.Core(request.fields, request.height, request.width)
    
        field_keys_dict = self.INSTANCES[instance_id].field_keys
        field_keys = [item[0] for item in sorted(field_keys_dict.items(), key=lambda item: item[1])]
        
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
        return tetrispace_pb2.Instances(list=list(map(lambda x: self._getInstance(x), self.INSTANCES)))

    def GetInstance(self, request, context):
        return self._getInstance(request.uuid)

    def DeleteInstance(self, request, context):
        self.INSTANCES[request.uuid].delete()
        self.INSTANCES.pop(request.uuid, 0)
        return tetrispace_pb2.DeleteInstanceReturn()

    def GetField(self, request, context):
        instance = self.INSTANCES[request.uuid]

        data = []
        for field in instance.field.tolist():
            for row in field:
                for col in row:
                    data.append(col)

        return tetrispace_pb2.Field(fields=instance.fields, height=instance.field_height, width=instance.field_width, data=data)

    def SetReady(self, request, context):
        instance_id = request.instance_id.uuid
        for field_key in request.field_keys:
            self.INSTANCES[instance_id].ready(field_key)
        return tetrispace_pb2.Status()

if __name__ == "__main__":
    logging.basicConfig()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    tetrispace_pb2_grpc.add_TetrispaceServicer_to_server(TetrispaceService(), server)
    server.add_insecure_port("[::]:5000")
    server.start()
    server.wait_for_termination()