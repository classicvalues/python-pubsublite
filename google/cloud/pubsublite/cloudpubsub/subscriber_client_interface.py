from abc import abstractmethod
from typing import (
    ContextManager,
    Union,
    AsyncContextManager,
    AsyncIterator,
    Callable,
    Optional,
    Set,
)

from google.cloud.pubsub_v1.subscriber.futures import StreamingPullFuture
from google.cloud.pubsub_v1.subscriber.message import Message

from google.cloud.pubsublite.types import (
    SubscriptionPath,
    FlowControlSettings,
    Partition,
)


class AsyncSubscriberClientInterface(AsyncContextManager):
    """
  An AsyncSubscriberClientInterface reads messages similar to Google Pub/Sub, but must be used in an
  async context.
  Any subscribe failures are unlikely to succeed if retried.

  Must be used in an `async with` block or have __aenter__() awaited before use.
  """

    @abstractmethod
    async def subscribe(
        self,
        subscription: Union[SubscriptionPath, str],
        per_partition_flow_control_settings: FlowControlSettings,
        fixed_partitions: Optional[Set[Partition]] = None,
    ) -> AsyncIterator[Message]:
        """
    Read messages from a subscription.

    Args:
      subscription: The subscription to subscribe to.
      per_partition_flow_control_settings: The flow control settings for each partition subscribed to. Note that these
          settings apply to each partition individually, not in aggregate.
      fixed_partitions: A fixed set of partitions to subscribe to. If not present, will instead use auto-assignment.

    Returns:
      An AsyncIterator with Messages that must have ack() called on each exactly once.

    Raises:
      GoogleApiCallError: On a permanent failure.
    """


MessageCallback = Callable[[Message], None]


class SubscriberClientInterface(ContextManager):
    """
  A SubscriberClientInterface reads messages similar to Google Pub/Sub.
  Any subscribe failures are unlikely to succeed if retried.

  Must be used in a `with` block or have __enter__() called before use.
  """

    @abstractmethod
    def subscribe(
        self,
        subscription: Union[SubscriptionPath, str],
        callback: MessageCallback,
        per_partition_flow_control_settings: FlowControlSettings,
        fixed_partitions: Optional[Set[Partition]] = None,
    ) -> StreamingPullFuture:
        """
    This method starts a background thread to begin pulling messages from
    a Pub/Sub Lite subscription and scheduling them to be processed using the
    provided ``callback``.

    Args:
      subscription: The subscription to subscribe to.
      callback: The callback function. This function receives the message as its only argument.
      per_partition_flow_control_settings: The flow control settings for each partition subscribed to. Note that these
          settings apply to each partition individually, not in aggregate.
      fixed_partitions: A fixed set of partitions to subscribe to. If not present, will instead use auto-assignment.

    Returns:
      A StreamingPullFuture instance that can be used to manage the background stream.

    Raises:
      GoogleApiCallError: On a permanent failure.
    """
