from flask import Flask, abort, jsonify, request
from miio import Device
from dotenv import load_dotenv
import os

load_dotenv()

plug1_ip = os.getenv("MI_IP")
plug1_token = os.getenv("MI_TOKEN")

plug2_ip = os.getenv("MI_FAN_SL_IP")
plug2_token = os.getenv("MI_FAN_SL_TOKEN")

SECRET_KEY = os.getenv("SECRET_KEY")

if not plug1_ip or not plug1_token:
    raise Exception("Plug1 not set")

if not plug2_ip or not plug2_token:
    raise Exception("Plug2 not set")

if not SECRET_KEY:
    raise Exception("SECRET_KEY not set")


devices = {
    "plug1": Device(plug1_ip, plug1_token),
    "plug2": Device(plug2_ip, plug2_token),
}

app = Flask(__name__)


def check_secret():
    token = request.args.get("key")

    if not token or token.strip() != SECRET_KEY.strip():
        abort(401, description="Unauthorized")


def set_power(name, value):
    device = devices[name]

    return device.send(
        "set_properties",
        [
            {
                "siid": 2,
                "piid": 1,
                "value": value
            }
        ]
    )


def get_power(name):
    device = devices[name]

    result = device.send(
        "get_properties",
        [
            {
                "siid": 2,
                "piid": 1
            }
        ]
    )

    return result[0]["value"]


def toggle(name):
    state = get_power(name)

    if state:
        set_power(name, False)
        return "off"
    else:
        set_power(name, True)
        return "on"


@app.route("/plug1/on")
def plug1_on():
    check_secret()
    return jsonify(set_power("plug1", True))


@app.route("/plug1/off")
def plug1_off():
    check_secret()
    return jsonify(set_power("plug1", False))


@app.route("/plug1/status")
def plug1_status():
    check_secret()
    return jsonify({"power": get_power("plug1")})


@app.route("/plug1/toggle")
def plug1_toggle():
    check_secret()
    return jsonify({"status": toggle("plug1")})


@app.route("/plug2/on")
def plug2_on():
    check_secret()
    return jsonify(set_power("plug2", True))


@app.route("/plug2/off")
def plug2_off():
    check_secret()
    return jsonify(set_power("plug2", False))


@app.route("/plug2/status")
def plug2_status():
    check_secret()
    return jsonify({"power": get_power("plug2")})


@app.route("/plug2/toggle")
def plug2_toggle():
    check_secret()
    return jsonify({"status": toggle("plug2")})


# -----------------
# ALL
# -----------------

@app.route("/all/on")
def all_on():
    check_secret()

    r1 = set_power("plug1", True)
    r2 = set_power("plug2", True)

    return jsonify({
        "plug1": r1,
        "plug2": r2
    })


@app.route("/all/off")
def all_off():
    check_secret()

    r1 = set_power("plug1", False)
    r2 = set_power("plug2", False)

    return jsonify({
        "plug1": r1,
        "plug2": r2
    })


@app.route("/all/status")
def all_status():
    check_secret()

    s1 = get_power("plug1")
    s2 = get_power("plug2")

    return jsonify({
        "plug1": s1,
        "plug2": s2
    })


# -----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
