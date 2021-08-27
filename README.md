# vspu-notification-system
Notification system for Video Stream Processing Unit<br><br>
<b>Process data in real time to finally trigger data-driven actions.</b>


[![Python](https://img.shields.io/badge/Python-3.7-FFD43B?style=flat&logo=Python&logoColor=FFD43B)](https://www.python.org/)
[![Java](https://img.shields.io/badge/Java-1.8-ED8B00?style=flat&logo=Java&logoColor=white)](https://java.com/)
[![Apache_Kafka](https://img.shields.io/badge/Apache_Kafka-2.8-231F20?style=flat&logo=Apache-Kafka&logoColor=white)](https://kafka.apache.org/)
[![Apache_Maven](https://img.shields.io/badge/Apache_Maven-4.0-C71A36?style=flat&logo=Apache-Maven&logoColor=white)](https://maven.apache.org/)
[![Redis](https://img.shields.io/badge/Redis-6.2-D82C20?style=flat&logo=Redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-6.2-384d54?style=flat&logo=Docker&logoColor=0db7ed)](https://www.docker.com/)
![IOS](https://img.shields.io/badge/iOS-000000?style=flat&logo=ios&logoColor=white)

---

## Overview:
Architecture has 6 components:
1. Kafka CLI Consumer<br>- Connected to raw data topic "example.001"
2. **"sumTheAge" Kafka Streams Application**<br>- Process the data from topic "example.001"
3. Kafka CLI Consumer<br>- Connected to processed data topic "example.001.age.sum"
4. **Live Plot Python Consumer**<br>- Connected to processed data topic "example.001.age.sum"
5. **Email/SMS Notification Python Consumer**<br>- Connected to processed data topic "example.001.age.sum"
6. **Python Data Producer Mockup**<br>- Simulates input data

List suggests the order to run the software.<br>
**Bolded** elements are crucial workflow components.<br>
Kafka CLI Consumers are optional elements set for visualizational purpose.<br>

<p align="center">
  <img src="visualizations/high-level-notification-system-architecture/high-level-notification-system-architecture.png"
       alt="visualization of high-level-notification-system-architecture"
       width=100%>
</p>

---

## Prepare Environment

### Clone repository
```bash
git clone https://github.com/patryklaskowski/kafka-vspu.git &&
cd kafka-vspu
```

### Create Kafka topics using Kafka CLI
> **_NOTE:_**  Assumed that Kafka is installed and it's bin directory is added to path

#### Topic: example.001
```bash
kafka-topics.sh --zookeeper 127.0.0.1:2181 \
--topic example.001 \
--create \
--partitions 1 \
--replication-factor 1
```

#### Topic: example.001.age.sum
```bash
kafka-topics.sh --zookeeper 127.0.0.1:2181 \
--topic example.001.age.sum \
--create \
--partitions 1 \
--replication-factor 1
```

---
## Run software

### 1. Kafka CLI example.001 Consumer (group: example.001.vis.app)
```bash
kafka-console-consumer.sh --bootstrap-server 149.81.197.180:9092 \
--topic example.001 \
--group example.001.vis.app \
--from-beginning \
--formatter kafka.tools.DefaultMessageFormatter \
--property print.key=true \
--property print.value=true \
--property key.deserializer=org.apache.kafka.common.serialization.StringDeserializer \
--property value.deserializer=org.apache.kafka.common.serialization.StringDeserializer
```

> **_NOTE:_**  To reset group offset to very beginning
> ```bash
> kafka-consumer-groups.sh --bootstrap-server 149.81.197.180:9092 \
> --topic example.001 \
> --group example.001.vis.app \
> --reset-offsets --to-earliest \
> --execute
> ```

### 2. "sumTheAge" Kafka Streams Application
```bash
java -jar kafka-streams/sumTheAge-kafka-streams/target/sumTheAge-kafka-streams-1.0-jar-with-dependencies.jar
```

### 3. Kafka CLI example.001.age.sum Consumer (group: example.001.age.sum.vis.app)
```bash
kafka-console-consumer.sh --bootstrap-server 149.81.197.180:9092 \
--topic example.001.age.sum \
--group example.001.age.sum.vis.app \
--from-beginning \
--formatter kafka.tools.DefaultMessageFormatter \
--property print.key=true \
--property print.value=true \
--property key.deserializer=org.apache.kafka.common.serialization.StringDeserializer \
--property value.deserializer=org.apache.kafka.common.serialization.IntegerDeserializer
```

> **_NOTE:_**  To reset group offset to very beginning
> ```bash
> kafka-consumer-groups.sh --bootstrap-server 149.81.197.180:9092 \
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

<p align="center">
  <img src="visualizations/screen-record.gif"
       alt="screen-record.gif"
       width=90%>
</p>

---

