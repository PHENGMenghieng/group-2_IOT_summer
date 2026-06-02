# group-2_IOT_summer
lab2


+-----------------------------------------------------------------------------+
|                                 WEB BROWSER                                 |
|                                                                             |
|   +-----------------------+  +-------------------+  +-------------------+   |
|   |   LED Control Panel   |  | Custom Message Box|  |  Telemetry Display|   |
|   |  [LED ON]  [LED OFF]  |  | [               ] |  | Temp: -- C        |   |
|   +-----------+-----------+  +---------+---------+  | Dist: -- cm       |   |
+---------------|------------------------|------------+---------^-------------+
                |                        |                      |
    (HTTP GET /on or /off)        (HTTP GET /msg)        (AJAX /data Fetch)
    Toggles LED instantly         Sends message text     Runs every 2 seconds
                |                        |         (Never wipes your textbox!)
                v                        v                      |
+---------------------------------------------------------------|-------------+
|                               ESP32 WEB SERVER                |             |
|                                                               |             |
|   +------------------------+  +--------------------------+  +-v----------+  |
|   |    GPIO 2 (Output)     |  | Hardware Virtual Timer   |  | Sensor     |  |
|   |   Controls Onboard     |  | Shifting text array rows |  | Subroutines|  |
|   |       Blue LED         |  | at a perfect 1.5s pace   |  |            |  |
+---+-----------+------------+--+------------+-------------+--+-----+------+--+
                |                            |                      |
          (Onboard Pin)               (SoftI2C Bus)         (GPIO 4 / 26 / 27)
                |                            |                      |
                v                            v                      v
    +-----------------------+    +-----------------------+    +--------------+
    |      PHYSICAL LED     |    |   I2C 16x2 LCD UNIT   |    | DHT11 Temp & |
    |  Turns bright blue /  |    |  Row 1: Scrolling msg |    |   HC-SR04    |
    |  shuts down smoothly  |    |  Row 2: Pressed metrics|   | Ultrasound   |
    +-----------------------+    +-----------------------+    +--------------+
    
<div align="center">

# 🌐 IoT Webserver with LED, Sensors, and LCD Control
### Course: IoT Architecture & Design | Lab Assignment 2
**Group Number:** Group 2
    

<img width="555" height="802" alt="image" src="https://github.com/user-attachments/assets/c6925363-d2f2-44fb-b857-066a30cd8405" />
<img width="1280" height="960" alt="image" src="https://github.com/user-attachments/assets/19f98815-edd5-47f9-b4a6-b5b93b74d986" />
<img width="1280" height="960" alt="image" src="https://github.com/user-attachments/assets/62504a47-cbd3-4a13-92d0-3968c214baf5" />
<img width="960" height="1280" alt="image" src="https://github.com/user-attachments/assets/6e6ebbb5-c92d-40fa-bbf1-c6ac1fdce0f3" />
<img width="960" height="1280" alt="image" src="https://github.com/user-attachments/assets/4841ff2d-0936-41db-a77e-e0d78443705f" />
<img width="960" height="1280" alt="image" src="https://github.com/user-attachments/assets/9c694386-5369-4f05-9a1b-1f011ef59556" />
<img width="960" height="1280" alt="image" src="https://github.com/user-attachments/assets/cc99931d-b513-4f1a-91ec-bcad2c5a83cd" />
<img width="960" height="1280" alt="image" src="https://github.com/user-attachments/assets/25d3fd19-e6d6-406e-9719-ca1327f43ea6" />
<img width="960" height="1280" alt="image" src="https://github.com/user-attachments/assets/bf3c2545-38c0-4fe7-abb1-c7059cd6dccf" />

Video:

https://github.com/user-attachments/assets/4a1a300a-ad82-4e08-9299-b2b0b1f248ac
-
-
https://github.com/user-attachments/assets/ec122e6a-3863-4454-b546-4e7ca9665279
