FROM python:3.11

LABEL org.opencontainers.image.source="https://github.com/Digital-Maritime-Consultancy/abnf-tool"

WORKDIR /usr/src/app

RUN useradd -m worker

RUN chown worker:worker /usr/src/app

USER worker

COPY requirements.txt .

RUN pip install --no-cache-dir wheel && pip install --no-cache-dir -r requirements.txt

COPY . .

USER root

RUN chmod +x docker-entrypoint.sh

USER worker

ENTRYPOINT ["./docker-entrypoint.sh"]

CMD ["server"]
