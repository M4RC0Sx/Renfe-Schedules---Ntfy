import logging

from dataclasses import dataclass, field
from enum import IntEnum
from datetime import date, datetime

import schedule
import requests

from rsn.datasources.renfe_servlet import RenfeServletDataSource
from rsn.models.renfe_stop import RenfeStop
from rsn.models.renfe_trip import RenfeTrip


WEEKDAY = IntEnum(
    "WEEKDAY", "MONDAY TUESDAY WEDNESDAY THURSDAY FRIDAY SATURDAY SUNDAY", start=1)
WEEKDAY_SCHEDULE = {
    WEEKDAY.MONDAY: schedule.every().monday,
    WEEKDAY.TUESDAY: schedule.every().tuesday,
    WEEKDAY.WEDNESDAY: schedule.every().wednesday,
    WEEKDAY.THURSDAY: schedule.every().thursday,
    WEEKDAY.FRIDAY: schedule.every().friday,
    WEEKDAY.SATURDAY: schedule.every().saturday,
    WEEKDAY.SUNDAY: schedule.every().sunday,
}


class AlertTime:
    def __init__(self, time_str: str):
        day, time = time_str.split('-')
        self.day: WEEKDAY = WEEKDAY[day]
        self.time: str = time


@dataclass
class Notification:
    name: str
    topic: str
    enabled: bool
    src_stop: int
    dst_stop: int
    alert_times: list[str]
    trips_to_show: int
    _alert_times: list[AlertTime] = field(default_factory=list)
    src_stop_name: str = None
    dst_stop_name: str = None

    ntfy_token: str = None
    ntfy_url: str = None

    def __post_init__(self):
        self._alert_times = [AlertTime(time_str)
                             for time_str in self.alert_times]

    def set_up_ntfy(self, token: str, url: str):
        self.ntfy_token = token
        self.ntfy_url = url

    def _get_alert_msg(self, trips: list[RenfeTrip]) -> str:

        msg = f"\n🚩{self.src_stop_name}\n🏁{self.dst_stop_name}\n\n"
        if len(trips) == 0:
            msg += "No trips found! 😭\n"
            return msg

        for trip in trips:
            msg += f"🚂 {trip.line} ({trip.train_id}){' ♿' if trip.accessibility else ''}\n"
            msg += f"🕑 {trip.departure_time_str} ➡️ {trip.arrival_time_str}\n\n"
        return msg

    def __send_ntfy_request(self, msg: str):
        headers = {
            "Title": self.name,
            "Tags": "bullettrain_front",
        }
        if self.ntfy_token is not None:
            headers["Authorization"] = f"Bearer {self.ntfy_token}"

        r = requests.post(
            f"{self.ntfy_url}/{self.topic}", headers=headers, data=msg.encode('utf-8'))

        if r.status_code != 200:
            logging.error(f"Could not send notification to ntfy! - {r.text}")

    def notify(self, renfe_servlet: RenfeServletDataSource):
        trips = renfe_servlet.get_trip_schedule(
            self.src_stop, self.dst_stop, date.today())

        trips = [trip for trip in trips if trip.departure_time >
                 datetime.now().time()]
        trips = sorted(trips, key=lambda trip: trip.departure_time)[
            :self.trips_to_show]

        msg = self._get_alert_msg(trips)
        self.__send_ntfy_request(msg)

    def schedule(self, renfe_stops: list[RenfeStop], renfe_servlet: RenfeServletDataSource):

        if self.enabled is False:
            return

        self.src_stop_name = next(
            stop.stop_name for stop in renfe_stops if stop.stop_id == self.src_stop)
        self.dst_stop_name = next(
            stop.stop_name for stop in renfe_stops if stop.stop_id == self.dst_stop)

        # For some reason, this doesn't work and it only schedules the last alert time.
        # It overrides the previous scheduled jobs. So I have to use eval() instead.
        # for alert_time in self._alert_times:
        #     WEEKDAY_SCHEDULE[alert_time.day].at(
        #         alert_time.time).do(self.__notify, renfe_servlet)

        for alert_time in self._alert_times:
            eval(f"schedule.every().{str(alert_time.day.name).lower()}.at(alert_time.time).do(self.notify, renfe_servlet)",
                 {"self": self,
                  "renfe_servlet": renfe_servlet,
                  "schedule": schedule,
                  "alert_time": alert_time
                  }
                 )
