FROM --platform=$BUILDPLATFORM python:3.10-alpine as builder
RUN apk update && apk add --update git gcc libc-dev libffi-dev
WORKDIR proxy_finder
COPY ./requirements.txt .
RUN pip3 install --target=/proxy_finder/dependencies -r requirements.txt
COPY . .

FROM python:3.10-alpine
WORKDIR proxy_finder
COPY --from=builder	/proxy_finder .
ENV PYTHONPATH="${PYTHONPATH}:/proxy_finder/dependencies" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python3", "./finder.py"]
