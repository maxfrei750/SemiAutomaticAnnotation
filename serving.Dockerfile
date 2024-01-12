# TODO: Support GPU (also in client Dockerfile).
ARG TENSORFLOW_VERSION="2.6.0"

# Use multi-stage build
FROM tensorflow/serving:${TENSORFLOW_VERSION} as builder
ARG DEBIAN_FRONTEND=noninteractive

# Install unzip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    unzip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /models

# Download DeepMARC model
ADD https://storage.googleapis.com/tf_model_garden/vision/deepmac_maskrcnn/deepmarc_spinenet.zip .
RUN unzip deepmarc_spinenet.zip && \
    rm deepmarc_spinenet.zip && \
    mkdir -p deepmarc/1 && \
    mv deepmarc_spinenet/* deepmarc/1/ && \
    rmdir deepmarc_spinenet

# Download DeepMAC model
ADD http://download.tensorflow.org/models/object_detection/tf2/20210329/deepmac_1024x1024_coco17.tar.gz .
RUN tar --strip-components=1 -xvf deepmac_1024x1024_coco17.tar.gz deepmac_1024x1024_coco17/saved_model && \
    rm deepmac_1024x1024_coco17.tar.gz && \
    mkdir -p deepmac/1 && \
    mv saved_model/* deepmac/1/ && \
    rmdir saved_model

# Final stage
FROM tensorflow/serving:${TENSORFLOW_VERSION}
ARG DEBIAN_FRONTEND=noninteractive

COPY --from=builder /models /models

# Add models.config to allow serving multiple models
ADD models.config /models/models.config
RUN printf '#!/bin/bash\ntensorflow_model_server --port=8500 --rest_api_port=8501 --model_name=${MODEL_NAME} --model_base_path=${MODEL_BASE_PATH}/${MODEL_NAME} --model_config_file=${MODEL_CONFIG_FILE} "$@"' > usr/bin/tf_serving_entrypoint.sh
ENV MODEL_CONFIG_FILE=/models/models.config

