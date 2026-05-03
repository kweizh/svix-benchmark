FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm i -g @nestjs/cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="NestJS project environment for Svix raw body parsing task."

RUN cd /home/user && \
    nest new svix-nestjs-app --package-manager npm --skip-git && \
    cd svix-nestjs-app && \
    npm install

# Container contents:
#   - always required libs: curl ca-certificates git python3 python3-pip python3-pytest bash
#   - Node.js v24 for the NestJS task environment
#   - /home/user/svix-nestjs-app: Initialized NestJS project

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]