import datetime
from fastapi import FastAPI, Response
from pyaurn import importAURN

app = FastAPI()


@app.get("/data")
async def get_data(site: str, date: datetime.datetime, metric: str | None = None):
    data = importAURN(site, [date.year])
    if not data.empty and date in data.index:
        if metric is None:
            return Response(content=data.loc[date].to_json(orient="index", date_format="iso"),
                            media_type="application/json")
        else:
            return {metric: data.loc[date][metric]}
    else:
        return Response(status_code=404)
