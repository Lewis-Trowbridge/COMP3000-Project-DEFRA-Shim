import datetime

import pandas
from fastapi import FastAPI, Response
from pyaurn import importAURN

app = FastAPI()


@app.get("/data")
async def get_data(site: str, date: datetime.datetime | None = None, metric: str | None = None):
    # Avoid using default parameters: https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments
    if date is None:
        date = datetime.datetime.now()
    data = importAURN(site, [date.year])
    if not data.empty:
        data = get_given_or_latest(data, date)
        if metric is None:
            return Response(content=data.to_json(orient="index", date_format="iso"),
                            media_type="application/json")
        else:
            return {metric: data[metric], "timestamp": data["timestamp"]}
    else:
        return Response(status_code=404)


def get_given_or_latest(data: pandas.DataFrame, date: datetime.datetime) -> pandas.Series:
    if date.date() == datetime.datetime.today().date():
        date = data.last_valid_index()
    timeslice = data.loc[date].copy()
    timeslice["timestamp"] = date
    return timeslice
