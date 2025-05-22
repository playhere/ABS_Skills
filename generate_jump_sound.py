import wave
import struct
import math
import os

def generate_jump_sound(filename, duration=0.3, sample_rate=44100):
    # Create the sounds directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Calculate number of frames
    n_frames = int(duration * sample_rate)
    
    # Open wave file
    with wave.open(filename, 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        
        # Generate a simple "boing" sound
        for i in range(n_frames):
            # Create a decaying sine wave
            t = i / sample_rate
            frequency = 440 * (1 - t/duration)  # Frequency decreases over time
            amplitude = 32767 * (1 - t/duration)  # Amplitude decreases over time
            
            # Generate the sine wave
            value = int(amplitude * math.sin(2 * math.pi * frequency * t))
            
            # Pack the value into a 16-bit signed integer
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

if __name__ == "__main__":
    # Generate the jump sound
    generate_jump_sound("assets/sounds/jump.wav")
    print("Jump sound effect generated successfully!") 