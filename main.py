import network
import socket
import time
import dht
import json
from machine import Pin, SoftI2C, time_pulse_us, Timer
from machine_i2c_lcd import I2cLcd

# ==========================================
# 1. HARDWARE SETUP
# ==========================================
# Task 1: Built-in LED on GPIO 2 (D2)
led = Pin(2, Pin.OUT)
led.off()
led_state = False

# Task 2: Ultrasonic Sensor (HC-SR04)
TRIG = Pin(27, Pin.OUT)
ECHO = Pin(26, Pin.IN)

# Task 2: DHT11 Sensor on Pin 4 (D4)
dht_sensor = dht.DHT11(Pin(4))

# Task 3 & 4: I2C 16x2 LCD Setup (Pins 21 & 22)
I2C_ADDR = 0x27
i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

lcd.clear()
lcd.putstr("Server Initializing...")

# ==========================================
# STATE & SCROLL VARIABLES
# ==========================================
scroll_timer = Timer(0)
scroll_text = ""
scroll_index = 0
is_scrolling = False
last_msg = "" 

def lcd_scroll_callback(t):
    """Background hardware timer function to handle smooth scrolling."""
    global scroll_text, scroll_index
    if not is_scrolling or not scroll_text:
        return
    
    display_frame = scroll_text[scroll_index:scroll_index + 16]
    lcd.move_to(0, 0)
    lcd.putstr(display_frame)
    
    scroll_index += 1
    if scroll_index > len(scroll_text) - 16:
        scroll_index = 0

# ==========================================
# CORE HARDWARE HELPER FUNCTIONS
# ==========================================
def get_distance_cm():
    """Task 2: Read HC-SR04 ultrasonic distance sensor."""
    TRIG.off()
    time.sleep_us(2)
    TRIG.on()
    time.sleep_us(10)
    TRIG.off()
    
    t = time_pulse_us(ECHO, 1, 30000)
    if t < 0:
        return None
    return (t * 0.0343) / 2.0

def get_temperature_c():
    """Task 2: Read DHT11 climate module safely."""
    try:
        dht_sensor.measure()
        return dht_sensor.temperature()
    except Exception:
        return None

def url_decode(s):
    """Task 4: Sanitize text payload sent from the browser textbox."""
    s = s.replace('+', ' ')
    while '%' in s:
        idx = s.find('%')
        if idx != -1:
            hex_code = s[idx+1:idx+3]
            try:
                s = s[:idx] + chr(int(hex_code, 16)) + s[idx+3:]
            except:
                s = s[:idx] + '?' + s[idx+3:]
    return s

# ==========================================
# WIFI NETWORK ENGINE
# ==========================================
ssid = "Robotic WIFI"
password = "rbtWIFI@2025"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

ip = wifi.ifconfig()[0]
print("Connected! IP Address:", ip)

lcd.clear()
lcd.move_to(0, 0)
lcd.putstr("WiFi Connected!")
lcd.move_to(0, 1)
lcd.putstr(ip)

# ==========================================
# WEB SERVER SOCKET SETUP
# ==========================================
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

# ==========================================
# HTML GENERATOR WITH SEAMLESS BACKGROUND AJAX
# ==========================================
def web_page(state, temp, dist, current_msg):
    color = "green" if state else "red"
    status = "LED is ON" if state else "LED is OFF"
    
    temp_str = f"{temp} &deg;C" if temp is not None else "Reading error..."
    dist_str = f"{dist:.1f} cm" if dist is not None else "Out of range..."

    html = f"""
    <html>
    <head>
        <title>IoT Controller Platform</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; background: #eaedf1; margin: 0; padding: 20px; }}
            .app-container {{ background: #ffffff; max-width: 500px; margin: 0 auto; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); }}
            h1 {{ color: #2c3e50; font-size: 24px; margin-bottom: 5px; }}
            h3 {{ color: #7f8c8d; font-weight: 400; margin-top: 0; margin-bottom: 20px; }}
            .status-indicator {{ width: 50px; height: 50px; background-color: {color}; border-radius: 50%; margin: 15px auto; box-shadow: inset 0 2px 5px rgba(0,0,0,0.2); }}
            .section {{ border-top: 1px solid #dcdde1; padding: 15px 0; margin-top: 15px; }}
            .data-box {{ font-size: 18px; font-weight: 600; color: #2c3e50; margin: 8px 0; }}
            button {{ padding: 10px 20px; font-size: 15px; font-weight: bold; margin: 5px; cursor: pointer; border-radius: 6px; border: none; transition: 0.2s; }}
            .btn-on {{ background: #2ecc71; color: white; }}
            .btn-off {{ background: #e74c3c; color: white; }}
            .btn-lcd {{ background: #3498db; color: white; width: 45%; }}
            .btn-submit {{ background: #9b59b6; color: white; width: 100%; max-width: 200px; }}
            input[type="text"] {{ width: 80%; padding: 10px; font-size: 15px; border: 1px solid #bdc3c7; border-radius: 6px; margin-bottom: 10px; box-sizing: border-box; }}
        </style>
        
        <script>
            // Quiet background updates for sensor numbers only (Stops page reloads!)
            setInterval(function() {{
                fetch('/data')
                    .then(response => response.json())
                    .then(data => {{
                        document.getElementById('tempVal').innerHTML = data.temp;
                        document.getElementById('distVal').innerHTML = data.dist;
                    }})
                    .catch(err => console.log('Update error:', err));
            }}, 2000);
        </script>
    </head>
    <body>
        <div class="app-container">
            <h1>IoT Web Dashboard</h1>
            <h3>ESP32 Resource Management</h3>
            
            <div class="section">
                <div class="status-indicator"></div>
                <p style="font-size: 16px; font-weight: bold; margin: 5px 0;">Status: {status}</p>
                <a href="/on"><button class="btn-on">LED ON</button></a>
                <a href="/off"><button class="btn-off">LED OFF</button></a>
            </div>
            
            <div class="section">
                <div class="data-box">Temperature Sensor: <span id="tempVal" style="color:#e67e22;">{temp_str}</span></div>
                <div class="data-box">Ultrasonic Tracker: <span id="distVal" style="color:#16a085;">{dist_str}</span></div>
            </div>
            
            <div class="section">
                <p style="font-weight: bold; color: #34495e;">LCD Display Sync Engine</p>
                <a href="/show_dist"><button class="btn-lcd">Write Distance (Row 1)</button></a>
                <a href="/show_temp"><button class="btn-lcd">Write Temp (Row 2)</button></a>
            </div>
            
            <div class="section">
                <p style="font-weight: bold; color: #34495e;">Send Custom Text Broadcast</p>
                <form action="/msg" method="get">
                    <input type="text" id="msgBox" name="text" value="{current_msg}" placeholder="Type a message to send..." required>
                    <br>
                    <button type="submit" class="btn-submit">Broadcast onto LCD</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# ==========================================
# MAIN EVENT PROCESSOR LOOP
# ==========================================
while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(1024).decode()
        
        if not request:
            conn.close()
            continue

        request_line = request.split('\n')[0]
        print("Incoming Event Route Target:", request_line)

        # background AJAX request route handler
        if "/data" in request_line:
            current_temp = get_temperature_c()
            current_dist = get_distance_cm()
            
            temp_output = f"{current_temp} &deg;C" if current_temp is not None else "Reading error..."
            dist_output = f"{current_dist:.1f} cm" if current_dist is not None else "Out of range..."
            
            json_data = json.dumps({{"temp": temp_output, "dist": dist_output}})
            
            conn.send("HTTP/1.1 200 OK\n")
            conn.send("Content-Type: application/json\n")
            conn.send("Connection: close\n\n")
            conn.send(json_data)
            conn.close()
            continue

        # TASK 1 HANDLING
        if "/on" in request_line:
            led.on()
            led_state = True
        elif "/off" in request_line:
            led.off()
            led_state = False

        current_temp = get_temperature_c()
        current_dist = get_distance_cm()

        # TASK 3 HANDLING
        if "/show_dist" in request_line:
            is_scrolling = False  
            scroll_timer.deinit()
            lcd.move_to(0, 0)
            lcd.putstr(" " * 16)  
            lcd.move_to(0, 0)
            if current_dist is not None:
                lcd.putstr(f"Dist: {current_dist:.1f} cm")
            else:
                lcd.putstr("Dist: Out Range")
                
        elif "/show_temp" in request_line:
            is_scrolling = False
            scroll_timer.deinit()
            lcd.move_to(0, 1)
            lcd.putstr(" " * 16)
            lcd.move_to(0, 1)
            if current_temp is not None:
                lcd.putstr(f"Temp: {current_temp} C")
            else:
                lcd.putstr("Temp: Read Error")

        # TASK 4 HANDLING
        elif "/msg?text=" in request_line:
            try:
                is_scrolling = False
                scroll_timer.deinit()
                lcd.clear()
                
                start_idx = request_line.find("?text=") + 6
                end_idx = request_line.find(" HTTP", start_idx)
                raw_msg = request_line[start_idx:end_idx]
                
                last_msg = url_decode(raw_msg)
                
                if len(last_msg) <= 16:
                    lcd.move_to(0, 0)
                    lcd.putstr(last_msg)
                else:
                    scroll_text = last_msg + "    " 
                    scroll_index = 0
                    is_scrolling = True
                    # CHANGED: period set to 1500ms to allow text to advance smoothly without jumping or rushing
                    scroll_timer.init(period=1500, mode=Timer.PERIODIC, callback=lcd_scroll_callback)
                    
            except Exception as msg_error:
                print("Error tracking text input:", msg_error)

        # RESPONSE DELIVERY PIPELINE
        response = web_page(led_state, current_temp, current_dist, last_msg)
        
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)
        conn.close()
        
    except Exception as general_error:
        print("Server Engine Exception Trap:", general_error)
        time.sleep(1)
