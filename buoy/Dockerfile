FROM rust:1.90 AS builder

WORKDIR /build
COPY fmindexer.rs ./fmindexer.rs
RUN cd fmindexer.rs && cargo build --release

FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY buoy ./buoy
COPY --from=builder /build/fmindexer.rs/target/release/fmindexer /usr/local/bin/fmindexer

ENV ORCA_SHARED_SECRET=sands-shared-secret
ENV FMINDEXER_BIN=/usr/local/bin/fmindexer

EXPOSE 8001
ENTRYPOINT ["uvicorn", "buoy.app.main:app", "--host", "0.0.0.0", "--port", "8001"]
