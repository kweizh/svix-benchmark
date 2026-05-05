FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Node.js project with svix SDK installed for testing webhook transformations."

RUN mkdir -p /home/user/svix-project && \
    cd /home/user/svix-project && \
    npm init -y && \
    npm install svix

# Container contents:
#   - Node.js v24 installed
#   - /home/user/svix-project  — Node.js project directory
#   - svix npm package installed in /home/user/svix-project/node_modules

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]