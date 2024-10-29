FROM python:3.12-slim


WORKDIR /app
COPY . . 

# Install system dependencies, including libgomp1 for LightGBM
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

EXPOSE 5001

CMD [ "python", "app.py" ]