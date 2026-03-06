import warnings
warnings.filterwarnings("ignore")
from flask import Flask, render_template, Response
import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime
import csv

app = Flask(__name__)

camera = cv2.VideoCapture(0)

def load_encoding(path):
    img = face_recognition.load_image_file(path)
    return face_recognition.face_encodings(img)[0]
try:
    EmanEncoding = load_encoding("Images/Eman.jpg")
    TahirEncoding = load_encoding("Images/Tahir.jpg")
    TahirEncoding1 = load_encoding("Images/Tahir1.jpg")
    NalainEncoding = load_encoding("Images/Nalain.jpg")
    MoheezEncoding = load_encoding("Images/Moheez.jpg")
    RameeshaEncoding = load_encoding("Images/Rameesha.jpg")
    AsimEncoding = load_encoding("Images/Asim.jpg")
    AhmedEncoding = load_encoding("Images/Ahmed.jpg")
    UmerEncoding = load_encoding("Images/Umer.jpg")
except FileNotFoundError as e:
    print(f"Error loading images: {e}")

known_face_encodings = [
    EmanEncoding, TahirEncoding, TahirEncoding1, NalainEncoding,
    MoheezEncoding, RameeshaEncoding, AsimEncoding, AhmedEncoding, UmerEncoding
]

known_face_names = [
    "Eman","Tahir", "Tahir", "Nalain",
    "Moheez", "Rameesha", "Asim", "Ahmed", "Umer"
]

students_to_mark = list(set(known_face_names))
marked_students = [] 

now = datetime.now()
current_date = now.strftime("%Y-%m-%d")
csv_filename = f"{current_date}.csv"

if not os.path.exists(csv_filename):
    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Time'])

def mark_attendance(name):
    """Attendance CSV aur List mein update karega"""
    if name in students_to_mark:
        students_to_mark.remove(name)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        with open(csv_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([name, current_time])

        marked_students.append({'name': name, 'time': current_time})
        print(f"MARKED PRESENT: {name}")

def generate_frames():
    """Video Feed Generator with Frame Skipping Optimization"""
    frame_count = 0  
    face_locations = []
    face_names = []

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            if frame_count % 5 == 0:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
                    name = "Unknown"
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                        mark_attendance(name)
                    
                    face_names.append(name)

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

            frame_count += 1 

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@app.route('/')
def index():
    """Home Page"""
    return render_template('index.html', attendance_list=marked_students, date=current_date)

@app.route('/video_feed')
def video_feed():
    """Video Streaming Route"""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)