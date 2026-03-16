import cv2

def recognize_user():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer.yml')
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    font = cv2.FONT_HERSHEY_SIMPLEX

    print("\n [INFO] Scanning Face... Look at the camera.")

    while True:
        ret, img = cam.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.2, 5)

        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

            # Debugging: Console mein dekhein ki score kya aa raha hai
            print(f"Confidence Score: {round(confidence)}") 

            # --- STRICT FIX ---
            # Pehle 85 tha, ab 50 kar diya hai. 
            # Agar score 50 se neeche hai tabhi 'Yash' maano.
            if confidence < 50:
                name = "Yash Raj"
                match_txt = "Match: {0}%".format(round(100 - confidence))
                color = (0, 255, 0) # Green for Yash
                
                cv2.putText(img, str(name), (x+5,y-5), font, 1, (255,255,255), 2)
                cv2.putText(img, str(match_txt), (x+5,y+h-5), font, 1, (255,255,0), 1)
                
                cv2.imshow('Face Verification', img)
                cv2.waitKey(1000)
                cam.release()
                cv2.destroyAllWindows()
                return True 
                
            else:
                name = "Unknown"
                match_txt = "Match: {0}%".format(round(100 - confidence))
                color = (0, 0, 255) # Red for Unknown
                
                cv2.putText(img, str(name), (x+5,y-5), font, 1, (255,255,255), 2)
                cv2.putText(img, str(match_txt), (x+5,y+h-5), font, 1, (255,255,0), 1)
                # Rectangle ka color red karein agar unknown hai
                cv2.rectangle(img, (x,y), (x+w,y+h), color, 2)

        cv2.imshow('Face Verification', img) 

        k = cv2.waitKey(10) & 0xff 
        if k == 27: 
            break

    cam.release()
    cv2.destroyAllWindows()
    return False

if __name__ == "__main__":
    if recognize_user():
        print("ACCESS GRANTED")
    else:
        print("ACCESS DENIED")