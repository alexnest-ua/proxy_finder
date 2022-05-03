FROM --platform=$BUILDPLATFORM python:3.10-alpine as builder
RUN apk update && apk add --update git gcc libc-dev libffi-dev
WORKDIR proxy_finder
COPY ./requirements.txt .
RUN pip3 install --target=/proxy_finder/dependencies -r requirements.txt
COPY . .

FROM python:3.10-alpine
WORKDIR proxy_finder
COPY --from=builder	/proxy_finder .
RUN sysctl -w net.core.somaxconn=32768 && sysctl -w net.ipv4.ip_local_port_range="16384 65535"
ENV PYTHONPATH="${PYTHONPATH}:/proxy_finder/dependencies" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python3", "./finder.py"]
