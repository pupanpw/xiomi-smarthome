from flask import Flask, jsonify
from miio import Device
from dotenv import load_dotenv
import os

load_dotenv()

ip = os.getenv("MI_IP")
token = os.getenv("MI_TOKEN")

if not ip or not token:
    raise Exception("MI_IP or MI_TOKEN not set in .env")

device = Device(ip, token)

app = Flask(__name__)


def plug_on():
    return device.send(
        "set_properties",
        [{"siid": 2, "piid": 1, "value": True}]
    )


def plug_off():
    return device.send(
        "set_properties",
        [{"siid": 2, "piid": 1, "value": False}]
    )


def plug_status():
    result = device.send(
        "get_properties",
        [{"siid": 2, "piid": 1}]
    )
    return result[0]["value"]


def get_energy():
    # ดึงข้อมูลเฉพาะที่เซ็นเซอร์รุ่น WP5-AM รองรับ
    result = device.send(
        "get_properties",
        [
            # Electric Power (ค่าวัตต์ปัจจุบัน)
            {"did": "1", "siid": 3, "piid": 2},
            # Power Consumption (หน่วยการใช้ไฟสะสม)
            {"did": "1", "siid": 3, "piid": 1}
        ]
    )

    # เช็คว่าถ้าดึงค่ามาได้สำเร็จ (code: 0) ให้คืนค่า value
    power_watt = result[0].get("value", 0) if result[0].get("code") == 0 else 0
    power_consumption = result[1].get(
        "value", 0) if result[1].get("code") == 0 else 0

    return {
        "power_watt": power_watt,
        "energy_consumed": power_consumption,
        "note": "This model does not support Voltage and Current reading"
    }


@app.route("/plug/on")
def on():
    try:
        result = plug_on()
        return jsonify({"status": "on", "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/plug/off")
def off():
    try:
        result = plug_off()
        return jsonify({"status": "off", "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/plug/status")
def status():
    try:
        state = plug_status()
        return jsonify({"power": state})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/plug/toggle")
def toggle():
    try:
        state = plug_status()

        if state:
            plug_off()
            new_state = "off"
        else:
            plug_on()
            new_state = "on"

        return jsonify({"status": new_state})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/plug/energy")
def energy():
    try:
        return jsonify(get_energy())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
