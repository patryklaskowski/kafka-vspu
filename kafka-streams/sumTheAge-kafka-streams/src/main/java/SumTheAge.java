import com.google.gson.JsonParser;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.kstream.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Properties;

public class SumTheAge {

    final static String BOOTSTRAP_SERVERS = "149.81.197.180:9092";
    final static String GROUP_ID = "sum-lambda-example";
    final static String UNIQUE_CLIENT_ID = "sum-lambda-example-client-001";
    final static String INPUT_TOPIC = "example.001";
    final static String OUTPUT_TOPIC = "example.001.age.sum";

    // In order to overwrite default (properties) serialization / deserialization
    final static Serde<String> stringSerde = Serdes.String();
    final static Serde<Integer> integerSerde = Serdes.Integer();

    public static void main(String[] args) {
        System.out.println("Welcome in SumTheAge Kafka Streams Solution!");

        Logger logger = LoggerFactory.getLogger(SumTheAge.class.getName());

        System.out.println("Creating properties...");
        final Properties properties = createProperties();

        System.out.println("Creating topology...");
        // For testing purposes: getTopology is not static anymore, just public
        SumTheAge sumTheAge = new SumTheAge();
        final Topology topology = sumTheAge.getTopology();

        // Create stream
        System.out.println("Creating Kafka Streams client...");
        final KafkaStreams streams = new KafkaStreams(topology, properties);

        // Print topology
        System.out.println("\nSTREAMS: " + streams.toString() + "\n");

        // Clean local state prior to starting the processing topology. Not in production :)
        System.out.println("Cleaning up local state...");
        streams.cleanUp();

        // Start stream
        System.out.println("Firing stream...");
        streams.start();

        // Add shutdown hook to gracefully close Kafka Streams
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Shutting down...");
            streams.close();
            System.out.println(">> Done <<");
            logger.info(">> Done <<");
        }));
    }

    static Properties createProperties() {
        final Properties properties = new Properties();

        properties.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);

        properties.put(StreamsConfig.APPLICATION_ID_CONFIG, GROUP_ID);
        properties.put(StreamsConfig.CLIENT_ID_CONFIG, UNIQUE_CLIENT_ID);

        properties.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        // Serialization / Deserialization default configs
        properties.setProperty(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
        properties.setProperty(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());

        // Exactly once property Kafka -> Kafka Streams -> Kafka
        // Results are published in transactions - may cause small latency
        properties.setProperty(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE);

        return properties;
    }

    public Topology getTopology() {
        final StreamsBuilder builder = new StreamsBuilder();
        // Values are string type JSON format
        final KStream<String, String> input = builder.stream(INPUT_TOPIC);

        final KTable<String, Integer> sumOfAge = input
                // Only even IDs
                .filter((key, value) -> extractId(value) % 2 == 0)
                // Extract age value AS AN INTEGER
                .mapValues(val -> extractAge(val))
                // Make all the keys "sum"
                .selectKey((key, val) -> "sum")
                // Useful for debugging (works only with KStream
                .peek((key, val) -> System.out.println("|__/ [peek before groupByKey] Key: " + key + ", Val: " + val + "."))
                // groupByKey is one of operations that require Serdes info (if data type changed)
                // https://docs.confluent.io/platform/current/streams/developer-guide/datatypes.html
                .groupByKey(Grouped.with(Serdes.String(), Serdes.Integer()))
                // Reduce within group(s)
                .reduce((acc, val) -> {
                    System.out.println("|__/ [peek reduce KTable] acc: " + acc + " => val:" + val);
                    return acc + val;
                })
                .filter((key, value) -> {
                    System.out.println("|__/ [peek FINAL KTable] key" + key + " => " + value);
                    return true;
                });

        sumOfAge.toStream().to(OUTPUT_TOPIC, Produced.valueSerde(Serdes.Integer()));  // or (if want to overwrite both): Produced.with(stringSerde, integerSerde));

        return builder.build();
    }

    private static final JsonParser jsonParser = new JsonParser();

    public static Integer extractAge(String value) {
        // Using gson library
        // value = {"name": "Patryk_3", "surname": "Laskowski_3", "age": 17}
        Integer age = jsonParser.parse(value)
                .getAsJsonObject()
                .get("age")
                .getAsInt();

        System.out.println("|__/ Extracted age: " + age);

        return age;
    }

    public static String result;
    public static Integer extractId(String value) {
        // Using gson library
        // value = {"name": "Patryk_3", "surname": "Laskowski_3", "age": 17}
        String number = jsonParser.parse(value)
                .getAsJsonObject()
                .get("name")
                .getAsString()
                .replaceAll("[^0-9]", "");


        if (Integer.parseInt(number) % 2 == 0){
            result = "EVEN";
        } else {
            result = "ODD, filter out!";
        }

        System.out.println("\nFrom value: " + value + "\n" +
                            "|__/ Extracted id: " + number + " --> " + result);

        return Integer.parseInt(number);
    }
}
