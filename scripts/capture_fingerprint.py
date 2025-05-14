import cv2
import os

def capture_fingerprint(username):
    save_path = f"finger_auth/static/fingerprints/{username}.png"

    # Simulated scanner capture for now – replace with real scanner code
    cam = cv2.VideoCapture(0)
    print("Place your finger on the scanner...")
    ret, frame = cam.read()
    if ret:
        cv2.imwrite(save_path, frame)
        print("Fingerprint captured.")
    cam.release()
    return save_path
