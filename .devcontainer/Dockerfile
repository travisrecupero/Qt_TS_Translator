FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        qt6-l10n-tools \
        git \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/lib/qt6/bin:${PATH}"

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

WORKDIR /workspace
