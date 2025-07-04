/*
 * Rocket Data Logger for ESP32-S3 with GPS and Gyroscope
 * Collects: acceleration, gyroscope, pressure, altitude, temperature, latitude, longitude
 */

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <Adafruit_BMP280.h>
#include <SensorQMI8658.hpp>
#include <Adafruit_GPS.h>

// Pin definitions
#define TFT_CS        7
#define TFT_DC        39
#define TFT_RST       40
#define TFT_backlight 45
#define SPI_SCK       36
#define SPI_MISO      37
#define SPI_MOSI      35
#define I2C_SDA       42
#define I2C_SCL       41
#define BMP_Addr      0x77
#define QMI_Addr      0x6B

// Constants
const float SEA_LEVEL_PRESSURE_HPA = 1013.25;
const unsigned int MAX_DATA_POINTS = 2000;
const unsigned int SAMPLE_RATE_HZ = 10;
const unsigned int SAMPLE_INTERVAL_US = 1000000 / SAMPLE_RATE_HZ;
const float LAUNCH_THRESHOLD = 2.0; // 2G threshold

// Sensor objects
Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);
Adafruit_BMP280 bmp;
SensorQMI8658 qmi;
Adafruit_GPS gps(&Wire);

// Data structure for each sample
struct SensorData {
  unsigned long timestamp;
  float acceleration[3];
  float gyroscope[3];
  float pressure;
  float altitude;
  float temperature;
  float latitude;
  float longitude;
};

SensorData flightData[MAX_DATA_POINTS];
volatile unsigned int dataIndex = 0;
volatile bool launchDetected = false;
volatile bool recordingComplete = false;

// Initialize display
void initDisplay() {
  pinMode(TFT_backlight, OUTPUT);
  digitalWrite(TFT_backlight, HIGH);
  tft.init(135, 240);
  tft.setRotation(3);
  tft.fillScreen(ST77XX_BLACK);
  tft.setTextColor(ST77XX_WHITE);
  tft.setTextSize(2);
  tft.println("Rocket Logger");
}

// Initialize BMP280
void initBMP() {
  if (!bmp.begin(BMP_Addr)) {
    tft.setCursor(0, 20);
    tft.print("BMP not found");
    while (1);
  }
}

// Initialize QMI8658
void initQMI() {
  if (!qmi.begin(Wire, QMI_Addr, I2C_SDA, I2C_SCL)) {
    tft.setCursor(0, 40);
    tft.print("QMI not found");
    while (1);
  }
  qmi.enableGyroscope();
  qmi.enableAccelerometer();
}

// Initialize GPS
void initGPS() {
  gps.begin(0x10); // I2C address of PA1010D (verifica que sea correcto)
  gps.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  gps.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  delay(1000);
}

// Detect launch based on vertical acceleration
bool detectLaunch(float currentAccel) {
  static float baselineAccel = 1.0;
  return (currentAccel > baselineAccel * LAUNCH_THRESHOLD);
}

// Display current status on screen
void displayStatus() {
  tft.setTextSize(1);
  tft.setCursor(0, 100);
  float accX, accY, accZ;
  if (qmi.getAccelerometer(accX, accY, accZ)) {
    tft.printf("AccZ: %.2f g\n", accZ);
  }
  tft.printf("Alt: %.1f m\n", bmp.readAltitude(SEA_LEVEL_PRESSURE_HPA));
  tft.printf("Samples: %d/%d\n", dataIndex, MAX_DATA_POINTS);
}

// Output all recorded data as JSON
void dumpDataToSerial() {
  Serial.println("{\"flight_data\": [");
  for (int i = 0; i < dataIndex; i++) {
    Serial.printf("  {\"timestamp\": %lu,", flightData[i].timestamp);
    Serial.printf("\"acceleration\": {\"x\": %.3f, \"y\": %.3f, \"z\": %.3f},",
                 flightData[i].acceleration[0],
                 flightData[i].acceleration[1],
                 flightData[i].acceleration[2]);
    Serial.printf("\"gyroscope\": {\"x\": %.2f, \"y\": %.2f, \"z\": %.2f},",
                 flightData[i].gyroscope[0],
                 flightData[i].gyroscope[1],
                 flightData[i].gyroscope[2]);
    Serial.printf("\"pressure\": %.2f,", flightData[i].pressure);
    Serial.printf("\"altitude\": %.2f,", flightData[i].altitude);
    Serial.printf("\"temperature\": %.2f,", flightData[i].temperature);
    Serial.printf("\"latitude\": %.6f, \"longitude\": %.6f}", 
                 flightData[i].latitude, flightData[i].longitude);
    if (i < dataIndex - 1) Serial.println(",");
    else Serial.println();
  }
  Serial.println("]}");
}

// Setup function
void setup() {
  Serial.begin(115200);
  while (!Serial);
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI, TFT_CS);
  Wire.begin(I2C_SDA, I2C_SCL);
  initDisplay();
  initBMP();
  initQMI();
  initGPS();
  memset(flightData, 0, sizeof(flightData));
  tft.println("Ready");
  tft.println("Waiting for launch...");
}

// Main loop
void loop() {
  static unsigned long lastSampleTime = 0;
  unsigned long currentTime = micros();

  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_US && !recordingComplete) {
    lastSampleTime = currentTime;

    float accX, accY, accZ;
    float gx, gy, gz;
    if (!qmi.getAccelerometer(accX, accY, accZ)) return;
    if (!qmi.getGyroscope(gx, gy, gz)) return;

    gps.read();
    float lat = 0.0, lon = 0.0;
    if (gps.fix) {
      lat = gps.latitudeDegrees;
      lon = gps.longitudeDegrees;
    }

    float pressure = bmp.readPressure() / 100.0F;
    float altitude = bmp.readAltitude(SEA_LEVEL_PRESSURE_HPA);
    float temperature = bmp.readTemperature();

    if (!launchDetected && detectLaunch(accZ)) {
      launchDetected = true;
      dataIndex = 0;
      tft.fillScreen(ST77XX_BLACK);
      tft.setCursor(0, 0);
      tft.println("LAUNCH DETECTED!");
      Serial.println("LAUNCH DETECTED!");
    }

    if (launchDetected || dataIndex < MAX_DATA_POINTS) {
      if (dataIndex < MAX_DATA_POINTS) {
        flightData[dataIndex].timestamp = currentTime;
        flightData[dataIndex].acceleration[0] = accX;
        flightData[dataIndex].acceleration[1] = accY;
        flightData[dataIndex].acceleration[2] = accZ;
        flightData[dataIndex].gyroscope[0] = gx;
        flightData[dataIndex].gyroscope[1] = gy;
        flightData[dataIndex].gyroscope[2] = gz;
        flightData[dataIndex].pressure = pressure;
        flightData[dataIndex].altitude = altitude;
        flightData[dataIndex].temperature = temperature;
        flightData[dataIndex].latitude = lat;
        flightData[dataIndex].longitude = lon;
        dataIndex++;
      } else {
        recordingComplete = true;
        tft.fillScreen(ST77XX_BLACK);
        tft.setCursor(0, 0);
        tft.println("DATA FULL");
      }
    }
  }

  static unsigned long lastDisplayUpdate = 0;
  if (millis() - lastDisplayUpdate > 200) {
    lastDisplayUpdate = millis();
    displayStatus();
  }

  if (recordingComplete && !Serial.available()) {
    dumpDataToSerial();
    while (1);
  }


}
  