from pycaw.pycaw import AudioUtilities
import time

# Get audio device
device = AudioUtilities.GetSpeakers()
volume = device.EndpointVolume

print(f"Audio output: {device.FriendlyName}")
print(f"Testing mute/unmute functionality...\n")

# Check current mute state
current_mute = volume.GetMute()
print(f"Current mute state: {current_mute} (0=unmuted, 1=muted)")

print("\nTest 1: Muting audio...")
volume.SetMute(1, None)
time.sleep(0.5)
print(f"Mute state after SetMute(1): {volume.GetMute()}")

print("\nWaiting 2 seconds...")
time.sleep(2)

print("\nTest 2: Unmuting audio...")
volume.SetMute(0, None)
time.sleep(0.5)
print(f"Mute state after SetMute(0): {volume.GetMute()}")

print("\nWaiting 2 seconds...")
time.sleep(2)

print("\nTest 3: Muting again...")
volume.SetMute(1, None)
time.sleep(0.5)
print(f"Mute state after SetMute(1): {volume.GetMute()}")

print("\nWaiting 2 seconds...")
time.sleep(2)

print("\nTest 4: Unmuting again...")
volume.SetMute(0, None)
time.sleep(0.5)
print(f"Mute state after SetMute(0): {volume.GetMute()}")

print("\n✓ Test completed!")
print("Did you hear the audio mute and unmute?")
