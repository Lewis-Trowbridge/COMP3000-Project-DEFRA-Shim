import datetime
import json
import unittest
from unittest.mock import patch, MagicMock

import pandas

from main import get_data


class UnitTests(unittest.IsolatedAsyncioTestCase):

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
        date = datetime.datetime.fromtimestamp(1676419200)

        data = {"met1": 1.0, "met2": 2.0}
        mock_importAURN.return_value = pandas.DataFrame.from_dict({date: data}, orient="index")

        actual = await get_data("site", date)

        assert actual.status_code == 200
        self.assertEqual(json.dumps(data | {"timestamp": date.isoformat(timespec="milliseconds")}, separators=(',', ':')),
                         actual.body.decode("utf-8"))

    @patch("main.importAURN")
    async def test_get_data_returns_filtered_data_with_metric_input(self, mock_importAURN: MagicMock):
        date = datetime.datetime.fromtimestamp(1676419200)

        data = {"met1": 1.0, "met2": 2.0}
        mock_importAURN.return_value = pandas.DataFrame.from_dict({date: data}, orient="index")

        actual = await get_data("site", date, "met1")
        self.assertEqual({"met1": 1.0, "timestamp": date}, actual)
