# vspu-notification-system

> <br>**Process stream of data in real time manner and trigger data-driven actions.**<br><br>

[![Python](https://img.shields.io/badge/Python-3.7-FFD43B?style=flat&logo=Python&logoColor=FFD43B)](https://www.python.org/)
[![Java](https://img.shields.io/badge/Java-1.8-ED8B00?style=flat&logo=Java&logoColor=white)](https://java.com/)
[![Apache_Kafka](https://img.shields.io/badge/Apache_Kafka-2.8-231F20?style=flat&logo=Apache-Kafka&logoColor=white)](https://kafka.apache.org/)
[![Apache_Maven](https://img.shields.io/badge/Apache_Maven-4.0-C71A36?style=flat&logo=Apache-Maven&logoColor=white)](https://maven.apache.org/)
[![Redis](https://img.shields.io/badge/Redis-6.2-D82C20?style=flat&logo=Redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-6.2-384d54?style=flat&logo=Docker&logoColor=0db7ed)](https://www.docker.com/)
![IOS](https://img.shields.io/badge/iOS-000000?style=flat&logo=ios&logoColor=white)

---

# Overview:
This is notification system for Video Stream Processing Unit (VSPU).<br>
The purpose is to build solution that based on any **data source** is able to **process** received data and finally trigger custom **actions**.
Each part is build in such way that custom data sources, data processors and actions may be implemented.
Here You have provided few examples.

## Action system
- **Live plot (matplotlib):**<br>
    Plots stream of incoming data provided by callable object.<br>
    Possible to set limit value (both static and dynamic).<br>
    Based on matplotlib.<br>
- **Email notificaiton (Gmail SMTP):**<br>
    Send email based on incoming data stream and either dynamic or static limit value.<br>
    System sources data from Kafka topic and compare to current limit.<br>
    If data value exceeds limit value, sends email.<br>
- **Database for IPC**:<br>
    Redis database for quick inter process communication.<br>
    Modifying vaiables by external user made available.<br>
    This component is optional.<br>
## Data  processor (Kafka Streams)
- **SumTheAge**:<br>
    Kafka Streams and Java application.<br>
    Recieves data from one Kafka topic, process and pass to another Kafka topic.<br>
    Values are filtered and then sum off all `age` key is evaluated in real time as data is coming.<br> 
## Data source
- **Mockup script**:<br>
    Python script that pushes data to Kafka topic. Data is flat JSON type in format of (string_key, JSON_value).
      
## Additional
- **Kafka CLI consumer**:<br>
    To visulize data flow through Kafka server.

---

# High-level notification system architecture
<p align="center">
  <img src="visualizations/high-level-notification-system-architecture/high-level-notification-system-architecture.png"
       alt="visualization of high-level-notification-system-architecture"
       width=100%>
</p>

---

# Runtime visualization
<p align="center">
  <img src="visualizations/screen-record.gif"
       alt="screen-record.gif"
       width=100%>
</p>

---

# Getting Started

## 1) Prepare Kafka Server
> **_NOTE:_** It is assumed that Kafka Server is up and running. Also it's bin directory added to path

#### a) Create topic: example.001
```bash
kafka-topics.sh --zookeeper 127.0.0.1:2181 \
--topic example.001 \
--create \
--partitions 1 \
--replication-factor 1
```

#### b) Topic: example.001.age.sum
```bash
kafka-topics.sh --zookeeper 127.0.0.1:2181 \
--topic example.001.age.sum \
--create \
--partitions 1 \
--replication-factor 1
```

## 2) Prepare Redis database

#### a) Using Docker
```bash
docker run -d --name redis-db -p 6379:6379 redis redis-server --requirepass "password"
```
> **_NOTE:_** To manipulate Redis data (e.g. change value for 'limit' key to 150):
> ```
> docker exec -it redis-db bash
> redis-cli -a password
> SET limit 150
> ```

## 3) Clone repository
```bash
git clone https://github.com/patryklaskowski/vspu-notification-system.git &&
cd vspu-notification-system
```

## 4) Run action system
### a). Kafka CLI Consumer (topic: example.001.age.sum, group: example.001.age.sum.vis.app)
```bash
kafka-console-consumer.sh --bootstrap-server 127.0.0.1:9092 \
--topic example.001.age.sum \
--group example.001.age.sum.vis.app \
--from-beginning \
--formatter kafka.tools.DefaultMessageFormatter \
--property print.key=true \
--property print.value=true \
--property key.deserializer=org.apache.kafka.common.serialization.StringDeserializer \
--property value.deserializer=org.apache.kafka.common.serialization.IntegerDeserializer
```

## 5) Run data processor
#### a) ...
```bash
```

## 6) Run data producer
#### a) Kafka CLI Consumer (topic:example.001, group: example.001.vis.app)
```bash
kafka-console-consumer.sh --bootstrap-server 127.0.0.1:9092 \
--topic example.001 \
--group example.001.vis.app \
--from-beginning \
--formatter kafka.tools.DefaultMessageFormatter \
--property print.key=true \
--property print.value=true \
--property key.deserializer=org.apache.kafka.common.serialization.StringDeserializer \
--property value.deserializer=org.apache.kafka.common.serialization.StringDeserializer
```

---


TODO





---
## Run software



> **_NOTE:_**  To reset group offset to very beginning
> ```bash
> kafka-consumer-groups.sh --bootstrap-server 127.0.0.1:9092 \
> --topic example.001 \
> --group example.001.vis.app \
> --reset-offsets --to-earliest \
> --execute
> ```

### 2. "sumTheAge" Kafka Streams Application
```bash
java -jar kafka-streams/sumTheAge-kafka-streams/target/sumTheAge-kafka-streams-1.0-jar-with-dependencies.jar
```



> **_NOTE:_**  To reset group offset to very beginning
> ```bash
> kafka-consumer-groups.sh --bootstrap-server 127.0.0.1:9092 \
> --topic example.001.age.sum \
> --group example.001.age.sum.vis.app \
> --reset-offsets --to-earliest \
> --execute
> ```

### 4. Live Plot Python Consumer
```bash
cd python-kafka-consumer &&
python3.7 -m venv env &&
source env/bin/activate &&
python3 -m pip install -r requirements.txt &&
python3 live_plot_consumer.py --limit 10000 --window 50 --interval 300
```

### 5. Email Notification Python Consumer
```bash
```

### 6. Python Data Producer Mockup
```bash
cd python-kafka-producer-mockup &&
python3.7 -m venv env &&
source env/bin/activate &&
python3 -m pip install -r requirements.txt &&
python3 kafka-python-sumTheAge-producer.py --min -5 --max 7 --sleep 0.2 -n 200
```



---

