# phase2
from tkinter import *
from tkinter import filedialog

import numpy as np
import scipy.io.wavfile as wav
from scipy.fft import fft
from scipy.signal import butter, lfilter
from scipy.signal import find_peaks

# frequency analysis
arr = np.array([])
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
        global arr
        # Apply Fourier Transform to each chunk
        yf = fft(chunk)
        # Get the absolute values of the frequencies
        spectrum = np.abs(yf[:len(yf) // 2])
        # Determine a threshold for peak height dynamically based on the max amplitude
        threshold = np.max(spectrum) * 0.5  # Adjust the multiplier as needed

        # Find peaks to determine the three main frequencies
        peaks, _ = find_peaks(spectrum, height=threshold)

        # Get the frequencies corresponding to the peaks
        freqs = peaks * rate / len(chunk)
        arr = np.append(arr, freqs)

        # Check if we found at least three peaks, which we need for a valid character encoding
        if len(freqs) < 3:
            continue  # Skip this chunk as it doesn't contain enough frequency components

        for char, freq_set in CHARACTER_FREQUENCIES.items():
            if len(freqs) == 0:
                continue  # No frequencies found, move to the next chunk

    for i in range(0, len(arr)):
        for char in CHARACTER_FREQUENCIES.keys():
            if (CHARACTER_FREQUENCIES[char][0] == arr[i] and
                    CHARACTER_FREQUENCIES[char][1] == arr[i+1] and
                    CHARACTER_FREQUENCIES[char][2] == arr[i+2]):
                decoded_text += char
    display_result(decoded_text)

# bandpass Filters analysis
def bandpass_filter(signal, sample_rate, frequencies):
    """
    Apply bandpass filters to the signal and return filtered signals for each frequency.

    Args:
        signal (numpy.ndarray): Input audio signal.
        sample_rate (int): Sampling rate of the audio signal.
        frequencies (list): List of center frequencies for the bandpass filters.

    Returns:
        filtered_signals (list): List of filtered signals for each frequency.
    """
    filtered_signals = []

    for center_freq in frequencies:
        # Define filter parameters (adjust as needed)
        lowcut = center_freq - 50  # Lower cutoff frequency
        highcut = center_freq + 50  # Upper cutoff frequency
        nyquist = 0.5 * sample_rate
        low = lowcut / nyquist
        high = highcut / nyquist
        order = 2  # Filter order, using a lower order for a less steep roll-off

        # Design the bandpass filter
        b, a = butter(order, [low, high], btype='band')

        # Apply the filter to the signal
        filtered_signal = lfilter(b, a, signal)

        # Append the filtered signal to the list
        filtered_signals.append(filtered_signal)

    return filtered_signals


def decode_filtered_signals(filtered_signals, character_frequencies, rate, chunk_length):
    decoded_text = ''
    for signal in filtered_signals:
        # Apply Fourier Transform to the filtered signal
        yf = fft(signal)
        spectrum = np.abs(yf[:len(yf) // 2])
        freqs = np.linspace(0, rate / 2, len(spectrum))

        # Find peaks in the spectrum
        peaks, _ = find_peaks(spectrum, height=np.max(spectrum) * 0.5)

        # Check against character frequencies
        for char, freq_set in character_frequencies.items():
            if all(any(np.isclose(freq, f, atol=rate/chunk_length) for f in freq_set) for freq in peaks):
                decoded_text += char
                break  # Character found

    return decoded_text



def decodingBandpass(filePath):
    rate, data = wav.read(filePath)
    if data.ndim > 1:
        data = data[:, 0]  # If stereo, just use one channel

    char_duration_samples = int(rate * 0.04)  # 40ms of samples
    chunks = [data[i:i + char_duration_samples] for i in range(0, len(data), char_duration_samples)]

    decoded_text = ''

    for chunk in chunks:
        # Apply bandpass filters for each character frequency
        filtered_signals = bandpass_filter(chunk, rate, [f for freqs in CHARACTER_FREQUENCIES.values() for f in freqs])

        # Decode the characters from the filtered signals
        decoded_chunk = decode_filtered_signals(filtered_signals, CHARACTER_FREQUENCIES, rate, len(chunk))
        decoded_text += decoded_chunk

    display_result(decoded_text)


root = Tk()
root.title("DSP project")
root.geometry("850x450+220+120")
root.resizable(False, False)
root.configure(bg="#3776ab")

iconImg1 = PhotoImage(file="mainLogo2.png")
root.iconphoto(False, iconImg1)

# header
header = Frame(root, bg="white", width=850, height=100)
header.place(x=0, y=0)

Logo = PhotoImage(file="logo1.png")
Label(header, image=Logo, bg="white").place(x=6, y=7)
Label(header, text="EchoAlphaEncoder", font="Helvetica 18 bold", bg="white", fg="#333", padx=10, pady=10).place(x=90,
                                                                                                                y=27)

button5 = Button(root, text="Upload Audio", width=15, font="arial 14", command=uploadAudio)
button5.place(x=500, y=290)

icon2 = PhotoImage(file="mainLogo2.png")
button1 = Button(root, text="convert", compound=LEFT, image=icon2, width=130, font="arial 14 ")
button1.place(x=30, y=330)

iconSave = PhotoImage(file="save2.png")
button2 = Button(root, text="save", compound=LEFT, image=iconSave, width=130, font="arial 14 ")
button2.place(x=200, y=330)

button3 = Button(root, text="Generate Signal with Frequency Analysis", width=15, font="arial 14")
button3.place(x=500, y=160)

button_bandpass = Button(root, text="Generate Signal with Bandpass Filter", width=15, font="arial 14")
button_bandpass.place(x=350, y=330)

button4 = Button(root, text="Restart", width=15, font="arial 14")
button4.place(x=500, y=230)

resultText = Text(root, font="arial 14", bg="white", relief=GROOVE, wrap=WORD)
resultText.place(x=10, y=170, width=350, height=60)

root.mainloop()
