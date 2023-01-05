from email import message

from pymercure.message import Message
from pymercure.publisher.sync import SyncPublisher

from settings import MERCURE_PUBLISHER_JWT_KEY, MERCURE_TOPIC, MERCURE_URL

mercure_publisher = SyncPublisher(
    mercure_hub=MERCURE_URL, mercure_jwt=MERCURE_PUBLISHER_JWT_KEY
)


async def send_mercure_message(data):
    message = Message([MERCURE_TOPIC], data)
    mercure_publisher.publish(message=message)
