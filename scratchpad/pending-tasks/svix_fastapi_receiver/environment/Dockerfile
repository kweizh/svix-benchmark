FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user/svix_project && chmod 0755 /home/user /home/user/svix_project

LABEL Author="any-task-builder"
LABEL Description="Environment for building a FastAPI webhook receiver with Svix."

# Container contents:
#   - python3, pip3 installed.
#   - /home/user/svix_project — empty directory for the project.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
