from miio import Device
import os
from dotenv import load_dotenv

load_dotenv()
device = Device(os.getenv("MI_IP"), os.getenv("MI_TOKEN"))

try:
    print("กำลังลองดึงค่าไฟด้วยโปรโตคอล MiIO รุ่นเก่า...")
    # ลองถามหาคำศัพท์เก่าๆ ที่ Xiaomi ชอบใช้
    res = device.send(
        "get_prop", ["power", "energy", "power_cost_today", "electric_power"])
    print(f"ผลลัพธ์: {res}")
except Exception as e:
    print(f"Error: {e}")
