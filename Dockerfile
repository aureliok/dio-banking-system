FROM python:3.12-slim AS build

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pytest

FROM python:3.12-slim AS production

WORKDIR /app
COPY --from=build /app .

RUN pip install uvicorn

EXPOSE 8000

CMD ["uvicorn", "run:application", "--host", "127.0.0.1", "--port", "8000"]