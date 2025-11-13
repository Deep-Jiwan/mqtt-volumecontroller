"""Integration-style test for VolumeController.

This script will:
 - Import VolumeController from `main.py` (the MQTT controller module)
 - Save current master volume and mute state
 - Set several volume levels (0, 25, 50, 75, 100), sleeping briefly between them,
   and verify the reported volume is within a small tolerance
 - Toggle mute and verify state
 - Restore original volume and mute state on exit

Note: This test manipulates the system audio device. It should be run on a
machine where changing sound levels is acceptable. Use the `--dry-run` flag to
only print intended actions without applying them.
"""

import argparse
import sys
import time

try:
    from main import VolumeController
except Exception as exc:
    print("Failed to import VolumeController from main.py:", exc)
    raise


def approx_equal(a: int, b: int, tol: int = 2) -> bool:
    return abs(a - b) <= tol


def run_test(dry_run: bool = False, sleep_s: float = 0.6) -> int:
    vc = VolumeController(show_osd=False)

    # Save original state
    try:
        orig_vol = vc.get_volume_percent()
    except Exception:
        print("Failed to read original volume")
        return 2

    try:
        # Query mute state via EndpointVolume GetMute
        import ctypes

        b = ctypes.c_bool()
        vc.ep.GetMute(ctypes.byref(b))
        orig_mute = bool(b.value)
    except Exception:
        print("Failed to read original mute state")
        orig_mute = None

    print(f"Original volume: {orig_vol}%, mute={orig_mute}")

    levels = [0, 25, 50, 75, 100]

    try:
        for lvl in levels:
            print(f"Setting volume to {lvl}%")
            if not dry_run:
                vc.set_volume_percent(lvl)
            time.sleep(sleep_s)
            if not dry_run:
                got = vc.get_volume_percent()
                print(f" Read-back volume: {got}%")
                if not approx_equal(got, lvl, tol=3):
                    print(f" Volume mismatch: expected {lvl} got {got}")
                    return 1

        # Test mute toggling
        print("Testing mute toggle")
        if not dry_run:
            new = vc.toggle_mute()
            time.sleep(0.5)
            # verify
            b = ctypes.c_bool()
            vc.ep.GetMute(ctypes.byref(b))
            is_muted = bool(b.value)
            print(f" Mute state after toggle: {is_muted}")
            if is_muted != new:
                print(" Mute toggle state mismatch")
                return 1

            # Toggle back
            vc.toggle_mute()
            time.sleep(0.3)

    finally:
        # Restore original
        print("Restoring original state")
        if not dry_run:
            try:
                if orig_mute is not None:
                    vc.ep.SetMute(orig_mute, None)
                vc.set_volume_percent(orig_vol)
            except Exception as exc:
                print("Failed to restore audio state:", exc)
                # continue

    print("Integration test completed successfully")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Run integration test for VolumeController")
    parser.add_argument("--dry-run", action="store_true", help="Do not actually change volume; just print actions")
    parser.add_argument("--sleep", type=float, default=0.6, help="Seconds to sleep between operations")
    args = parser.parse_args()

    rc = run_test(dry_run=args.dry_run, sleep_s=args.sleep)
    sys.exit(rc)


if __name__ == "__main__":
    main()
