/*
 * Enhanced Rocket Data Logger for ESP32-S3
 * Features:
 * - 5Hz GPS sampling (PA1010D)
 * - Launch detection (2G threshold)
 * - Dual altitude (BMP280 + GPS)
 * - Vertical speed tracking
 * - Power-efficient GPS standby mode
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
const unsigned int GPS_SAMPLE_INTERVAL = 200; // 5Hz GPS sampling

// Sensor objects
Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);
Adafruit_BMP280 bmp;
SensorQMI8658 qmi;
Adafruit_GPS gps(&Wire);

// Enhanced data structure
struct SensorData {
  unsigned long timestamp;
  float acceleration[3];    // X,Y,Z in g
  float gyroscope[3];       // X,Y,Z in dps
  float pressure;           // hPa
  float bmpAltitude;        // meters
  float temperature;        // °C
  float latitude;           // degrees
  float longitude;          // degrees
  float gpsAltitude;        // meters
  float verticalSpeed;      // m/s
  uint8_t satellites;       // Number of satellites
  bool gpsFix;              // Fix status
};

SensorData flightData[MAX_DATA_POINTS];
volatile unsigned int dataIndex = 0;
volatile bool launchDetected = false;
volatile bool recordingComplete = false;
unsigned long lastGpsSampleTime = 0;

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
  tft.setTextSize(1);
}

// Initialize BMP280
void initBMP() {
  if (!bmp.begin(BMP_Addr)) {
    tft.setCursor(0, 20);
    tft.print("BMP280 not found");
    while (1);
  }
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                 Adafruit_BMP280::SAMPLING_X2,
                 Adafruit_BMP280::SAMPLING_X16,
                 Adafruit_BMP280::FILTER_X16,
                 Adafruit_BMP280::STANDBY_MS_500);
}

// Initialize QMI8658
void initQMI() {
  if (!qmi.begin(Wire, QMI_Addr, I2C_SDA, I2C_SCL)) {
    tft.setCursor(0, 40);
    tft.print("QMI8658 not found");
    while (1);
  }
  qmi.enableGyroscope(500);  // 500 dps range
  qmi.enableAccelerometer(4); // 4g range
}

// Initialize GPS with improved settings
void initGPS() {
  gps.begin(0x10); // PA1010D default I2C address
  
  // Configure for minimum necessary NMEA sentences
  gps.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA); // Position and altitude
  gps.sendCommand(PMTK_SET_NMEA_UPDATE_5HZ);    // 5Hz update rate
  gps.sendCommand(PGCMD_NOANTENNA);             // No antenna status
  
  // Put GPS in standby until launch
  gps.sendCommand(PMTK_STANDBY);
  delay(1000);
}

// Detect launch based on vertical acceleration
bool detectLaunch(float currentAccel) {
  static float baselineAccel = 1.0; // 1G baseline
  return (currentAccel > baselineAccel * LAUNCH_THRESHOLD);
}

// Display current status on screen
void displayStatus() {
  tft.fillRect(0, 60, 240, 180, ST77XX_BLACK); // Clear status area
  
  float accX, accY, accZ;
  if (qmi.getAccelerometer(accX, accY, accZ)) {
    tft.setCursor(0, 60);
    tft.printf("AccZ: %.2f g\n", accZ);
  }
  
  tft.printf("BMP Alt: %.1f m\n", bmp.readAltitude(SEA_LEVEL_PRESSURE_HPA));
  
  if (gps.fix) {
    tft.printf("GPS Alt: %.1f m\n", gps.altitude);
    tft.printf("Speed: %.1f m/s\n", gps.speed);
    tft.printf("Sats: %d\n", gps.satellites);
  } else {
    tft.println("GPS: No fix");
  }
  
  tft.printf("Samples: %d/%d\n", dataIndex, MAX_DATA_POINTS);
  tft.printf("Status: %s\n", launchDetected ? "LAUNCH!" : "Waiting...");
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
    Serial.printf("\"bmpAltitude\": %.2f,", flightData[i].bmpAltitude);
    Serial.printf("\"gpsAltitude\": %.2f,", flightData[i].gpsAltitude);
    Serial.printf("\"verticalSpeed\": %.2f,", flightData[i].verticalSpeed);
    Serial.printf("\"temperature\": %.2f,", flightData[i].temperature);
    Serial.printf("\"position\": {\"lat\": %.6f, \"lon\": %.6f},", 
                 flightData[i].latitude, flightData[i].longitude);
    Serial.printf("\"gpsFix\": %s,", flightData[i].gpsFix ? "true" : "false");
    Serial.printf("\"satellites\": %d}", flightData[i].satellites);
    
    if (i < dataIndex - 1) Serial.println(",");
    else Serial.println();
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
  initGPS();
  
  memset(flightData, 0, sizeof(flightData));
  
  tft.println("System Ready");
  tft.println("Waiting for launch...");
  displayStatus();
}

void loop() {
  static unsigned long lastSampleTime = 0;
  unsigned long currentTime = micros();

  // Main data sampling at 10Hz
  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_US && !recordingComplete) {
    lastSampleTime = currentTime;

    // Read IMU data
    float accX, accY, accZ;
    float gx, gy, gz;
    qmi.getAccelerometer(accX, accY, accZ);
    qmi.getGyroscope(gx, gy, gz);

    // Read BMP280 data
    float pressure = bmp.readPressure() / 100.0F;
    float altitude = bmp.readAltitude(SEA_LEVEL_PRESSURE_HPA);
    float temperature = bmp.readTemperature();

    // Check for launch
    if (!launchDetected && detectLaunch(accZ)) {
      launchDetected = true;
      dataIndex = 0;
      gps.sendCommand(PMTK_AWAKE); // Wake up GPS
      tft.fillScreen(ST77XX_BLACK);
      tft.setCursor(0, 0);
      tft.println("LAUNCH DETECTED!");
    }

    // Store data if launched or buffer not full
    if (launchDetected && dataIndex < MAX_DATA_POINTS) {
      flightData[dataIndex].timestamp = currentTime;
      flightData[dataIndex].acceleration[0] = accX;
      flightData[dataIndex].acceleration[1] = accY;
      flightData[dataIndex].acceleration[2] = accZ;
      flightData[dataIndex].gyroscope[0] = gx;
      flightData[dataIndex].gyroscope[1] = gy;
      flightData[dataIndex].gyroscope[2] = gz;
      flightData[dataIndex].pressure = pressure;
      flightData[dataIndex].bmpAltitude = altitude;
      flightData[dataIndex].temperature = temperature;
      
      // GPS data is updated separately at 5Hz
      dataIndex++;
    } else if (dataIndex >= MAX_DATA_POINTS) {
      recordingComplete = true;
      tft.fillScreen(ST77XX_BLACK);
      tft.setCursor(0, 0);
      tft.println("DATA FULL");
      gps.sendCommand(PMTK_STANDBY); // Save power
    }
  }

  // GPS sampling at 5Hz (independent of main loop)
  if (millis() - lastGpsSampleTime >= GPS_SAMPLE_INTERVAL && launchDetected) {
    lastGpsSampleTime = millis();
    
    // Read and parse GPS data
    if (gps.newNMEAreceived()) {
      gps.read();
      
      if (dataIndex > 0 && dataIndex <= MAX_DATA_POINTS) {
        // Update most recent data point with GPS info
        flightData[dataIndex-1].latitude = gps.latitudeDegrees;
        flightData[dataIndex-1].longitude = gps.longitudeDegrees;
        flightData[dataIndex-1].gpsAltitude = gps.altitude;
        flightData[dataIndex-1].verticalSpeed = gps.speed;
        flightData[dataIndex-1].satellites = gps.satellites;
        flightData[dataIndex-1].gpsFix = gps.fix;
      }
    }
  }

  // Update display every 200ms
  static unsigned long lastDisplayUpdate = 0;
  if (millis() - lastDisplayUpdate > 200) {
    lastDisplayUpdate = millis();
    displayStatus();
  }

  // Dump data when complete
  if (recordingComplete && !Serial.available()) {
    dumpDataToSerial();
    while (1); // Stop after dumping data
  }
}