# Source: https://github.com/tensorflow/models/issues/9911#issuecomment-922411819

ARG TENSORFLOW_VERSION="2.6.0"

FROM tensorflow/tensorflow:${TENSORFLOW_VERSION}
ARG DEBIAN_FRONTEND=noninteractive

# Needs to be repeated, since it is cleared by FROM
ARG TENSORFLOW_VERSION

# Install apt dependencies
RUN apt-get update && apt-get install -y \
    git \
    gpg-agent \
    python3-cairocffi \
    protobuf-compiler \
    python3-pil \
    python3-lxml \
    python3-tk \
    wget

# Add new user to avoid running as root
RUN useradd -ms /bin/bash tensorflow
USER tensorflow
WORKDIR /home/tensorflow

# Clone Object Detection API
RUN git clone https://github.com/tensorflow/models/ /home/tensorflow/models/

# Compile protobuf configs
RUN (cd /home/tensorflow/models/research/ && protoc object_detection/protos/*.proto --python_out=.)
WORKDIR /home/tensorflow/models/research/

RUN cp object_detection/packages/tf2/setup.py ./
ENV PATH="/home/tensorflow/.local/bin:${PATH}"

RUN python -m pip install -U pip

# Workaround for `ModuleNotFoundError: No module named 'object_detection'`
# Lock tensorflow and corresponding tf-models-official versions. Elsewise, object_detection module
RUN python -m pip install tensorflow==${TENSORFLOW_VERSION} tensorflow-text==${TENSORFLOW_VERSION} tf-models-official==${TENSORFLOW_VERSION}
RUN python -m pip install .

ENV TF_CPP_MIN_LOG_LEVEL 3

# Download model.
WORKDIR /home/tensorflow/models/research/object_detection/test_data/
ADD --chown=tensorflow http://download.tensorflow.org/models/object_detection/tf2/20210329/deepmac_1024x1024_coco17.tar.gz .
RUN tar -xzf deepmac_1024x1024_coco17.tar.gz && rm deepmac_1024x1024_coco17.tar.gz

# Install additional dependencies
RUN python -m pip install -U scikit-image

# Set initial workdir
WORKDIR /home/tensorflow/
