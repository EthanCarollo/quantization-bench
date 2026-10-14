FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 TMPDIR=/tmp
WORKDIR /sandbox
COPY requirements-livecodebench-evaluator.txt /sandbox/requirements.txt
RUN pip install --no-cache-dir --disable-pip-version-check -r /sandbox/requirements.txt
COPY vendor/livecodebench/testing_util.py /sandbox/testing_util.py
COPY docker/livecodebench/evaluate_one.py /sandbox/evaluate_one.py
USER 65534:65534
ENTRYPOINT ["python", "/sandbox/evaluate_one.py"]
