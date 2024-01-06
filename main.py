from tkinter import *
from tkinter.ttk import Combobox
import pyttsx3
import numpy as np
import wave
import pyaudio
import matplotlib.pyplot as plt


CHARACTER_FREQUENCIES = {
    'a': (100, 1100, 2500),
    'b': (100, 1100, 3000),
    'c': (100, 1100, 3500),
    'd': (100, 1300, 2500),
    'e': (100, 1300, 3000),
    'f': (100, 1300, 3500),
    'g': (100, 1500, 2500),
    'h': (100, 1500, 3000),
    'i': (100, 1500, 3500),
    'j': (300, 1100, 2500),
    'k': (300, 1100, 3000),
    'l': (300, 1100, 3500),
    'm': (300, 1300, 2500),
    'n': (300, 1300, 3000),
    'o': (300, 1300, 3500),
    'p': (300, 1500, 2500),
    'q': (300, 1500, 3000),
    'r': (300, 1500, 3500),
    's': (500, 1100, 2500),
    't': (500, 1100, 3000),
    'u': (500, 1100, 3500),
    'v': (500, 1300, 2500),
    'w': (500, 1300, 3000),
    'x': (500, 1300, 3500),
    'y': (500, 1500, 2500),
    'z': (500, 1500, 3000),
    ' ': (500, 1500, 3500)  # Space character
}

root = Tk()
root.title("DSP project")
root.geometry("850x450+220+120")
root.resizable(False, False)
root.configure(bg="#3776ab")

engine = pyttsx3.init()


def generate_sine_wave(frequencies, duration_ms):
    # Calculate sample rate and duration in samples
    sample_rate = 44100  # Common audio sampling rate
    duration_samples = int(duration_ms * sample_rate / 1000)

    # Create time vector
    t = np.linspace(0, duration_ms / 1000, duration_samples)

    # Generate combined sine wave signal
    signal = np.sin(2 * np.pi * frequencies[0] * t)  # Low frequency component
    for freq in frequencies[1:]:
        signal += np.sin(2 * np.pi * freq * t)  # Add other components

    # Normalize signal amplitude
    signal /= np.max(np.abs(signal))

    return signal


def encode_string(text):
    full_signal = np.array([])
    for char in text:
        char_signal = encode_character(char)
        if char_signal is not None:
            full_signal = np.append(full_signal, char_signal)
    return full_signal


def encode_character(char):
    char_lower = char.lower()
    if char_lower not in CHARACTER_FREQUENCIES:
        return None  # Ignore characters not in the dictionary
    frequencies = CHARACTER_FREQUENCIES[char_lower]
    signal = generate_sine_wave(frequencies, 40)  # 40ms duration
    return signal


def GenerateSignal():
    text = inputText.get(1.0, END).lower()
    signal = encode_string(text)
    plot_signal(signal)


def EncodingFunction():
    text = inputText.get(1.0, END).lower()
    if text.strip() == "":
        return

    try:
        signal = encode_string(text)
        playAudio(signal)
        save_wav("encoded_signal.wav", signal)

    except ValueError as e:
        # Handle invalid character error (e.g., display an error message)
        print(f"Error: {e}")


def plot_signal(signal):
    plt.figure(figsize=(10, 4))
    time = np.linspace(0, len(signal) / 44100, len(signal))
    plt.plot(time, signal)
    plt.title('Encoded Signal in Time Domain')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()


def save_wav(filename, signal):
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes((signal * 32767).astype(np.int16).tobytes())


def playAudio(signal):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=True)
    stream.write(signal.astype(np.float32).tobytes())
    stream.stop_stream()
    stream.close()
    p.terminate()


def listen():
    text = inputText.get(1.0, END).lower()
    engine.say(text)
    engine.runAndWait()


iconImg1 = PhotoImage(file="mainLogo2.png")
root.iconphoto(False, iconImg1)

#header
header = Frame(root, bg="white", width=850, height=100)
header.place(x=0, y=0)

Logo = PhotoImage(file="logo1.png")
Label(header, image=Logo, bg="white").place(x=6, y=7)
Label(header, text="EchoAlphaEncoder", font="Helvetica 18 bold", bg="white", fg="#333", padx=10, pady=10).place(x=90, y=27)

inputText = Text(root, font="arial 14", bg="white", relief=GROOVE, wrap=WORD)
inputText.place(x=10, y=150, width=350, height=130)

icon2=PhotoImage(file="mainLogo2.png")
button1=Button(root, text="convert",compound=LEFT,  image=icon2, width=130, font="arial 14 ", command= EncodingFunction)
button1.place(x=30, y= 330)

iconSave=PhotoImage(file="save2.png")
button2=Button(root, text="save",compound=LEFT,  image=iconSave, width=130, font="arial 14 ")
button2.place(x=200, y= 330)

button3 = Button(root, text="Generate Signal", width=15, font="arial 14", command=GenerateSignal)
button3.place(x=500, y= 160)

button4 = Button(root, text="Listen", width=15, font="arial 14", command=listen)
button4.place(x=500, y= 230)


root.mainloop()