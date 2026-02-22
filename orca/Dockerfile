FROM python:3.11-slim AS base

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY orca ./orca
COPY fmindexer.rs/seq.fmi /fmi/seq.fmi

ENV ORCA_SHARED_SECRET=sands-shared-secret
ENV ORCA_DEFAULT_FMI_PATH=/fmi/seq.fmi
ENV ORCA_DB_PATH=/data/orca_state.db

EXPOSE 8000
ENTRYPOINT ["uvicorn", "orca.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
