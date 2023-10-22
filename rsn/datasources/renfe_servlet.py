import logging

import requests
import json
from datetime import date

from rsn.models.renfe_trip import RenfeTrip


class RenfeServletDataSource():

    def __init__(self, servlet_url: str):
        self.servlet_url: str = servlet_url

    def __get_trip_schedule_raw(self, src: int, dst: int, date) -> list[dict]:
        headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
        }

        data = {
            "nucleo": "10",
            "origen": str(src),
            "destino": str(dst),
            "fchaViaje": date.strftime("%Y%m%d"),
            "validaReglaNegocio": True,
            "tiempoReal": True,
            "servicioHorarios": "VTI",
            "horaViajeOrigen": "00",
            "horaViajeLlegada": "26",
            "accesibilidadTrenes": True
        }

        r = requests.post(self.servlet_url, headers=headers,
                          data=json.dumps(data))
        return r.json()["horario"]

    def get_trip_schedule(self, src: int, dst: int, date: date = date.today()) -> list[RenfeTrip]:
        raw_data = self.__get_trip_schedule_raw(src, dst, date)

        # Change keys to match RenfeTrip dataclass
        for trip in raw_data:
            trip["line"] = trip.pop("linea")
            trip["train_id"] = trip.pop("cdgoTren")
            trip["departure_time_str"] = trip.pop("horaSalida")
            trip["arrival_time_str"] = trip.pop("horaLlegada")
            trip["duration"] = trip.pop("duracion")
            trip["accessibility"] = trip.pop("accesible")
            trip.pop("lineaEstOrigen")
            trip.pop("lineaEstDestino")
            if "horaSalidaReal" in trip:
                trip.pop("horaSalidaReal")
            if "horaLlegadaReal" in trip:
                trip.pop("horaLlegadaReal")

        trips: list[RenfeTrip] = []
        for trip in raw_data:
            trips.append(RenfeTrip(**trip))

        return trips
