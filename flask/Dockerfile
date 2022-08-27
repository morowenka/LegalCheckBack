# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10 AS builder
#FROM python:latest

WORKDIR /src
COPY requirements.txt /src
#RUN apt update && \
#    apt add build-base

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip  \
    pip3 -v install torch==1.11.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
#RUN --mount=type=cache,target=/root/.cache/pip  \
#    pip3 -v install spacy
RUN --mount=type=cache,target=/root/.cache/pip  \
    pip3 -v install scikit-learn
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . .

CMD ["python3", "server.py"]

FROM builder as dev-envs

RUN <<EOF
apk update
apk add git
EOF

RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF

# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /

CMD ["python3", "server.py"]
