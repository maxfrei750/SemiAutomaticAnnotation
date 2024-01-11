# TODO: Merge with serving.Dockerfile to use a single, common base image.

ARG TENSORFLOW_VERSION="2.6.0"

FROM tensorflow/tensorflow:${TENSORFLOW_VERSION}
ARG DEBIAN_FRONTEND=noninteractive

ARG USERNAME=tensorflow
ARG USERID=1000
RUN useradd --system --create-home --shell /bin/bash --uid $USERID $USERNAME
USER $USERNAME
WORKDIR /home/$USERNAME

# Install additional dependencies
COPY requirements-client.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
  python -m pip install -r requirements-client.txt

# Set initial workdir
WORKDIR /home/tensorflow/app
