"""Integration test that exercises the MQTT-controlled volume controller
by publishing messages to the broker and verifying the system volume/mute
changes.

Notes:
- Requires a running MQTT broker reachable at `--broker`/`--port`.
- Will start an in-process subscriber client (using the same handlers as
  `main.py`) so you don't need to run `main.py` separately.
- This test will change system audio. Use `--dry-run` to only print actions.
"""

import argparse
import ctypes
import sys
import time

import paho.mqtt.client as mqtt

from main import VolumeController, _on_connect, _on_message


def approx_equal(a: int, b: int, tol: int = 3) -> bool:
    return abs(a - b) <= tol


def run_test(broker: str, port: int, dry_run: bool = False, sleep_s: float = 0.6) -> int:
    vc = VolumeController(show_osd=False)

    # save original state
    orig_vol = vc.get_volume_percent()
    b = ctypes.c_bool()
    vc.ep.GetMute(ctypes.byref(b))
    orig_mute = bool(b.value)
    print(f"Original: vol={orig_vol}% mute={orig_mute}")

    # Start subscriber client (the controller) in-process
    sub = mqtt.Client(userdata={"vc": vc})
    sub.on_connect = _on_connect
    sub.on_message = _on_message
    sub.user_data_set({"vc": vc})
    try:
        sub.connect(broker, port)
    except Exception as exc:
        print(f"Failed to connect subscriber to broker {broker}:{port}: {exc}")
        return 2
    sub.loop_start()

    pub = mqtt.Client()
    try:
        pub.connect(broker, port)
    except Exception as exc:
        print(f"Failed to connect publisher to broker {broker}:{port}: {exc}")
        sub.loop_stop()
        sub.disconnect()
        return 2
    pub.loop_start()

    try:
        # publish a few volume values
        for level in (10, 60, 30):
            print(f"Publishing volume {level}")
            if not dry_run:
                pub.publish("esp32/volume", str(level))
            time.sleep(sleep_s)
            if not dry_run:
                got = vc.get_volume_percent()
                print(f" Read-back: {got}%")
                if not approx_equal(got, level):
                    print(f"Mismatch: expected {level}, got {got}")
                    return 1

        # test mute via MQTT (toggle)
        print("Publishing mute toggle")
        if not dry_run:
            pub.publish("esp32/mute", "toggle")
        time.sleep(sleep_s)
        if not dry_run:
            b = ctypes.c_bool()
            vc.ep.GetMute(ctypes.byref(b))
            print(f" Mute state now: {bool(b.value)}")

            # toggle back
            pub.publish("esp32/mute", "toggle")
            time.sleep(sleep_s)

    finally:
        print("Restoring original state")
        if not dry_run:
            try:
                vc.ep.SetMute(orig_mute, None)
                vc.set_volume_percent(orig_vol)
            except Exception as exc:
                print("Failed to restore state:", exc)

        pub.loop_stop()
        pub.disconnect()
        sub.loop_stop()
        sub.disconnect()

    print("MQTT integration test passed")
    return 0


def main():
    parser = argparse.ArgumentParser(description="MQTT integration test for volume controller")
    parser.add_argument("--broker", default="localhost", help="MQTT broker host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--dry-run", action="store_true", help="Do not actually publish; only print actions")
    parser.add_argument("--sleep", type=float, default=0.6, help="Seconds to wait between operations")
    args = parser.parse_args()

    rc = run_test(args.broker, args.port, dry_run=args.dry_run, sleep_s=args.sleep)
    sys.exit(rc)


if __name__ == "__main__":
    main()
