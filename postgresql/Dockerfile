FROM postgres:16

ARG AGE_VERSION=release/PG16/1.6.0
ARG PGVECTOR_VERSION=v0.8.2

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    git \
    flex \
    bison \
    libreadline-dev \
    zlib1g-dev \
    postgresql-server-dev-16 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Install Apache AGE
RUN git clone --branch ${AGE_VERSION} --depth 1 https://github.com/apache/age.git \
    && cd age \
    && make PG_CONFIG=/usr/lib/postgresql/16/bin/pg_config install \
    && cd /tmp \
    && rm -rf age

# Install pgvector
RUN git clone --branch ${PGVECTOR_VERSION} --depth 1 https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make PG_CONFIG=/usr/lib/postgresql/16/bin/pg_config \
    && make PG_CONFIG=/usr/lib/postgresql/16/bin/pg_config install \
    && cd /tmp \
    && rm -rf pgvector

# Preload AGE at server startup
RUN echo "shared_preload_libraries = 'age'" >> /usr/share/postgresql/postgresql.conf.sample

WORKDIR /