FROM tensorflow/serving:2.6.0

WORKDIR /models
ADD http://download.tensorflow.org/models/object_detection/tf2/20210329/deepmac_1024x1024_coco17.tar.gz .
RUN tar --strip-components=1 -xvf deepmac_1024x1024_coco17.tar.gz deepmac_1024x1024_coco17/saved_model
RUN rm deepmac_1024x1024_coco17.tar.gz && \
    mkdir -p deepmac/1 && \
    mv saved_model/* deepmac/1/ && \
    rmdir saved_model
