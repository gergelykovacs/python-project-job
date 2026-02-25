FROM python:3.14-slim-bookworm

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout/stderr (crucial for Docker logs)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

USER root

RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -r nonroot_usr && useradd -r -g nonroot_usr nonroot_usr

COPY pyproject.toml .
COPY requirements.txt .

#RUN pip config set global.index-url https://nexus.mycompany.com/repository/pypi-packages/simple
#RUN pip config set global.trusted-host nexus.mycompany.com

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN pip install --no-cache-dir -e .

RUN chown -R nonroot_usr:nonroot_usr /app

RUN mkdir -p /home/nonroot_usr && chown -R nonroot_usr:nonroot_usr /home/nonroot_usr

USER nonroot_usr

ENV SOURCE_DATA_PATH="/app/source_data.csv"
ENV DB_CONN="sqlite:////app/production.db"

CMD ["python3", "-m", "my_job.main"]