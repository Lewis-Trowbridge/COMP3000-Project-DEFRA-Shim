import datetime
from fastapi import FastAPI, Response
from pyaurn import importAURN

app = FastAPI()


@app.get("/data")
async def get_data(site: str, date: datetime.datetime):
    data = importAURN(site, [date.year])
    if not data.empty and date in data.index:
        return Response(content=data.loc[date].to_json(orient="index", date_format="iso"),
                        media_type="application/json")
    else:
        return Response(status_code=404)
