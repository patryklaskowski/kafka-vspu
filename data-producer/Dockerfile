FROM python:3.7

WORKDIR /data-producer

COPY . .

RUN pip install -r requirements.txt  # --no-cache-dir

ENTRYPOINT ["python", "./sumTheAge-mockup.py"]
