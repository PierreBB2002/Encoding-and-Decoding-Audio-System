from tkinter import *
from tkinter.ttk import Combobox
import pyttsx3
import numpy as np
import wave
import pyaudio
import matplotlib.pyplot as plt
from tkinter import filedialog
import scipy.fft
from scipy.io import wavfile
from scipy.fft import fft
from scipy.signal import find_peaks
from scipy.signal import butter, sosfilt, sosfreqz


#phase one
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
# Function to upload a file and display the path in the text box


#phase two

def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if file_path:
        inputText.delete(1.0, END)  # Clear the text box if there's any text
        inputText.insert(END, file_path)  # Show the file path in the text box


def decode_using_fourier(file_path):
    # Read the WAV file
    rate, data = wavfile.read(file_path)
    if data.ndim > 1:
        data = data[:, 0]  # If stereo, just use one channel

    # The duration of each character in samples
    char_duration_samples = int(rate * 0.04)  # 40ms of samples

    # Split the signal into 40ms chunks
    chunks = [data[i:i + char_duration_samples] for i in range(0, len(data), char_duration_samples)]

    decoded_text = ''

    for chunk in chunks:
        # Apply Fourier Transform to each chunk
        yf = fft(chunk)
        # Get the absolute values of the frequencies
        spectrum = np.abs(yf[:len(yf) // 2])
        # Find peaks to determine the three main frequencies
        peaks, _ = find_peaks(spectrum, height=rate // 20)

        # Get the frequencies corresponding to the peaks
        freqs = peaks * rate / len(chunk)

        # Match the frequencies to the character frequencies
        for char, freq_set in CHARACTER_FREQUENCIES.items():
            if all(np.isclose(freq, freq_set, atol=10.0) for freq in freqs):
                decoded_text += char
                break

    display_result(decoded_text)


# Helper function to create a bandpass filter
def butter_bandpass(lowcut, highcut, fs, order=5):
    sos = butter(order, [lowcut, highcut], btype='bandpass', fs=fs, output='sos')
    return sos


# Helper function to apply a bandpass filter to a signal
def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sosfilt(sos, data)
    return y


# Function to decode an audio signal using bandpass filters
def decode_using_filters(file_path):
    rate, data = wavfile.read(file_path)
    if data.ndim > 1:
        data = data[:, 0]  # If stereo, just use one channel

    char_duration_samples = int(rate * 0.04)  # 40ms of samples
    chunks = [data[i:i + char_duration_samples] for i in range(0, len(data), char_duration_samples)]

    decoded_text = ''

    for chunk in chunks:
        energies = {}
        for char, freqs in CHARACTER_FREQUENCIES.items():
            # Apply bandpass filter for each frequency
            filtered_signal = np.zeros_like(chunk)
            for freq in freqs:
                lowcut = freq - 10.0
                highcut = freq + 10.0
                filtered_signal += butter_bandpass_filter(chunk, lowcut, highcut, rate, order=2)

            # Calculate the energy of the filtered signal
            energy = np.sum(filtered_signal ** 2)
            energies[char] = energy

        # Find the character with the highest energy
        decoded_char = max(energies, key=energies.get)
        decoded_text += decoded_char

    display_result(decoded_text)

# Function to display the decoding result
def display_result(result):
    resultText.delete(1.0, END)
    resultText.insert(END, result)

# Add a button to upload files
upload_button = Button(root, text="Upload WAV File", command=upload_file)
upload_button.place(x=400, y= 330)

# Add a text box to display the decoding result
resultText = Text(root, font="arial 14", bg="white", relief=GROOVE, wrap=WORD)
resultText.place(x=10, y=380, width=350, height=60)


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

# Button for decoding using Fourier transform
button_fourier = Button(root, text="Decode with Fourier", width=20, font="arial 14", command=lambda: decode_using_fourier(inputText.get(1.0, END).strip()))
button_fourier.place(x=500, y= 330)

# Button for decoding using bandpass filters
button_filters = Button(root, text="Decode with Filters", width=20, font="arial 14", command=lambda: decode_using_filters(inputText.get(1.0, END).strip()))
button_filters.place(x=500, y= 380)


root.mainloop()
