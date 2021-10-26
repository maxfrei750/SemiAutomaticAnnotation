# Source: https://github.com/tensorflow/models/issues/9911#issuecomment-922411819
# TODO: Remove gpu dependency.

FROM tensorflow/tensorflow:2.3.0-gpu
ARG DEBIAN_FRONTEND=noninteractive

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

# Workaround: If you use TF 2.2.x, uncomment the line below.
# WORKDIR /home/tensorflow/models/
# RUN git checkout 03a6d6c8e79b426231a4d5ba0cf45be9afc8bad5

# Workaround: If you use TF 2.3.x, uncomment the line below.
WORKDIR /home/tensorflow/models/
RUN git checkout cf82a72480a41a62b4bbe0f1378d319f0d6f5d5c

# Compile protobuf configs
RUN (cd /home/tensorflow/models/research/ && protoc object_detection/protos/*.proto --python_out=.)
WORKDIR /home/tensorflow/models/research/

RUN cp object_detection/packages/tf2/setup.py ./
ENV PATH="/home/tensorflow/.local/bin:${PATH}"

# Workaround (For Tensorflow < 2.5.1): Remove tf-models-official dependency from object_detection, will install it manually.
RUN sed -i -e 's/^.*tf-models-official.*$//g' ./setup.py

RUN python -m pip install -U pip

# Workaround: Lock tensorflow and corresponding tf-models-official versions.
RUN python -m pip install tensorflow==2.3.0 tensorflow-text==2.3.0 tf-models-official==2.3.0
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
