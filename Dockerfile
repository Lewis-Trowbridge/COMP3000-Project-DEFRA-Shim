FROM python:slim AS compile

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc zlib1g-dev libbz2-dev liblzma-dev

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:slim
COPY --from=compile /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY main.py .

ENTRYPOINT [ "python", "main.py" ]