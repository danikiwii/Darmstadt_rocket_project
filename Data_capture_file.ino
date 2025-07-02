/*
 * Rocket Data Logger for ESP32-S3
 * Complete fixed version with all function implementations
 */

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <Adafruit_BMP280.h>
#include <SensorQMI8658.hpp>

// Pin Definitions
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
const unsigned int MAX_DATA_POINTS = 2000;    // Reduced for memory
const unsigned int SAMPLE_RATE_HZ = 10;
const unsigned int SAMPLE_INTERVAL_US = 1000000 / SAMPLE_RATE_HZ;
const float LAUNCH_THRESHOLD = 2.0;          // 2G threshold for launch detection

// Sensor Objects
Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);
Adafruit_BMP280 bmp;
SensorQMI8658 qmi;

// Data Structure
struct SensorData {
  unsigned long timestamp;
  float acceleration[3]; // x, y, z in g
  float pressure;       // in hPa
  float altitude;       // in meters
  float temperature;    // in °C
};

// Data Storage
SensorData flightData[MAX_DATA_POINTS];
volatile unsigned int dataIndex = 0;
volatile bool launchDetected = false;
volatile bool recordingComplete = false;

// Function Implementations
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

void initBMP() {
  if (!bmp.begin(BMP_Addr)) {
    tft.setCursor(0, 20);
    tft.print("BMP not found");
    Serial.println("BMP not found");
    while (1);
  }
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                  Adafruit_BMP280::SAMPLING_X2,
                  Adafruit_BMP280::SAMPLING_X16,
                  Adafruit_BMP280::FILTER_X16,
                  Adafruit_BMP280::STANDBY_MS_500);
}

void initQMI() {
  if (!qmi.begin(Wire, QMI_Addr, I2C_SDA, I2C_SCL)) {
    tft.setCursor(0, 20);
    tft.print("QMI not found");
    Serial.println("QMI not found");
    while (1);
  }
  qmi.enableGyroscope();
  qmi.enableAccelerometer();
  qmi.configAccelerometer(
    SensorQMI8658::ACC_RANGE_8G,
    SensorQMI8658::ACC_ODR_1000Hz,
    SensorQMI8658::LPF_MODE_0);
  qmi.configGyroscope(
    SensorQMI8658::GYR_RANGE_512DPS,
    SensorQMI8658::GYR_ODR_896_8Hz,
    SensorQMI8658::LPF_MODE_3);
}

bool detectLaunch(float currentAccel) {
  static float baselineAccel = 1.0; // Normal gravity
  return (currentAccel > baselineAccel * LAUNCH_THRESHOLD);
}

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

void dumpDataToSerial() {
  Serial.println("BEGIN_DATA_DUMP");
  Serial.println("Timestamp(us),AccX(g),AccY(g),AccZ(g),Pressure(hPa),Altitude(m),Temp(C)");
  
  for (int i = 0; i < dataIndex; i++) {
    Serial.printf("%lu,%.3f,%.3f,%.3f,%.2f,%.2f,%.2f\n",
                 flightData[i].timestamp,
                 flightData[i].acceleration[0],
                 flightData[i].acceleration[1],
                 flightData[i].acceleration[2],
                 flightData[i].pressure,
                 flightData[i].altitude,
                 flightData[i].temperature);
  }
  
  Serial.println("END_DATA_DUMP");
}

void setup() {
  Serial.begin(115200);
  while (!Serial);
  
  SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI, TFT_CS);
  Wire.begin(I2C_SDA, I2C_SCL);

  initDisplay();
  initBMP();
  initQMI();

  memset(flightData, 0, sizeof(flightData));
  tft.println("Ready");
  tft.println("Waiting for launch...");
  Serial.println("Rocket Data Logger Ready");
}

void loop() {
  static unsigned long lastSampleTime = 0;
  unsigned long currentTime = micros();

  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_US && !recordingComplete) {
    lastSampleTime = currentTime;
    
    float accX, accY, accZ;
    if (!qmi.getAccelerometer(accX, accY, accZ)) {
      Serial.println("Accelerometer read failed!");
      return;
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
        flightData[dataIndex].pressure = pressure;
        flightData[dataIndex].altitude = altitude;
        flightData[dataIndex].temperature = temperature;
        dataIndex++;
      } else {
        recordingComplete = true;
        tft.fillScreen(ST77XX_BLACK);
        tft.setCursor(0, 0);
        tft.println("DATA FULL");
        Serial.println("Data storage full");
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
    while(1); // Stop after dumping data
  }
}