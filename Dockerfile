FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install packages that reliably generate CVEs
RUN apt-get update && \
    apt-get install -y \
        nginx \
        curl \
        openssl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Expose NGINX default port
EXPOSE 80

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
