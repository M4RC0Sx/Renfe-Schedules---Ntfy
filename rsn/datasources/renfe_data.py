import logging

import io
import requests
import zipfile
import csv

from rsn.models.renfe_stop import RenfeStop


class RenfeDataSource():

    def __init__(self, service_url: str):
        self.service_url: str = service_url

    def __get_zip_file(self, url: str) -> zipfile.ZipFile:
        r = requests.get(url)
        zip_file = zipfile.ZipFile(io.BytesIO(r.content))
        return zip_file

    def __process_zip_file(self, zip_file: zipfile.ZipFile) -> list[RenfeStop]:
        stops: list[RenfeStop] = []
        with zip_file.open('stops.txt') as csvfile:
            reader = csv.DictReader(io.TextIOWrapper(
                csvfile, 'utf-8'), delimiter=',')

            reader.fieldnames = [field.strip() for field in reader.fieldnames]
            for row in reader:
                stops.append(RenfeStop(**{
                    'stop_id': int(row['stop_id']),
                    'stop_name': row['stop_name'],
                    'stop_lat': float(row['stop_lat']),
                    'stop_lon': float(row['stop_lon'])
                }))
        return stops

    def get_renfe_data(self) -> list[RenfeStop] | None:
        try:
            zip_file = self.__get_zip_file(self.service_url)
        except Exception as e:
            logging.error(f"Could not download Renfe data! - {str(e)}")
            return None

        try:
            return self.__process_zip_file(zip_file)
        except Exception as e:
            logging.error(f"Could not process Renfe data! - {str(e)}")
            return None
