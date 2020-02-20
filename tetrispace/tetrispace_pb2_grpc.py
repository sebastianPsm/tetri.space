# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import tetrispace_pb2 as tetrispace__pb2


class TetrispaceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.CreateInstance = channel.unary_unary(
        '/tetrispace.Tetrispace/CreateInstance',
        request_serializer=tetrispace__pb2.InstanceParameter.SerializeToString,
        response_deserializer=tetrispace__pb2.InstanceIdentifier.FromString,
        )
    self.GetField = channel.unary_unary(
        '/tetrispace.Tetrispace/GetField',
        request_serializer=tetrispace__pb2.InstanceIdentifier.SerializeToString,
        response_deserializer=tetrispace__pb2.FieldKey.FromString,
        )
    self.GetFieldStatusStream = channel.unary_stream(
        '/tetrispace.Tetrispace/GetFieldStatusStream',
        request_serializer=tetrispace__pb2.FieldKey.SerializeToString,
        response_deserializer=tetrispace__pb2.FieldStatus.FromString,
        )
    self.ListInstances = channel.unary_unary(
        '/tetrispace.Tetrispace/ListInstances',
        request_serializer=tetrispace__pb2.ListInstancesParams.SerializeToString,
        response_deserializer=tetrispace__pb2.Instances.FromString,
        )
    self.GetInstance = channel.unary_unary(
        '/tetrispace.Tetrispace/GetInstance',
        request_serializer=tetrispace__pb2.InstanceIdentifier.SerializeToString,
        response_deserializer=tetrispace__pb2.Instance.FromString,
        )
    self.DeleteInstance = channel.unary_unary(
        '/tetrispace.Tetrispace/DeleteInstance',
        request_serializer=tetrispace__pb2.InstanceIdentifier.SerializeToString,
        response_deserializer=tetrispace__pb2.DeleteInstanceReturn.FromString,
        )
    self.SetReady = channel.unary_unary(
        '/tetrispace.Tetrispace/SetReady',
        request_serializer=tetrispace__pb2.FieldKey.SerializeToString,
        response_deserializer=tetrispace__pb2.Status.FromString,
        )


class TetrispaceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def CreateInstance(self, request, context):
    """Creates a new tetri.space instance and returns the instance identifier string
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetField(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetFieldStatusStream(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListInstances(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetInstance(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def DeleteInstance(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SetReady(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_TetrispaceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'CreateInstance': grpc.unary_unary_rpc_method_handler(
          servicer.CreateInstance,
          request_deserializer=tetrispace__pb2.InstanceParameter.FromString,
          response_serializer=tetrispace__pb2.InstanceIdentifier.SerializeToString,
      ),
      'GetField': grpc.unary_unary_rpc_method_handler(
          servicer.GetField,
          request_deserializer=tetrispace__pb2.InstanceIdentifier.FromString,
          response_serializer=tetrispace__pb2.FieldKey.SerializeToString,
      ),
      'GetFieldStatusStream': grpc.unary_stream_rpc_method_handler(
          servicer.GetFieldStatusStream,
          request_deserializer=tetrispace__pb2.FieldKey.FromString,
          response_serializer=tetrispace__pb2.FieldStatus.SerializeToString,
      ),
      'ListInstances': grpc.unary_unary_rpc_method_handler(
          servicer.ListInstances,
          request_deserializer=tetrispace__pb2.ListInstancesParams.FromString,
          response_serializer=tetrispace__pb2.Instances.SerializeToString,
      ),
      'GetInstance': grpc.unary_unary_rpc_method_handler(
          servicer.GetInstance,
          request_deserializer=tetrispace__pb2.InstanceIdentifier.FromString,
          response_serializer=tetrispace__pb2.Instance.SerializeToString,
      ),
      'DeleteInstance': grpc.unary_unary_rpc_method_handler(
          servicer.DeleteInstance,
          request_deserializer=tetrispace__pb2.InstanceIdentifier.FromString,
          response_serializer=tetrispace__pb2.DeleteInstanceReturn.SerializeToString,
      ),
      'SetReady': grpc.unary_unary_rpc_method_handler(
          servicer.SetReady,
          request_deserializer=tetrispace__pb2.FieldKey.FromString,
          response_serializer=tetrispace__pb2.Status.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'tetrispace.Tetrispace', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
