from tkinter import *
from tkinter.ttk import Combobox
import pyttsx3

root = Tk()
root.title("DSP project")
root.geometry("850x450+220+120")
root.resizable(False, False)
root.configure(bg="#3776ab")

engine = pyttsx3.init()


def EncodingFunction():
    text = inputText.get(1.0, END)
    voices = engine.getProperty('voices')
    engine.say(text)
    engine.runAndWait()


#app icon
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

label1 = Button(root, text="Generate Signal", font="arial 14", fg="black", width=17)
label1.place(x=480, y=160)

label2 = Button(root, text="Listen", font="arial 14", fg="black", width=17)
label2.place(x=480, y=230)

icon2=PhotoImage(file="mainLogo2.png")
button1=Button(root, text="convert",compound=LEFT,  image=icon2, width=130, font="arial 14 ", command= EncodingFunction)

iconSave=PhotoImage(file="save2.png")
button2=Button(root, text="save",compound=LEFT,  image=iconSave, width=130, font="arial 14 ")
button2.place(x=210, y= 340)

root.mainloop()