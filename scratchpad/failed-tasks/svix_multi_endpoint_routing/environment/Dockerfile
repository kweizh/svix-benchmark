FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g svix-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Node.js environment with svix-cli installed for testing webhook routing."

RUN mkdir -p /home/user/svix_project

# Container contents:
#   - Node.js v24 and npm installed.
#   - svix-cli installed globally.
#   - /home/user/svix_project - empty directory for the project.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]