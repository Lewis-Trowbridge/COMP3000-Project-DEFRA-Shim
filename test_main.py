import datetime
import json
import unittest
from unittest.mock import patch, MagicMock

import pandas
from freezegun import freeze_time

from main import get_data


class UnitTests(unittest.IsolatedAsyncioTestCase):
    valid_date = datetime.datetime.fromtimestamp(1676419200)
    valid_date_2 = datetime.datetime.fromtimestamp(1676505600)

    @patch("main.importAURN")
    async def test_get_data_returns_404_when_empty_dataframe(self, mock_importAURN: MagicMock):
        mock_importAURN.return_value = pandas.DataFrame()

        actual = await get_data("site", datetime.datetime.now())
        assert actual.status_code == 404

    @patch("main.importAURN")
    async def test_get_data_returns_404_when_date_not_in_dataframe(self, mock_importAURN: MagicMock):
        existing_date = datetime.datetime.fromtimestamp(1676419200)
        non_existing_date = datetime.datetime.fromtimestamp(1676505600)
        mock_importAURN.return_value = pandas.DataFrame({existing_date: {}})

        actual = await get_data("site", non_existing_date)
        assert actual.status_code == 404

    @patch("main.importAURN")
    async def test_get_data_returns_all_data_with_no_metric_input(self, mock_importAURN: MagicMock):
        data = {"met1": 1.0, "met2": 2.0}
        mock_importAURN.return_value = pandas.DataFrame.from_dict({self.valid_date: data}, orient="index")

        actual = await get_data("site", self.valid_date)

        assert actual.status_code == 200
        self.assertEqual(
            json.dumps(data | {"timestamp": self.valid_date.isoformat(timespec="milliseconds")}, separators=(',', ':')),
            actual.body.decode("utf-8"))

    @patch("main.importAURN")
    async def test_get_data_returns_filtered_data_with_metric_input(self, mock_importAURN: MagicMock):
        data = {"met1": 1.0, "met2": 2.0}
        mock_importAURN.return_value = pandas.DataFrame.from_dict({self.valid_date: data}, orient="index")

        actual = await get_data("site", self.valid_date, "met1")
        self.assertEqual({"met1": 1.0, "timestamp": self.valid_date}, actual)

    @patch("main.importAURN")
    @freeze_time(valid_date_2)
    async def test_get_data_returns_latest_data_with_today_timestamp(self, mock_importAURN: MagicMock):
        data = {"met1": 1.0, "met2": 2.0}
        mock_importAURN.return_value = pandas.DataFrame.from_dict({self.valid_date: data}, orient="index")

        actual = await get_data("site", self.valid_date_2)

        assert actual.status_code == 200
        self.assertEqual(
            json.dumps(data | {"timestamp": self.valid_date.isoformat(timespec="milliseconds")}, separators=(',', ':')),
            actual.body.decode("utf-8"))

    @patch("main.importAURN")
    @freeze_time(valid_date_2)
    async def test_get_data_returns_latest_data_with_no_timestamp(self, mock_importAURN: MagicMock):
        data = {"met1": 1.0, "met2": 2.0}
        mock_importAURN.return_value = pandas.DataFrame.from_dict({self.valid_date: data}, orient="index")

        actual = await get_data("site")

        assert actual.status_code == 200
        self.assertEqual(
            json.dumps(data | {"timestamp": self.valid_date.isoformat(timespec="milliseconds")}, separators=(',', ':')),
            actual.body.decode("utf-8"))
