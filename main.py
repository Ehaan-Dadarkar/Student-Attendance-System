from customtkinter import *
from PIL import Image, ImageTk
import cv2 as cv
import face_recognition
import numpy as np
import csv
import os
from datetime import datetime


name_image = face_recognition.load_image_file('file_path')
name_encoding = face_recognition.face_encodings(name_image)[0]


known_face_encodings = [name_encoding]
known_face_names = ["name"]


now = datetime.now()
current_date = now.strftime("%Y-%m-%d")
filename = f"attendance_{current_date}.csv"
recorded_students = set()

if os.path.exists(filename):
    with open(filename, "r") as f:
        reader = csv.reader(f)
        next(reader, None) 
        for row in reader:
            if row:
                recorded_students.add(row[0])

if not os.path.exists(filename) or os.stat(filename).st_size == 0:
    with open(filename, "w", newline="") as f:
        lnwriter = csv.writer(f)
        lnwriter.writerow(["Name", "Time"])

video_capture = None

def update_video():
    global video_capture
    if video_capture is not None:
        ret, frame = video_capture.read()
        if ret:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)
        video_label.after(10, update_video)

def capture_and_match():
    global video_capture
    if video_capture is None:
        print("Video is not running.")
        return

    ret, frame = video_capture.read()
    if not ret:
        print("Failed to capture image.")
        return

    small_frame = cv.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv.cvtColor(small_frame, cv.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distance = face_recognition.face_distance(known_face_encodings, face_encoding)

        name = "Unknown"

        if any(matches):  
            best_match_index = np.argmin(face_distance)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                result_label_final(name)

        if name != "Unknown" and name not in recorded_students:
            current_time = datetime.now().strftime("%H:%M:%S")
            with open(filename, "a", newline="") as f:
                lnwriter = csv.writer(f)
                lnwriter.writerow([name, current_time])
            recorded_students.add(name)

def start_video():
    global video_capture
    if video_capture is None or not video_capture.isOpened():
        video_capture = cv.VideoCapture(0)
        update_video()

def stop_video():
    global video_capture  

    if video_capture is not None:
        video_capture.release()  
        video_capture = None  
        
    cv.destroyAllWindows()
    

    placeholder_image = create_image(640, 480, "gray")
    video_label.configure(image=placeholder_image)
    video_label.imgtk = placeholder_image  # Prevent garbage collection


    result_label.configure(text=" ")

    # Force UI update to apply changes
    root.update_idletasks()


def create_image(width, height, clr):
    creating_image = Image.new("RGB", (width, height), clr)
    return ImageTk.PhotoImage(creating_image)

def result_label_final(name):
    result_label.configure(text=f"{name} is Present", text_color="green", height=2, width=20)

root = CTk()
root.title("Face Recognition")
root.geometry("1280x720")

root_label = CTkLabel(root, text="Student Attendance System", font=("Arial", 38, "bold"), anchor="center")
root_label.pack(pady=50)  

line = CTkCanvas(root, width=1920, height=2, bg="black", highlightthickness=0)
line.create_line(0, 1, 1920, 1, fill="white", width=2) 
line.place(x=0, y=150)  

video_image = create_image(640, 480, "gray")
video_label = CTkLabel(root, image=video_image, text="")
video_label.place(x=400, y=300)

start_button = CTkButton(root, text="Start Video", font=("Arial", 16, "bold"), fg_color="green", text_color="white", corner_radius=15, height=50, width=200, command=start_video)
start_button.place(x=1350, y=350)

capture_button = CTkButton(root, text="Capture & Match", font=("Arial", 16, "bold"), fg_color="blue", text_color="white", corner_radius=15, height=50, width=200, command=capture_and_match)
capture_button.place(x=1350, y=450)

stop_button = CTkButton(root, text="Stop Video", font=("Arial", 16, "bold"), fg_color="gray30", text_color="white", corner_radius=15, height=50, width=200, command=stop_video)
stop_button.place(x=1350, y=550)

result_image = create_image(280, 50, "white")
result_label = CTkLabel(root, text="", font=("Arial", 32, "bold"), image=result_image, text_color="green", height=2, width=20)
result_label.place(x=575, y=850)

exit_button = CTkButton(root, text="Exit", font=("Arial", 16, "bold"), fg_color="red", text_color="white", corner_radius=15, height=50, width=200, command=root.destroy)
exit_button.place(x=1350, y=650)

root.mainloop()
