import logging

import os
import json
import time

import schedule

from rsn.datasources.renfe_data import RenfeDataSource
from rsn.datasources.renfe_servlet import RenfeServletDataSource
from rsn.models.notification import Notification


LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO").upper()

RENFE_DATA_URL = os.getenv("RENFE_DATA_URL")
RENFE_SERVLET_URL = os.getenv("RENFE_SERVLET_URL")

NTFY_TOKEN = os.getenv("NTFY_TOKEN")
NTFY_URL = os.getenv("NTFY_URL")


def __load_notifications() -> list[Notification]:
    notifications: list[Notification] = []
    with open('notifications.json', 'r') as f:
        notifications_json = json.load(f)
        for notification_json in notifications_json:
            n = Notification(**notification_json)
            n.set_up_ntfy(NTFY_TOKEN, NTFY_URL)
            notifications.append(n)
    return notifications


def main():

    if RENFE_DATA_URL is None or RENFE_SERVLET_URL is None or NTFY_URL is None:
        logging.error("Missing environment variables!")
        exit(1)

    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=LOGGING_LEVEL)

    notifications = __load_notifications()

    renfe_data = RenfeDataSource(RENFE_DATA_URL)

    stops = renfe_data.get_renfe_data()
    if stops is None:
        logging.error("Could not load Renfe data!")
        exit(1)

    renfe_servlet = RenfeServletDataSource(RENFE_SERVLET_URL)

    for notification in notifications:
        notification.schedule(stops, renfe_servlet)

    logging.debug(schedule.get_jobs())
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
