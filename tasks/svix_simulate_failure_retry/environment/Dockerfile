FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash xz-utils && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install svix Python SDK for the verifier
RUN pip3 install --break-system-packages svix==1.92.2

# Install svix CLI
RUN curl -fsSL https://github.com/svix/svix-webhooks/releases/download/v1.92.2/svix-cli-x86_64-unknown-linux-musl.tar.xz | tar -xJ -C /usr/local/bin --strip-components=1 svix-cli-x86_64-unknown-linux-musl/svix && \
    chmod +x /usr/local/bin/svix

RUN mkdir -p /home/user/project && \
    cd /home/user/project && \
    npm init -y && \
    chmod -R 0777 /home/user/project

LABEL Author="any-task-builder"
LABEL Description="Node.js 24 environment with Svix CLI installed and a basic project initialized."

# Container contents:
#   - Node.js 24 and npm
#   - Python 3 with pytest and svix SDK for verification
#   - svix CLI installed to /usr/local/bin/svix
#   - /home/user/project initialized with package.json

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
