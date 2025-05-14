import cv2
import face_recognition  # We can use this to compare fingerprints as images for now

def match_fingerprint(username):
    registered_path = f"finger_auth/static/fingerprints/{username}.png"

    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()

    if ret:
        # Save and compare as images
        live_path = "temp_fingerprint.png"
        cv2.imwrite(live_path, frame)

        img1 = face_recognition.load_image_file(registered_path)
        img2 = face_recognition.load_image_file(live_path)

        try:
            result = face_recognition.compare_faces([face_recognition.face_encodings(img1)[0]], face_recognition.face_encodings(img2)[0])
            return result[0]
        except:
            return False
    return False
