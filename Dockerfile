FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
        nginx \
        curl \
        openssl \
        ca-certificates \
        python3 \
        python3-pip \
        vim && \
    pip3 install requests==2.31.0 && \
    rm -rf /var/lib/apt/lists/*

RUN echo "sbom-variant-1" > /opt/version.txt

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
