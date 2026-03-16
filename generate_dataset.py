import cv2
import os

# --- CHANGE IS HERE ---
# cv2.CAP_DSHOW add kiya hai taaki Windows error fix ho jaye
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(3, 640) # Width
cam.set(4, 480) # Height

# Face Detector load karein
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# User ID (1 for Yash)
face_id = 1

print("\n [INFO] Initializing face capture. Look at the camera and wait...")

count = 0
while(True):
    ret, img = cam.read()
    
    # Agar camera frame nahi padh pa raha, to loop break karein
    if not ret:
        print("[ERROR] Cannot read frame. Camera index might be wrong.")
        break
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
        count += 1

        # Save image
        if not os.path.exists('samples'):
            os.makedirs('samples')
            
        cv2.imwrite("samples/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
        cv2.imshow('image', img)

    k = cv2.waitKey(100) & 0xff 
    if k == 27: # Press 'ESC' to stop
        break
    elif count >= 100: # 100 photos lene ke baad ruk jaye
        break

print("\n [INFO] Exiting Program.")
cam.release()
cv2.destroyAllWindows()