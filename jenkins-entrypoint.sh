#!/bin/bash
set -e

DOCKER_SOCKET=/var/run/docker.sock

if [[ -S "${DOCKER_SOCKET}" ]]; then
    DOCKER_GID=$(stat -c '%g' "${DOCKER_SOCKET}")
    DOCKER_GROUP=$(getent group "${DOCKER_GID}" | cut -d: -f1)

    if [[ -z "${DOCKER_GROUP}" ]]; then
        groupadd -g "${DOCKER_GID}" docker
        DOCKER_GROUP=docker
    fi

    usermod -aG "${DOCKER_GROUP}" jenkins
fi

exec /usr/bin/tini -- /usr/local/bin/jenkins.sh
