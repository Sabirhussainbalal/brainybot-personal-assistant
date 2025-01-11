import tkinter as tk
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import speech_recognition as sr
from tkinter import Canvas, Scrollbar
from PIL import Image, ImageTk
import tkinter.font as tkFont
import pyttsx3, time, os, threading, webbrowser, subprocess






class VoiceRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("BrainyBot")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # Load and resize background image
        bg_image = Image.open("bg.jpg")
        bg_image = bg_image.resize((500, 400), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)  # Keep reference to bg_photo
        
        # Set window icon
        icon = Image.open("icon.ico")  # Replace with your PNG file path
        icon = ImageTk.PhotoImage(icon)  # Convert to Tkinter-compatible format
        self.root.iconphoto(True, icon)  # Set as the window icon

        # Create Canvas for background image
        self.canvas = Canvas(root, width=500, height=400, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        

        # Add background image to canvas
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Create a label and center it
        self.label = tk.Label(root, text="BrainyBot: Your Personal Assistant", font=("Helvetica", 14, "bold"), fg="#2c3e50")

        # Add padding
        self.label.config(padx=10, pady=5)

        # Create a custom font for bold part
        bold_font = tkFont.Font(weight="bold")

        # Change font for specific text parts
        self.label.config(font=("Helvetica", 14))

        # Apply the bold style for specific parts of the text manually
        # You may need to experiment with your own formatting to control bold placement
        self.label_window = self.canvas.create_window(250, 60, window=self.label)


        # Buttons: Add them to the canvas using create_window
        self.record_button = tk.Button(
            root, text="Start...", command=self.start_recording_thread, width=15, bg="white", fg="black"
        )
        self.record_button_window = self.canvas.create_window(190, 130, window=self.record_button)

        self.stop_button = tk.Button(
            root, text="Stop and Save", command=self.stop_recording, width=15, bg="white", fg="black", state=tk.DISABLED
        )
        self.stop_button_window = self.canvas.create_window(310, 130, window=self.stop_button)

        self.fs = 44100  # Sample rate
        self.recording = []
        self.is_recording = False
        self.filepath = "recording.wav"

        # Frame
        self.frame = tk.Frame(self.canvas, width=300, height=100, bg="white")
        self.frame_window = self.canvas.create_window(250, 250, window=self.frame)

        # Create a canvas inside the frame for scrolling
        self.scroll_canvas = Canvas(self.frame, width=280, height=80)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        # Add a scrollbar to the scroll canvas
        self.scrollbar = Scrollbar(self.frame, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create the label inside the scrollable canvas
        self.scrollable_label = tk.Label(self.scroll_canvas, text="Made by Sabir..." , font=("Helvetica", 10), fg="#2c3e50", wraplength=260)
        self.scroll_canvas.create_window(0, 0, window=self.scrollable_label, anchor="nw")

        # Update the scrollable area after adding the label
        self.scrollable_label.update_idletasks()
        self.scroll_canvas.config(scrollregion=self.scroll_canvas.bbox("all"))

    def start_recording_thread(self):
        threading.Thread(target=self.start_recording).start()

    def msg_label_func(self, color, content):
        # Ensure the color and content are valid
        self.scrollable_label.config(fg=color, text=content)



    def start_recording(self):
        self.is_recording = True
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.recording = []

        def callback(indata, frames, time, status):
            if self.is_recording:
                # Ensure proper appending to avoid misalignment
                self.recording.append(indata.copy())
            if status:
                self.msg_label_func("#ff5733", f"Status Warning: {status}")

        self.stream = sd.InputStream(samplerate=self.fs, channels=1, callback=callback, dtype="int16", blocksize=1024)
        self.stream.start()

    def stop_recording(self):
        if not self.is_recording:
            return

        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        # Convert the list of recorded chunks into a NumPy array
        audio_data = np.concatenate(self.recording, axis=0)

        # Save to file
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        write(self.filepath, self.fs, audio_data)

        # Convert to text
        self.convert_to_text()

    def convert_to_text(self):
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(self.filepath) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                self.msg_label_func("#ff5733", f"You Said: {text}")
                self.final(text)
                print("Converted Text:", text)
        except Exception as e:
            self.msg_label_func("#ff5733", f"Error converting audio to text: {e}")
            print("Error converting audio to text:", e)
    
    def convert_to_text(self):
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(self.filepath) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
                self.msg_label_func("#ff5733", f"You Said: {text}")
                self.final(text)  # Calling final method properly
                print("Converted Text:", text)
        except Exception as e:
            self.msg_label_func("#ff5733", f"Error converting audio to text: {e}")
            print("Error converting audio to text:", e)

    def ai_voice(self, text):
        self.engine = pyttsx3.init()
        if text.lower() == 'q':
            self.message = "Thank you for using this program.\nAllah Hafiz..."  # Fixed variable name
            print(self.message)  # Use the correct variable name
            self.engine.say(self.message)
            self.engine.runAndWait()
            return

        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.error_message = "Something went wrong. Please try again."
            self.engine.say(self.error_message)
            self.engine.runAndWait()
            print("Error:", e)

    def final(self, text):
        self.text = text.lower()
        if "hello" in self.text:
            self.ai_voice("Hello, how can I help you?")
        elif "goodbye" in self.text:
                self.ai_voice("Goodbye! Have a nice day!")
        elif "how are" in self.text:
            self.ai_voice("I'm good, thank you!")
        elif "your name" in self.text:
            self.ai_voice("My name is BrainyBot.")
        elif "who are" in self.text:
            self.ai_voice("I'm a personal AI assistant.")
        elif "what can you" in self.text:
            self.ai_voice("I can help you with various tasks and provide information.")
        elif "your purpose" in self.text:
            self.ai_voice("My purpose is to assist you with various tasks and provide information.")
        elif "open facebook" in self.text:
            self.ai_voice("Opening Facebook...")
            webbrowser.open("https://www.facebook.com")
        elif "open youtube" in self.text:
            self.ai_voice("Opening YouTube...")
            webbrowser.open("https://www.youtube.com")
        elif "open google" in self.text:
            self.ai_voice("Opening Google...")
            webbrowser.open("https://www.google.com")
        elif "open instagram" in self.text:
            self.ai_voice("Opening Instagram...")
            webbrowser.open("https://www.instagram.com")
        elif "open twitter" in self.text:
            self.ai_voice("Opening Twitter...")
            webbrowser.open("https://www.twitter.com")
        elif "open linkedin" in self.text:
            self.ai_voice("Opening LinkedIn...")
            webbrowser.open("https://www.linkedin.com")
        elif "open steam" in self.text:
            self.ai_voice("Opening Steam...")
            steam_path = r"D:\steam\steam.exe"  # Update with the correct path
            if os.path.exists(steam_path):
                subprocess.Popen(steam_path, shell=True)
            else:
                self.ai_voice("I couldn't find the Steam application. Please check the path.")
        elif "open game" in self.text:
            self.ai_voice("Opening Counter-Strike 1.6...")
            steam_cs_url = "steam://rungameid/10"  # Correct Steam game URL
            try:
                webbrowser.open(steam_cs_url)
                self.ai_voice("Counter-Strike 1.6 launched successfully!")
            except Exception as e:
                self.ai_voice(f"Failed to launch Counter-Strike 1.6. Please ensure Steam is installed and running. Error: {str(e)}")
        else:
            self.ai_voice("Sorry, I didn't understand that.")





if __name__ == "__main__":
    # Create the app
    root = tk.Tk()
    app = VoiceRecorder(root)

    root.mainloop()
