import time

import utility

env_vars = utility.load_env(".env")

# Connect to WiFi
if env_vars.get("WIFI_ENABLED", None) and env_vars.get("WIFI_ENABLED", "").upper() == "TRUE":
    print("Initializing Network...")
    wlan = utility.connect_wifi(env_vars)
    if wlan is not None:
        utility.sync_ntp_time()

        # Extract network information
        import debugpy
        ip_address, subnet_mask, gateway, dns_server = wlan.ifconfig()
        # # 2. Extract current automatic assignments to read your gateway/DNS
        # current_config = wlan.ifconfig()
        # gateway = current_config[2]
        # dns = current_config[3]

        # # 3. FORCE the network mask to match your laptop's 255.255.252.0 profile
        # # Structure: (ESP32_IP, NETMASK, GATEWAY, DNS)
        # wlan.ifconfig(('192.168.4.34', '255.255.252.0', gateway, dns))
        print(f"=================================")
        print(f" ESP32 IP ADDRESS: {ip_address}")  # <-- Use this in your VS Code launch.json
        print(f"=================================")
        debugpy.listen("5678", "0.0.0.0")
        print("Waiting for VS Code to attach over Wi-Fi...")

        # 3. Halt code execution right here until you press attach in your IDE
        # debugpy.wait_for_attach()

        # 4. Instrument the active execution line hook
        debugpy.debug_this_thread()
        time.sleep(1)
        import app
    else:
        print("WiFi connection failed. Skipping NTP time sync.")
else:
    print("WIFI_ENABLED not set to 'true'. Skipping network initialization and time sync.")

app.main_loop()
