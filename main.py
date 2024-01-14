from tkinter import *
from tkinter.ttk import Combobox
import pyttsx3
import numpy as np
import wave
import pyaudio
import matplotlib.pyplot as plt
from tkinter import filedialog
import scipy.io.wavfile as wav
from scipy.fft import fft
from scipy.signal import find_peaks
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


def uploadAudio():
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if file_path:
        # Process the selected audio file (you can add decoding logic here)
        print("Selected file:", file_path)
        decodingFFT(file_path)


def display_result(result):
    resultText.delete(1.0, END)
    resultText.insert(END, result)


def decodingFFT(filePath):
    # Read the WAV file
    rate, data = wav.read(filePath)
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
            if len(freqs) == 0:
                continue  # No frequencies found, move to the next chunk

            matching_freqs = [all(np.isclose(freq, freq_set, atol=10.0)) for freq in freqs]
            if any(matching_freqs):
                decoded_text += char
                print(char)
                break

    display_result(decoded_text)


root = Tk()
root.title("DSP project")
root.geometry("850x450+220+120")
root.resizable(False, False)
root.configure(bg="#3776ab")

iconImg1 = PhotoImage(file="mainLogo2.png")
root.iconphoto(False, iconImg1)

#header
header = Frame(root, bg="white", width=850, height=100)
header.place(x=0, y=0)

Logo = PhotoImage(file="logo1.png")
Label(header, image=Logo, bg="white").place(x=6, y=7)
Label(header, text="EchoAlphaEncoder", font="Helvetica 18 bold", bg="white", fg="#333", padx=10, pady=10).place(x=90, y=27)

button5 = Button(root, text="Upload Audio", width=15, font="arial 14", command=uploadAudio)
button5.place(x=500, y=290)

icon2=PhotoImage(file="mainLogo2.png")
button1=Button(root, text="convert", compound=LEFT,  image=icon2, width=130, font="arial 14 ")
button1.place(x=30, y= 330)

iconSave=PhotoImage(file="save2.png")
button2=Button(root, text="save",compound=LEFT,  image=iconSave, width=130, font="arial 14 ")
button2.place(x=200, y= 330)

button3 = Button(root, text="Generate Signal", width=15, font="arial 14")
button3.place(x=500, y= 160)

button4 = Button(root, text="Restart", width=15, font="arial 14")
button4.place(x=500, y= 230)

resultText = Text(root, font="arial 14", bg="white", relief=GROOVE, wrap=WORD)
resultText.place(x=10, y=170, width=350, height=60)


root.mainloop()
