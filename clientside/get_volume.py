from pycaw.pycaw import AudioUtilities

# Get audio device
device = AudioUtilities.GetSpeakers()
volume = device.EndpointVolume

print(f"Audio output: {device.FriendlyName}\n")

# Get current volume as scalar (0.0 - 1.0)
scalar_volume = volume.GetMasterVolumeLevelScalar()
percentage = int(scalar_volume * 100)

# Get current volume in dB
db_volume = volume.GetMasterVolumeLevel()

# Get mute state
is_muted = volume.GetMute()

# Get volume range
min_db, max_db, increment = volume.GetVolumeRange()

print("Current Audio State:")
print(f"  Volume (Scalar): {scalar_volume:.2f}")
print(f"  Volume (Percentage): {percentage}%")
print(f"  Volume (dB): {db_volume:.2f} dB")
print(f"  Muted: {'Yes 🔇' if is_muted else 'No 🔊'}")
print(f"\nVolume Range: {min_db} dB to {max_db} dB (increment: {increment})")
