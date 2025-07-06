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
const float CRASH_ALTITUDE_THRESHOLD = 20.0; // Fixed naming to match usage
const float CRASH_ACCELERATION_THRESHOLD = 5.0; // Fixed naming
const float CRASH_VELOCITY_THRESHOLD = -5.0; // Fixed naming
const unsigned int CRASH_CONFIRMATION_SAMPLES = 5; // Fixed naming

// Sensor Objects
Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);
Adafruit_BMP280 bmp;
SensorQMI8658 qmi;

// Data Structure
struct SensorData {
  unsigned long timestamp;
  float acceleration[3]; // x, y, z in g
  float gyroscope[3];    // x, y, z in deg/s
  float pressure;       // in hPa
  float altitude;       // in meters
  float temperature;    // in °C
};

// Data Storage
SensorData flightData[MAX_DATA_POINTS];
volatile unsigned int dataIndex = 0;
volatile bool launchDetected = false;
volatile bool recordingComplete = false;
volatile bool apogeeReached = false;
volatile bool crashDetected = false;
volatile unsigned int crashConfirmationCount = 0;
float previousAltitude = 0;
unsigned long previousAltitudeTime = 0;
float verticalVelocity = 0;

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

bool detectCrash(float currentAltitude, float currentAccelZ, unsigned long currentTime) {
    // Calculate vertical velocity (m/s)
    if (previousAltitudeTime > 0 && currentTime > previousAltitudeTime) {
        float timeDelta = (currentTime - previousAltitudeTime) / 1000000.0; // Convert to seconds
        verticalVelocity = (currentAltitude - previousAltitude) / timeDelta;
    }
    
    // Update previous values for next calculation
    previousAltitude = currentAltitude;
    previousAltitudeTime = currentTime;
    
    // Only check for crash if we've reached significant altitude
    if (currentAltitude > CRASH_ALTITUDE_THRESHOLD) {
        apogeeReached = true;
    }
    
    // Check for crash conditions
    if (apogeeReached) {
        bool crashCondition = (verticalVelocity < CRASH_VELOCITY_THRESHOLD) || 
                             (currentAccelZ > CRASH_ACCELERATION_THRESHOLD);
        
        if (crashCondition) {
            crashConfirmationCount++;
            if (crashConfirmationCount >= CRASH_CONFIRMATION_SAMPLES) {
                return true;
            }
        } else {
            crashConfirmationCount = 0; // Reset if conditions aren't consistently met
        }
    }
    
    return false;
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
  tft.printf("Vel: %.1f m/s\n", verticalVelocity);
  if (apogeeReached) {
    tft.println("Apogee: YES");
  }
  if (crashDetected) {
    tft.println("STATUS: CRASHED");
  } else if (launchDetected) {
    tft.println("STATUS: IN FLIGHT");
  }
}

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
    Serial.printf("\"temperature\": %.2f}", flightData[i].temperature);
    
    if (i < dataIndex - 1) {
      Serial.println(",");
    } else {
      Serial.println();
    }
  }
  
  Serial.println("]}");
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
  static unsigned long lastDisplayUpdate = 0;
  unsigned long currentTime = micros();

  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_US && !recordingComplete) {
    lastSampleTime = currentTime;
    
    float accX, accY, accZ;
    float gx, gy, gz;
    if (!qmi.getAccelerometer(accX, accY, accZ)) {
      Serial.println("Accelerometer read failed!");
      return;
    }
    if (!qmi.getGyroscope(gx, gy, gz)) {
      Serial.println("Gyroscope read failed!");
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
        flightData[dataIndex].gyroscope[0] = gx;
        flightData[dataIndex].gyroscope[1] = gy;
        flightData[dataIndex].gyroscope[2] = gz;
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

    // Check for crash
    if (!crashDetected && launchDetected) {
      if (detectCrash(altitude, accZ, currentTime)) {
        crashDetected = true;
        tft.fillScreen(ST77XX_RED);
        tft.setCursor(0, 0);
        tft.println("CRASH DETECTED!");
        Serial.println("CRASH DETECTED!");
        recordingComplete = true;
      }
    }
  }

  if (millis() - lastDisplayUpdate > 200) {
    lastDisplayUpdate = millis();
    displayStatus();
  }

  if (recordingComplete && !Serial.available()) {
    dumpDataToSerial();
    while(1); // Stop after dumping data
  }
}