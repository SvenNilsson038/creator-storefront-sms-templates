import os

from infrai_sms import InfraiSms
from store_sms.models import SubscriberUpdate, choose_message


def main() -> None:
    update = SubscriberUpdate(os.environ["CREATOR_ID"], os.environ["SUBSCRIBER_PHONE"], os.environ["ASSET_TITLE"], os.getenv("PROCESSING_STATE", "ready"))
    message = choose_message(update)
    client = InfraiSms()
    print(client.send(update.phone, message.template_id, message.template_vars))


if __name__ == "__main__":
    main()
