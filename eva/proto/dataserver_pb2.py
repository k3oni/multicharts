# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: dataserver.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)




DESCRIPTOR = _descriptor.FileDescriptor(
  name='dataserver.proto',
  package='EVA.DataServer.ProtoBuf',
  serialized_pb='\n\x10\x64\x61taserver.proto\x12\x17\x45VA.DataServer.ProtoBuf\"\xd7\x06\n\x0bMessageBase\x12>\n\x04type\x18\x01 \x02(\x0e\x32\x30.EVA.DataServer.ProtoBuf.MessageBase.MessageType\x12\x11\n\trequestId\x18\x02 \x01(\x05\x12\x41\n\x03ldr\x18\x03 \x01(\x0b\x32\x34.EVA.DataServer.ProtoBuf.MessageBase.LiveDataRequest\x12G\n\x03hdr\x18\x04 \x01(\x0b\x32:.EVA.DataServer.ProtoBuf.MessageBase.HistoricalDataRequest\x1a\x37\n\x0bSessionType\x12\x14\n\x0csessionBegin\x18\x01 \x02(\t\x12\x12\n\nsessionEnd\x18\x02 \x02(\t\x1a\xed\x01\n\x0fLiveDataRequest\x12\x12\n\ninstrument\x18\x01 \x01(\t\x12\x10\n\x08\x64\x61taType\x18\x02 \x01(\x05\x12\r\n\x05today\x18\x03 \x01(\t\x12\x41\n\x07session\x18\x04 \x01(\x0b\x32\x30.EVA.DataServer.ProtoBuf.MessageBase.SessionType\x12\x0b\n\x03url\x18\x05 \x01(\t\x12\x11\n\tbarLength\x18\x06 \x01(\t\x12\x42\n\x08sessions\x18\x07 \x03(\x0b\x32\x30.EVA.DataServer.ProtoBuf.MessageBase.SessionType\x1a\xf3\x01\n\x15HistoricalDataRequest\x12\x12\n\ninstrument\x18\x01 \x01(\t\x12\x12\n\nexpireYear\x18\x02 \x01(\t\x12\x13\n\x0b\x65xpireMonth\x18\x03 \x01(\t\x12\x10\n\x08typeCode\x18\x04 \x01(\t\x12\x10\n\x08\x64\x61taType\x18\x05 \x01(\x05\x12\x11\n\tbarLength\x18\x06 \x01(\t\x12\x11\n\tstartDate\x18\x07 \x01(\t\x12\x0f\n\x07\x65ndDate\x18\x08 \x01(\t\x12\x42\n\x08sessions\x18\t \x03(\x0b\x32\x30.EVA.DataServer.ProtoBuf.MessageBase.SessionType\"J\n\x0bMessageType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x13\n\x0frequestLiveData\x10\x01\x12\x19\n\x15requestHistoricalData\x10\x02')



_MESSAGEBASE_MESSAGETYPE = _descriptor.EnumDescriptor(
  name='MessageType',
  full_name='EVA.DataServer.ProtoBuf.MessageBase.MessageType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='requestLiveData', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='requestHistoricalData', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=827,
  serialized_end=901,
)


_MESSAGEBASE_SESSIONTYPE = _descriptor.Descriptor(
  name='SessionType',
  full_name='EVA.DataServer.ProtoBuf.MessageBase.SessionType',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sessionBegin', full_name='EVA.DataServer.ProtoBuf.MessageBase.SessionType.sessionBegin', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sessionEnd', full_name='EVA.DataServer.ProtoBuf.MessageBase.SessionType.sessionEnd', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=284,
  serialized_end=339,
)

_MESSAGEBASE_LIVEDATAREQUEST = _descriptor.Descriptor(
  name='LiveDataRequest',
  full_name='EVA.DataServer.ProtoBuf.MessageBase.LiveDataRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instrument', full_name='EVA.DataServer.ProtoBuf.MessageBase.LiveDataRequest.instrument', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dataType', full_name='EVA.DataServer.ProtoBuf.MessageBase.LiveDataRequest.dataType', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='today', full_name='EVA.DataServer.ProtoBuf.MessageBase.LiveDataRequest.today', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='session', full_name='EVA.DataServer.ProtoBuf.MessageBase.LiveDataRequest.session', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='url', full_name='EVA.DataServer.ProtoBuf.MessageBase.LiveDataRequest.url', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='barLength', full_name='EVA.DataServer.ProtoBuf.MessageBase.LiveDataRequest.barLength', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sessions', full_name='EVA.DataServer.ProtoBuf.MessageBase.LiveDataRequest.sessions', index=6,
      number=7, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=342,
  serialized_end=579,
)

_MESSAGEBASE_HISTORICALDATAREQUEST = _descriptor.Descriptor(
  name='HistoricalDataRequest',
  full_name='EVA.DataServer.ProtoBuf.MessageBase.HistoricalDataRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='instrument', full_name='EVA.DataServer.ProtoBuf.MessageBase.HistoricalDataRequest.instrument', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='expireYear', full_name='EVA.DataServer.ProtoBuf.MessageBase.HistoricalDataRequest.expireYear', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='expireMonth', full_name='EVA.DataServer.ProtoBuf.MessageBase.HistoricalDataRequest.expireMonth', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='typeCode', full_name='EVA.DataServer.ProtoBuf.MessageBase.HistoricalDataRequest.typeCode', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dataType', full_name='EVA.DataServer.ProtoBuf.MessageBase.HistoricalDataRequest.dataType', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='barLength', full_name='EVA.DataServer.ProtoBuf.MessageBase.HistoricalDataRequest.barLength', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='startDate', full_name='EVA.DataServer.ProtoBuf.MessageBase.HistoricalDataRequest.startDate', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='endDate', full_name='EVA.DataServer.ProtoBuf.MessageBase.HistoricalDataRequest.endDate', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sessions', full_name='EVA.DataServer.ProtoBuf.MessageBase.HistoricalDataRequest.sessions', index=8,
      number=9, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=582,
  serialized_end=825,
)

_MESSAGEBASE = _descriptor.Descriptor(
  name='MessageBase',
  full_name='EVA.DataServer.ProtoBuf.MessageBase',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='EVA.DataServer.ProtoBuf.MessageBase.type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='requestId', full_name='EVA.DataServer.ProtoBuf.MessageBase.requestId', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ldr', full_name='EVA.DataServer.ProtoBuf.MessageBase.ldr', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='hdr', full_name='EVA.DataServer.ProtoBuf.MessageBase.hdr', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_MESSAGEBASE_SESSIONTYPE, _MESSAGEBASE_LIVEDATAREQUEST, _MESSAGEBASE_HISTORICALDATAREQUEST, ],
  enum_types=[
    _MESSAGEBASE_MESSAGETYPE,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=46,
  serialized_end=901,
)

_MESSAGEBASE_SESSIONTYPE.containing_type = _MESSAGEBASE;
_MESSAGEBASE_LIVEDATAREQUEST.fields_by_name['session'].message_type = _MESSAGEBASE_SESSIONTYPE
_MESSAGEBASE_LIVEDATAREQUEST.fields_by_name['sessions'].message_type = _MESSAGEBASE_SESSIONTYPE
_MESSAGEBASE_LIVEDATAREQUEST.containing_type = _MESSAGEBASE;
_MESSAGEBASE_HISTORICALDATAREQUEST.fields_by_name['sessions'].message_type = _MESSAGEBASE_SESSIONTYPE
_MESSAGEBASE_HISTORICALDATAREQUEST.containing_type = _MESSAGEBASE;
_MESSAGEBASE.fields_by_name['type'].enum_type = _MESSAGEBASE_MESSAGETYPE
_MESSAGEBASE.fields_by_name['ldr'].message_type = _MESSAGEBASE_LIVEDATAREQUEST
_MESSAGEBASE.fields_by_name['hdr'].message_type = _MESSAGEBASE_HISTORICALDATAREQUEST
_MESSAGEBASE_MESSAGETYPE.containing_type = _MESSAGEBASE;
DESCRIPTOR.message_types_by_name['MessageBase'] = _MESSAGEBASE

class MessageBase(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType

  class SessionType(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _MESSAGEBASE_SESSIONTYPE

    # @@protoc_insertion_point(class_scope:EVA.DataServer.ProtoBuf.MessageBase.SessionType)

  class LiveDataRequest(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _MESSAGEBASE_LIVEDATAREQUEST

    # @@protoc_insertion_point(class_scope:EVA.DataServer.ProtoBuf.MessageBase.LiveDataRequest)

  class HistoricalDataRequest(_message.Message):
    __metaclass__ = _reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _MESSAGEBASE_HISTORICALDATAREQUEST

    # @@protoc_insertion_point(class_scope:EVA.DataServer.ProtoBuf.MessageBase.HistoricalDataRequest)
  DESCRIPTOR = _MESSAGEBASE

  # @@protoc_insertion_point(class_scope:EVA.DataServer.ProtoBuf.MessageBase)


# @@protoc_insertion_point(module_scope)