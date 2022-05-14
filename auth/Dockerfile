FROM python:3.10.2 AS compile-image

ARG BASE_DIR=/popug
ARG USER=popug
ARG GROUP=popug

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    ssh \
    kafkacat \
    postgresql-client

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    DOCKER_CONTAINER=1 \
    TZ=Europe/Moscow

WORKDIR  ${BASE_DIR}
RUN adduser --uid 1000 --home ${BASE_DIR} --disabled-password --gecos "" ${USER} \
    && chown -hR ${USER}: ${BASE_DIR}

RUN pip install "poetry"

COPY ./pyproject.toml ./poetry.lock  ${BASE_DIR}

RUN poetry config virtualenvs.in-project true && \
    poetry config virtualenvs.create true && \
    poetry install --no-interaction --no-ansi

#=====================================================
FROM compile-image as dev

COPY --from=compile-image ${BASE_DIR}/.venv  ${BASE_DIR}/.venv

COPY docker-entrypoint.sh ${BASE_DIR}/docker-entrypoint.sh
RUN chmod +x  ${BASE_DIR}/docker-entrypoint.sh

ENV PATH="${BASE_DIR}/.venv/bin:$PATH"
USER ${USER}

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["help"]
