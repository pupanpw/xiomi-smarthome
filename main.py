from flask import Flask, abort, jsonify, request
from miio import Device
from dotenv import load_dotenv
import os

load_dotenv()

# ---------------- CONFIG ----------------

plug1_ip = os.getenv("MI_IP")
plug1_token = os.getenv("MI_TOKEN")

plug2_ip = os.getenv("MI_FAN_SL_IP")
plug2_token = os.getenv("MI_FAN_SL_TOKEN")

ac_ip = os.getenv("MI_AIR_IP")
ac_token = os.getenv("MI_AIR_TOKEN")

SECRET_KEY = os.getenv("SECRET_KEY")

if not all(
    [
        plug1_ip,
        plug1_token,
        plug2_ip,
        plug2_token,
        ac_ip,
        ac_token,
        SECRET_KEY,
    ]
):
    raise Exception("Missing configuration in .env")

devices = {
    "plug1": Device(plug1_ip, plug1_token),
    "plug2": Device(plug2_ip, plug2_token),
    "ac": Device(ac_ip, ac_token),
}

app = Flask(__name__)

# ---------------- SECURITY ----------------


def check_secret(token):
    if not token or token.strip() != SECRET_KEY.strip():
        abort(401, description="Unauthorized")


# ---------------- CORE ----------------


def set_power(name, value):
    device = devices[name]

    try:
        # AC uses siid 3
        if name == "ac":
            return device.send(
                "set_properties",
                [{"siid": 3, "piid": 1, "value": value}],
            )

        # Plug uses siid 2
        return device.send(
            "set_properties",
            [{"siid": 2, "piid": 1, "value": value}],
        )

    except Exception as e:
        return {"error": str(e)}


def get_power(name):
    device = devices[name]

    try:
        if name == "ac":
            result = device.send(
                "get_properties",
                [{"siid": 3, "piid": 1}],
            )
        else:
            result = device.send(
                "get_properties",
                [{"siid": 2, "piid": 1}],
            )

        return result[0]["value"]

    except Exception as e:
        return str(e)


# ---------------- PLUG1 ----------------


@app.route("/plug1/<action>")
def control_plug1(action):

    token = request.headers.get("X-SECRET-KEY") or request.args.get("key")
    check_secret(token)

    if action == "on":
        return jsonify(set_power("plug1", True))

    if action == "off":
        return jsonify(set_power("plug1", False))

    if action == "status":
        return jsonify({"power": get_power("plug1")})

    abort(400)


# ---------------- PLUG2 ----------------


@app.route("/plug2/<action>")
def control_plug2(action):

    token = request.headers.get("X-SECRET-KEY") or request.args.get("key")
    check_secret(token)

    if action == "on":
        return jsonify(set_power("plug2", True))

    if action == "off":
        return jsonify(set_power("plug2", False))

    if action == "status":
        return jsonify({"power": get_power("plug2")})

    abort(400)


# ---------------- AC ----------------


@app.route("/ac/on")
def ac_on():

    token = request.headers.get("X-SECRET-KEY") or request.args.get("key")
    check_secret(token)

    return jsonify(set_power("ac", True))


@app.route("/ac/off")
def ac_off():

    token = request.headers.get("X-SECRET-KEY") or request.args.get("key")
    check_secret(token)

    return jsonify(set_power("ac", False))


@app.route("/ac/status")
def ac_status():

    token = request.headers.get("X-SECRET-KEY") or request.args.get("key")
    check_secret(token)

    try:

        result = devices["ac"].send(
            "get_properties",
            [
                {"siid": 3, "piid": 1},
                {"siid": 3, "piid": 4},
            ],
        )

        power = result[0]["value"]
        temp = result[1]["value"]

        return jsonify(
            {
                "power": power,
                "temperature": temp,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)})


# -------- TEMP --------


@app.route("/ac/temp/<int:temp>")
def ac_temp(temp):

    token = request.headers.get("X-SECRET-KEY") or request.args.get("key")
    check_secret(token)

    try:
        result = devices["ac"].send(
            "set_properties",
            [{"siid": 3, "piid": 4, "value": temp}],
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})


# ---------------- ALL STATUS ----------------


@app.route("/all/status")
def all_status():

    token = request.headers.get("X-SECRET-KEY") or request.args.get("key")
    check_secret(token)

    return jsonify(
        {
            "plug1": get_power("plug1"),
            "plug2": get_power("plug2"),
            "ac": get_power("ac"),
        }
    )


# ---------------- MAIN ----------------


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
