#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// Pins D3,D4,D8 have special boot method, so device
// cannot be set up with high state on any of these.
// #define PIN_D8 15
#define PIN_D7 13
#define PIN_D6 12

const char* WiFi_NAME = "";
const char* PASSWORD = "";
const String HOST = "";
const int PORT = 7216;
// in seconds
const int REPORT_DELAY_TIME = 120;
// in seconds; if < 0 then no reconnect
const int RECONNECT_DELAY_TIME = -1; //30;

void setup() {
  pinMode(PIN_D6, OUTPUT);
  pinMode(PIN_D7, INPUT_PULLUP);
  Serial.begin(115200);
  WiFi.begin(WiFi_NAME, PASSWORD);
 
  delay(100);
  Serial.print("\nConnecting with WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.print("\nConnected with ");
  Serial.println(WiFi_NAME); 
}
  
void loop() {
  WiFiClient wifi_client;
  Serial.println("\nConnecting with Server...");
  while (!wifi_client.connect(HOST, PORT)) {
    Serial.print("Connection to ");
    Serial.print(HOST);
    Serial.println(" FAILED");
    if (RECONNECT_DELAY_TIME < 0)
      return;
    delay(RECONNECT_DELAY_TIME*1000);
  }
  Serial.print("Successfully connected with ");
  Serial.println(HOST);
  HTTPClient http;
  bool b = http.begin(wifi_client, HOST, PORT, "/post/", 0);
  digitalWrite(PIN_D6, LOW);
  bool isClosed = digitalRead(PIN_D7);
  http.addHeader("Content-Type", "text/plain");
  http.addHeader("Content-Length", "1");
  auto httpCode = http.POST(String(isClosed));
  Serial.println(httpCode);
  String payload = http.getString();
  Serial.println(payload);
  http.end();
  // delay(REPORT_DELAY_TIME*1000);
  // For deepSleep to work pin D0 musi be connected to RST
  // After deepSleep ESP will be reset
  ESP.deepSleep(REPORT_DELAY_TIME*1000000);
}
