import warnings
warnings.filterwarnings("ignore")
import face_recognition
import cv2
import numpy as np
import csv
import os
from datetime import datetime

VideoCapture = cv2.VideoCapture(0)

TahirImage = face_recognition.load_image_file("Images/Tahir.jpg")
TahirEncoding = face_recognition.face_encodings(TahirImage)[0]

TahirImage1 = face_recognition.load_image_file("Images/Tahir1.jpg")
TahirEncoding1 = face_recognition.face_encodings(TahirImage1)[0]

NalainImage = face_recognition.load_image_file("Images/Nalain.jpg")
NalainEncoding = face_recognition.face_encodings(NalainImage)[0]

EmanImage = face_recognition.load_image_file("Images/Eman.jpg")
EmanEncoding = face_recognition.face_encodings(EmanImage)[0]

MoheezImage = face_recognition.load_image_file("Images/Moheez.jpg")
MoheezEncoding = face_recognition.face_encodings(MoheezImage)[0]

RameeshaImage = face_recognition.load_image_file("Images/Rameesha.jpg")
RameeshaEncoding = face_recognition.face_encodings(RameeshaImage)[0]

AsimImage = face_recognition.load_image_file("Images/Asim.jpg")
AsimEncoding = face_recognition.face_encodings(AsimImage)[0]

AhmedImage = face_recognition.load_image_file("Images/Ahmed.jpg")
AhmedEncoding = face_recognition.face_encodings(AhmedImage)[0]


UmerImage = face_recognition.load_image_file("Images/Umer.jpg")
UmerEncoding = face_recognition.face_encodings(UmerImage)[0]


known_face_encoding = [
    TahirEncoding,
    TahirEncoding1,
    NalainEncoding,
    EmanEncoding,
    MoheezEncoding,
    RameeshaEncoding,
    AsimEncoding,
    AhmedEncoding,
    UmerEncoding
]
known_faces_name = [
    "Tahir",
    "Tahir",
    "Nalain",
    "Eman",
    "Moheez",
    "Rameesha",
    "Asim",
    "Ahmed",
    "Umer",
]
students = list(set(known_faces_name.copy()))

FaceLocations = []
FaceEncodings = []
FaceNames = []
s = True

now = datetime.now()
CurrentDate = now.strftime("%Y-%m-%d")

f = open(CurrentDate+'.csv','+w',newline = '')
Inwriter = csv.writer(f)

print("Camera Active. Press 'q' to quit.") 

while True:
    _,frame = VideoCapture.read()
    SmallFrame = cv2.resize(frame,(0,0),fx=0.25,fy=0.25)
    rgbSmallFrame = np.ascontiguousarray(SmallFrame[:, :, ::-1])

    if s:
        FaceLocations = face_recognition.face_locations(rgbSmallFrame)
        FaceEncodings = face_recognition.face_encodings(rgbSmallFrame,FaceLocations)
        FaceNames = []
        for FaceEncoding in FaceEncodings:
            Matches = face_recognition.compare_faces(known_face_encoding, FaceEncoding, tolerance=0.5)
            name = ''
            FaceDistance = face_recognition.face_distance(known_face_encoding,FaceEncoding)
            BestMatchIndex = np.argmin(FaceDistance)
            if Matches[BestMatchIndex]:
                name = known_faces_name[BestMatchIndex]
            FaceNames.append(name)
            if name in known_faces_name:
                if name in students:
                    students.remove(name)
                    print(f"MARKED PRESENT: {name}") 
                    CurrentTime = now.strftime("%H-%M-%S")
                    Inwriter.writerow([name,CurrentTime])
    cv2.imshow("AttendanceSystem",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
VideoCapture.release()
cv2.destroyAllWindows()
f.close()