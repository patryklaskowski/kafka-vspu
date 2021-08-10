import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.IntegerDeserializer;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.TopologyTestDriver;
import org.apache.kafka.streams.test.ConsumerRecordFactory;
import org.apache.kafka.streams.test.OutputVerifier;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.util.Properties;

import static org.junit.Assert.assertEquals;

public class SumTheAgeTest {

    final static String INPUT_TOPIC = "example.001";
    final static String OUTPUT_TOPIC = "example.001.age.sum";

    TopologyTestDriver testDriver;
    StringSerializer stringSerializer = new StringSerializer();
    ConsumerRecordFactory<String, String> recordFactory = new ConsumerRecordFactory<>(stringSerializer, stringSerializer);

    @Before
    public void setUpTopologyTestDriver(){
        //
        // Setup
        //
        Properties properties = new Properties();

        properties.setProperty(StreamsConfig.APPLICATION_ID_CONFIG, "test");
        properties.setProperty(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "doesNotMatter:1306");

        // Serialization / Deserialization default configs
        properties.setProperty(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());
        properties.setProperty(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass().getName());

        SumTheAge sumTheAge = new SumTheAge();
        Topology topology = sumTheAge.getTopology();
        testDriver = new TopologyTestDriver(topology, properties);
    }

    @After
    public void closeTestDriver(){
        //
        // Tear down
        // -> Otherwise information will be preserved.
        testDriver.close();
    }

    public void pushNewInputRecord(String key, String value){
        testDriver.pipeInput(recordFactory.create(INPUT_TOPIC, key, value));
    }

    public ProducerRecord<String, Integer> readOutput(){
        return testDriver.readOutput(OUTPUT_TOPIC, new StringDeserializer(), new IntegerDeserializer());
    }

    @Test
    public void dummyTest(){
        assertEquals("dummy", "dummy");
    }

    @Test
    public void testSumTheAge(){
        String firstKey = "camera_001";
        String firstValue = "{\"name\": \"Patryk_2\", \"surname\": \"Laskowski_2\", \"age\": 25}";
        pushNewInputRecord(firstKey, firstValue);

        OutputVerifier.compareKeyValue(readOutput(), "sum", 25);
        assertEquals(readOutput(), null);

    }

    @Test
    public void assertTakesOnlyEvenId(){
        String key = "camera_001";

        // This value should be filtered - not even taken under consideration
        String firstValue = "{\"name\": \"Patryk_1\", \"surname\": \"Laskowski_1\", \"age\": 30}";
        pushNewInputRecord(key, firstValue);
        String secondValue = "{\"name\": \"Patryk_2\", \"surname\": \"Laskowski_2\", \"age\": 10}";
        pushNewInputRecord(key, secondValue);

        OutputVerifier.compareKeyValue(readOutput(), "sum", 10);
        assertEquals(readOutput(), null);
    }
}
