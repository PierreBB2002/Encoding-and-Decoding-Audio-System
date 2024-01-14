#phase 1
from tkinter import *
from tkinter.ttk import Combobox
import pyttsx3
import numpy as np
import wave
import pyaudio
import matplotlib.pyplot as plt
from tkinter import filedialog  # Import filedialog for opening/saving files

publicVar = 0
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
    ' ': (500, 1500, 3500)
}

root = Tk()
root.title("DSP project")
root.geometry("850x450+220+120")
root.resizable(False, False)
root.configure(bg="#3776ab")

engine = pyttsx3.init()
full_signal = []


def clear():
    global full_signal
    full_signal = np.array([])


def plotSignal():
    plt.figure(figsize=(10, 4))
    time = np.linspace(0, len(full_signal) / 8000, len(full_signal))
    plt.plot(time, full_signal)
    plt.title('Encoded Signal in Time Domain')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()


def saveWave():
    file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
    if file_path:
        with wave.open(file_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(8000)
            wf.writeframes((full_signal * 32767).astype(np.int16).tobytes())


def encoding():
    global full_signal
    text = inputText.get(1.0, END).lower()
    text = text.replace("\n", "")
    if text.strip() == "":
        return

    for char in text:
        getChar = char.lower()
        if getChar not in CHARACTER_FREQUENCIES:
            print(getChar + ": Invalid Input")
            continue
        freq = CHARACTER_FREQUENCIES[getChar]
        sampleRate = 8000
        n = np.arange(0, 320)
        sinusoidalSignal_1 = np.sin(2*np.pi*freq[0]*n / sampleRate)
        sinusoidalSignal_2 = np.sin(2 * np.pi * freq[1] * n / sampleRate)
        sinusoidalSignal_3 = np.sin(2 * np.pi * freq[2] * n / sampleRate)

        finalSignal = sinusoidalSignal_1 + sinusoidalSignal_2 + sinusoidalSignal_3
        finalSignal /= np.max(np.abs(finalSignal))
        full_signal = np.append(full_signal, finalSignal)

        # Add a silent period (zeros) to introduce a delay
        silent_period = np.zeros(int(0.2 * sampleRate))  # 0.3 seconds of silence
        full_signal = np.append(full_signal, silent_period)

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32, channels=1, rate=8000, output=True)
        stream.write(finalSignal.astype(np.float32).tobytes())
        stream.stop_stream()
        stream.close()
        p.terminate()


iconImg1 = PhotoImage(file="mainLogo2.png")
root.iconphoto(False, iconImg1)

# header
header = Frame(root, bg="white", width=850, height=100)
header.place(x=0, y=0)

Logo = PhotoImage(file="logo1.png")
Label(header, image=Logo, bg="white").place(x=6, y=7)
Label(header, text="EchoAlphaEncoder", font="Helvetica 18 bold", bg="white", fg="#333", padx=10, pady=10).place(x=90, y=27)

inputText = Text(root, font="arial 14", bg="white", relief=GROOVE, wrap=WORD)
inputText.place(x=10, y=150, width=350, height=130)

icon2 = PhotoImage(file="mainLogo2.png")
button1 = Button(root, text="convert", compound=LEFT, image=icon2, width=130, font="arial 14 ", command=encoding)
button1.place(x=30, y=330)

iconSave = PhotoImage(file="save2.png")
button2 = Button(root, text="save", compound=LEFT, image=iconSave, width=130, font="arial 14 ", command=saveWave)
button2.place(x=200, y=330)

button3 = Button(root, text="Generate Signal", width=15, font="arial 14", command=plotSignal)
button3.place(x=500, y=160)

button4 = Button(root, text="Restart", width=15, font="arial 14", command=clear)
button4.place(x=500, y=230)

root.mainloop()
