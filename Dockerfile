FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV APP_ENV=production
ENV SBOM_VARIANT=multi-ecosystem-v1

# Install OS packages (expanded list for SBOM richness)
RUN apt-get update && \
    apt-get install -y \
        nginx \
        curl \
        wget \
        openssl \
        ca-certificates \
        vim \
        net-tools \
        git \
        build-essential \
        python3 \
        python3-pip \
        nodejs \
        npm \
        cron && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install \
        requests==2.31.0 \
        flask==2.3.2

# Install Node.js dependencies
RUN npm install -g \
        express@4.18.2 \
        lodash@4.17.21

# Add a non-root user
RUN useradd -m appuser
USER appuser

# Add custom file (layer change for SBOM diff)
RUN echo "SBOM Variant Build - v1" > /home/appuser/version.txt

# Switch back to root for nginx
USER root

# Copy a sample config (optional SBOM variation)
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start services (nginx)
CMD ["nginx", "-g", "daemon off;"]
