import cv2
import numpy as np
from PIL import Image
import os

# Path for face image database
path = 'samples'

# Recognizer aur Detector initialize karein
recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Function to get the images and label data
def getImagesAndLabels(path):
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []

    print(f"\n [INFO] Training faces. This will take a few seconds. Please wait...")

    for imagePath in imagePaths:
        # Image ko grayscale mein convert karein
        PIL_img = Image.open(imagePath).convert('L') 
        img_numpy = np.array(PIL_img, 'uint8')

        # Filename se ID nikalna (User.1.1.jpg -> ID = 1)
        try:
            id = int(os.path.split(imagePath)[-1].split(".")[1])
        except:
            continue # Agar filename format galat ho to skip karein

        faces = detector.detectMultiScale(img_numpy)

        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)

    return faceSamples,ids

# --- Main Execution ---
try:
    faces, ids = getImagesAndLabels(path)
    
    # Model train karein
    recognizer.train(faces, np.array(ids))

    # Model ko file mein save karein
    # Note: 'trainer' folder hona chahiye ya hum root mein save kar rahe hain
    recognizer.write('trainer.yml') 

    print(f"\n [INFO] {len(np.unique(ids))} faces trained. Exiting Program")

except Exception as e:
    print(f"\n [ERROR] Training failed: {e}")