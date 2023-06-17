import csv
from datetime import date, datetime
import os
import face_recognition
import cv2
import numpy as np

#Globals
images_path = ''
known_face = []
known_face_encodings = []
known_face_names = []
# For Students
known_face_student = []
known_face_encodings_student = []
known_face_names_student = []
# For Admin
known_face_admin = []
known_face_encodings_admin = []
known_face_names_admin = []

list_of_names = []
face_name = ''

def set_globals(user):
    global images_path, list_of_names
    if user == 'student':
        images_path = './static/images/Student images'
    else:
        images_path = './static/images/admin'
    list_of_names = os.listdir(images_path)


def load_images_from_disk():
    for imgname in list_of_names:
        curr_image = face_recognition.load_image_file(f'{images_path}/{imgname}')
        known_face.append(curr_image)
        known_face_names.append(os.path.splitext(imgname)[0])
    print('Images Loaded')

def find_encodings():
    for face in known_face:
        face_encode = face_recognition.face_encodings(face)[0]
        known_face_encodings.append(face_encode)
    print("Encoding Done")

def generate_frame(user):
    global known_face, known_face_encodings, known_face_names
    global known_face_admin, known_face_encodings_admin, known_face_names_admin
    global known_face_student, known_face_encodings_student, known_face_names_student
    set_globals(user)
    if user == 'student':
        # print("Student, :: ", known_face_student, "face name: ", known_face_names)
        if len(known_face_student) == 0:
            known_face, known_face_encodings, known_face_names = [], [], []
            load_images_from_disk()
            find_encodings()
            known_face_student = known_face
            known_face_encodings_student = known_face_encodings
            known_face_names_student = known_face_names
        else:
            print("Already Loaded & Encoded")
            known_face = known_face_student
            known_face_encodings = known_face_encodings_student
            known_face_names = known_face_names_student
    elif user == 'admin':
        # print("Admin, :: ", known_face_admin, "face name: ", known_face_names)
        if len(known_face_admin) == 0:
            known_face, known_face_encodings, known_face_names = [], [], []
            load_images_from_disk()
            find_encodings()
            known_face_admin = known_face
            known_face_encodings_admin = known_face_encodings
            known_face_names_admin = known_face_names
        else:
            print("Already Loaded & Encoded")
            known_face = known_face_admin
            known_face_encodings = known_face_encodings_admin
            known_face_names = known_face_names_admin

    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            small_frame = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            small_frame_rgb = small_frame[:,:,::-1]

            faceloc_curr = face_recognition.face_locations(small_frame_rgb)
            faceencode_curr = face_recognition.face_encodings(small_frame_rgb)

            global face_name
            if not faceloc_curr:
                face_name = ''
            for faceloc, faceencode in zip(faceloc_curr, faceencode_curr):
                matches = face_recognition.compare_faces(known_face_encodings, faceencode)
                facedis = face_recognition.face_distance(known_face_encodings, faceencode)

                match_index = np.argmin(facedis)

                if matches[match_index]:
                    face_name = known_face_names[match_index]

                    top, right, bottom, left = faceloc
                    top, right, bottom, left = top*4, right*4, bottom*4, left*4

                    cv2.rectangle(frame, (left, top), (right, bottom), (0,0,255), 1)
                    cv2.rectangle(frame, (left, bottom-25), (right, bottom), (0,0,255), -1)
                    cv2.putText(frame, face_name, (left+6, bottom-6), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.0, (255,255,255), 1)
                
    
            print(face_name)

            retval, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def face_detected():
    if face_name != "":
        return face_name
    else:
        return ""

def mark_attendance(face_name):
    if face_name != '':
        file_path = './static/Attendance'
        try:
            with open(f'{file_path}/{str(date.today()) + ".csv"}', 'r+' ) as f:
                myattendance_list = f.readlines()
                namelist = []
                for line in myattendance_list:
                    entry = line.split(',')
                    namelist.append(entry[0])
                if face_name not in namelist:
                    now = datetime.now()
                    dt_string = now.strftime('%H:%M:%S')
                    f.writelines(f'\n{face_name},{dt_string}')
                    print("Attendance Marked")
                    return 1
                else:
                    print("Already marked")
                    return 2
        except Exception as ex:
            print("EXCEPTION OCCURED :: ", ex)
            with open(f'{file_path}/{str(date.today()) + ".csv"}', 'a' ) as f:
                obj = csv.writer(f)
                now = datetime.now()
                dt_string = now.strftime('%H:%M:%S')
                data = (face_name, dt_string)
                obj.writerow(data)
                print("Attendance Marked")
                return 1
    else:
        print("no face detected")

# if __name__ == '__main__':
#     set_globals()
#     print(images_path)
#     print(list_of_names)
    # load_images_from_disk()