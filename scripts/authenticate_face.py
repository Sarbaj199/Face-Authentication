import cv2
import face_recognition
import pickle
import os
import sys

def authenticate_user(username):
    file_path = f"known_faces/{username}.pkl"

    # Check if user exists
    if not os.path.exists(file_path):
        print(f"No face data found for user: {username}")
        sys.exit(1)
    
    with open(file_path, "rb") as f:
        saved_encoding = pickle.load(f)

    video = cv2.VideoCapture(0)
    print("Authenticating... Please look at the camera.")

    authenticated = False

    while True:
        ret, frame = video.read()
        if not ret:
            continue

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            # Compare the current face with saved one
            results = face_recognition.compare_faces([saved_encoding], face_encoding)
            if results[0]:
                authenticated = True
                break

        cv2.imshow("Press Q to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or authenticated:
            break

    video.release()
    cv2.destroyAllWindows()

    if authenticated:
        print(f"✅ Authentication successful. Welcome, {username}!")
    else:
        print("❌ Authentication failed.")

if __name__ == "__main__":
    username = input("Enter your username: ").strip()
    authenticate_user(username)
