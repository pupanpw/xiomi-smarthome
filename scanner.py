from miio import Device
from dotenv import load_dotenv
import os

load_dotenv()

ip = os.getenv("MI_IP")
token = os.getenv("MI_TOKEN")

if not ip or not token:
    raise Exception("❌ ไม่พบ MI_IP หรือ MI_TOKEN ในไฟล์ .env กรุณาตรวจสอบ")

device = Device(ip, token)

print(f"🔍 กำลังสแกนหา Service ID และ Property ID ที่ IP: {ip}...")
print("อาจจะใช้เวลาสักครู่ (ตัวที่ Error จะรอ Timeout ประมาณ 5 วินาทีครับ)\n")

for siid in range(2, 7):
    for piid in range(1, 7):
        try:
            res = device.send("get_properties", [{"siid": siid, "piid": piid}])

            if res and len(res) > 0 and res[0].get("code") == 0:
                value = res[0].get("value")
                print(
                    f"✅ เจอแล้ว! siid: {siid}, piid: {piid} -> คืนค่ามาเป็น: {value}")
            else:
                code = res[0].get("code") if res and len(
                    res) > 0 else "Unknown"
                print(
                    f"⚠️ siid: {siid}, piid: {piid} -> ตอบกลับมาแต่ Code เป็น: {code}")

        except Exception as e:
            print(f"❌ siid: {siid}, piid: {piid} -> ไม่รองรับ (Timeout)")

print("\n🎉 สแกนเสร็จสิ้น!")
