import datetime

import grpc
from google.api_core.exceptions import GoogleAPICallError
from google.protobuf.timestamp_pb2 import Timestamp
from google.pubsub_v1 import PubsubMessage
from google.cloud.pubsublite.cloudpubsub.message_transforms import PUBSUB_LITE_EVENT_TIME, to_cps_subscribe_message, \
  encode_attribute_event_time, from_cps_publish_message
from google.cloud.pubsublite_v1 import SequencedMessage, Cursor, PubSubMessage, AttributeValues

NOT_UTF8 = bytes.fromhex('ffff')


def test_invalid_subscribe_transform_key():
  try:
    to_cps_subscribe_message(
      SequencedMessage(message=PubSubMessage(key=NOT_UTF8), publish_time=Timestamp(), cursor=Cursor(offset=10),
                       size_bytes=10))
    assert False
  except GoogleAPICallError as e:
    assert e.grpc_status_code == grpc.StatusCode.INVALID_ARGUMENT


def test_invalid_subscribe_contains_magic_attribute():
  try:
    to_cps_subscribe_message(SequencedMessage(
      message=PubSubMessage(key=b'def', attributes={PUBSUB_LITE_EVENT_TIME: AttributeValues(values=[b'abc'])}),
      publish_time=Timestamp(seconds=10), cursor=Cursor(offset=10), size_bytes=10))
    assert False
  except GoogleAPICallError as e:
    assert e.grpc_status_code == grpc.StatusCode.INVALID_ARGUMENT


def test_invalid_subscribe_contains_multiple_attributes():
  try:
    to_cps_subscribe_message(SequencedMessage(
      message=PubSubMessage(key=b'def', attributes={'xyz': AttributeValues(values=[b'abc', b''])}),
      publish_time=Timestamp(seconds=10), cursor=Cursor(offset=10), size_bytes=10))
    assert False
  except GoogleAPICallError as e:
    assert e.grpc_status_code == grpc.StatusCode.INVALID_ARGUMENT


def test_invalid_subscribe_contains_non_utf8_attributes():
  try:
    to_cps_subscribe_message(SequencedMessage(
      message=PubSubMessage(key=b'def', attributes={'xyz': AttributeValues(values=[NOT_UTF8])}),
      publish_time=Timestamp(seconds=10), cursor=Cursor(offset=10), size_bytes=10))
    assert False
  except GoogleAPICallError as e:
    assert e.grpc_status_code == grpc.StatusCode.INVALID_ARGUMENT


def test_subscribe_transform_correct():
  expected = PubsubMessage(
    data=b'xyz', ordering_key='def', attributes={'x': 'abc', 'y': 'abc',
                                                 PUBSUB_LITE_EVENT_TIME: encode_attribute_event_time(
                                                   Timestamp(seconds=55).ToDatetime())},
    message_id=str(10), publish_time=Timestamp(seconds=10))
  result = to_cps_subscribe_message(SequencedMessage(
    message=PubSubMessage(data=b'xyz', key=b'def', event_time=Timestamp(seconds=55),
                          attributes={'x': AttributeValues(values=[b'abc']), 'y': AttributeValues(values=[b'abc'])}),
    publish_time=Timestamp(seconds=10), cursor=Cursor(offset=10), size_bytes=10))
  assert result == expected


def test_publish_invalid_event_time():
  try:
    from_cps_publish_message(PubsubMessage(attributes={PUBSUB_LITE_EVENT_TIME: 'probably not an encoded proto'}))
    assert False
  except GoogleAPICallError as e:
    assert e.grpc_status_code == grpc.StatusCode.INVALID_ARGUMENT


def test_publish_valid_transform():
  now = datetime.datetime.now()
  expected = PubSubMessage(data=b'xyz', key=b'def', event_time=now,
                           attributes={'x': AttributeValues(values=[b'abc']), 'y': AttributeValues(values=[b'abc'])})
  result = from_cps_publish_message(PubsubMessage(
    data=b'xyz', ordering_key='def', attributes={'x': 'abc', 'y': 'abc',
                                                 PUBSUB_LITE_EVENT_TIME: encode_attribute_event_time(
                                                   now)}))
  assert result == expected
