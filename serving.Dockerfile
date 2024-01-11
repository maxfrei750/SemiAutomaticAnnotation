# TODO: Support GPU (also in client Dockerfile).
ARG TENSORFLOW_VERSION="2.6.0"

# Use multi-stage build
FROM tensorflow/serving:${TENSORFLOW_VERSION} as builder
ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /models
ADD http://download.tensorflow.org/models/object_detection/tf2/20210329/deepmac_1024x1024_coco17.tar.gz .
RUN tar --strip-components=1 -xvf deepmac_1024x1024_coco17.tar.gz deepmac_1024x1024_coco17/saved_model && \
    rm deepmac_1024x1024_coco17.tar.gz && \
    mkdir -p deepmac/1 && \
    mv saved_model/* deepmac/1/ && \
    rmdir saved_model

# Final stage
FROM tensorflow/serving:${TENSORFLOW_VERSION}
COPY --from=builder /models/deepmac /models/deepmac
