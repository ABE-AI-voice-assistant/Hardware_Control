import pvporcupine
import pyaudio
import struct
import wave
import time

ACCESS_KEY = "24lmnH3vMcvIXXXgZ6pzmcHsqVJqvENUq1UpTHnIBDKj2ZYAD8O1iw=="  

# Initialize Porcupine
porcupine = pvporcupine.create(access_key=ACCESS_KEY, keywords=["computer"])


#if we are using custom key word like Selam Abe 
# Use the path to your custom keyword file
#custom_keyword_path = "path/to/your/custom_keyword.ppn"
#.ppn file is the file you download after training the model in the website 
#porcupine = pvporcupine.create(access_key=ACCESS_KEY, keywords=[custom_keyword_path])

# Setup PyAudio
pa = pyaudio.PyAudio()

audio_stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

def record_command(filename="wake_command.wav", duration_sec=5):
    print(f"🎙️ Recording command for {duration_sec} seconds...")

    frames = []
    sample_rate = 16000
    chunk = 1024
    record_stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk
    )

    for _ in range(0, int(sample_rate / chunk * duration_sec)):
        data = record_stream.read(chunk)
        frames.append(data)

    record_stream.stop_stream()
    record_stream.close()

    # Save to WAV
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"💾 Saved: {filename}\n")

print("👂 Listening for wake word 'porcupine'...")

try:
    while True:
        pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm_unpacked)
        if keyword_index >= 0:
            print("🦔 Wake word detected!")
            record_command()
            print("🔁 Returning to wake word listening...")

except KeyboardInterrupt:
    print("🛑 Stopped by user.")

finally:
    audio_stream.stop_stream()
    audio_stream.close()
    porcupine.delete()
    pa.terminate()
