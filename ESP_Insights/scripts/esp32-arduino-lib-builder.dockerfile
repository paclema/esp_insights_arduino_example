# Create a docker image from this dockerfile with: 
# docker build -t esp32-arduino-lib-builder .
# or:
# docker build --tag esp32-arduino-lib-builder --file ./scripts/esp32-arduino-lib-builder.dockerfile .

# Run the docker image in a container with: 
# docker run -it --name esp32-arduino-lib-builder-container esp32-arduino-lib-builder

FROM espressif/idf:release-v4.4
RUN apt-get update
RUN apt-get install -y jq
RUN pip install --upgrade pip
RUN git clone --branch esp_insights https://github.com/paclema/esp32-arduino-lib-builder.git

WORKDIR /esp32-arduino-lib-builder
RUN ls -ll
RUN git checkout esp_insights

# RUN ./build.sh -A master -t esp32


# To get into a Docker container's shell:
# docker exec -it esp32-arduino-lib-builder-container bash