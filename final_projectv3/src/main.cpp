#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <PubSubClient.h>

#define SS_PIN 5
#define RST_PIN 22
#define RELAY_PIN 4

MFRC522 mfrc522(SS_PIN, RST_PIN);

const char* ssid = "IoTPrivate";
const char* password = "iotprivate303";
const char* mqtt_server = "13.50.238.148";

WiFiClient espClient;
PubSubClient client(espClient);
char msg[50];

// Function prototypes
void setup_wifi();
void callback(char* topic, byte* payload, unsigned int length);
void reconnect();

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);

  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  reconnect();
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  Serial.println(message);

  if (message == "TRIGGER_RELAY") {
    Serial.println("Triggering relay for 10 seconds");
    digitalWrite(RELAY_PIN, HIGH);
    delay(10000);  // Trigger the relay for 10 seconds
    digitalWrite(RELAY_PIN, LOW);
    Serial.println("Relay turned off");
  } else {
    Serial.println("Received unknown message");
  }
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
      // Once connected, resubscribe
      client.subscribe("esp32/relay");
      Serial.println("Subscribed to topic: esp32/relay");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    delay(50);
    return;
  }

  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }

  uid.toUpperCase();
  uid.toCharArray(msg, 50);
  Serial.print("UID:");
  Serial.println(uid);
  client.publish("esp32/uid", msg);
  Serial.println(msg);

  delay(1000);
}
