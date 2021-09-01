FROM java:8

WORKDIR /kafka-streams

COPY . .

ENTRYPOINT ["java", "-jar", "sumTheAge-kafka-streams/target/sumTheAge-kafka-streams-1.0-jar-with-dependencies.jar"]
