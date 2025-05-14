import cv2
import face_recognition
import pickle
import os


def capture_face(username):
    os.makedirs("known_faces", exist_ok=True)

    video = cv2.VideoCapture(0)
    print("Starting face capture. Please look at the camera...")

    face_encoding = None
    while True:
        ret, frame = video.read()
        if not ret:
            continue

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect face locations
        face_locations = face_recognition.face_locations(rgb_frame)

        print(f"[DEBUG] face_locations: {face_locations}")

        if len(face_locations) == 1:
            encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            print(f"[DEBUG] encodings: {encodings}")

            if encodings:
                face_encoding = encodings[0]
                print("Face captured successfully!")
                break
        elif len(face_locations) > 1:
            print("Multiple faces detected. Please ensure only your face is visible.")
        else:
            print("No face detected. Try adjusting your position or lighting.")

        cv2.imshow("Press Q to quit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()

    if face_encoding is not None:
        with open(f"known_faces/{username}.pkl", "wb") as f:
            pickle.dump(face_encoding, f)
        print(f"Encoding saved to known_faces/{username}.pkl")
    else:
        print("Face encoding failed.")

if __name__ == "__main__":
    username = input("Enter your username: ").strip()
    capture_face(username)
    
def save_encoded_face(username, image):
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        raise Exception("No face found in image")

    encodings = face_recognition.face_encodings(image, face_locations)

    known_faces_path = "scripts/known_faces"
    os.makedirs(known_faces_path, exist_ok=True)

    with open(f"{known_faces_path}/{username}.pkl", "wb") as f:
        pickle.dump(encodings[0], f)
