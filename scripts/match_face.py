import face_recognition
import pickle
import os

def match_face_with_user(username, image):
    known_faces_path = "scripts/known_faces"
    file_path = os.path.join(known_faces_path, f"{username}.pkl")

    if not os.path.exists(file_path):
        print("User face not found!")
        return False

    with open(file_path, "rb") as f:
        known_encoding = pickle.load(f)

    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        print("No face detected in input.")
        return False

    input_encoding = face_recognition.face_encodings(image, face_locations)[0]

    match_result = face_recognition.compare_faces([known_encoding], input_encoding)
    return match_result[0]
