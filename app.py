from flask import Flask, jsonify, request, abort
from flask_apscheduler import APScheduler
import cv2
import time
import os
from datetime import datetime
import requests
import json

app = Flask(__name__)
sched = APScheduler()
imagePath = "./capture"

# Define the URL of the Flask endpoint
url = 'https://www.pest-advisor.com/xxx'

@app.route("/")
def index():
    abort(403, "(403) Incorrect use of device!")


# https://legal-mastiff-optimal.ngrok-free.app/capture?username=Gvtone
@app.route('/capture', methods=['GET', 'POST'])
def capture():
    if not os.path.exists("settings.json"):
        abort(403, "(403) Device not set properly!")

    with open('settings.json', 'r') as openfile:
        jsonData = json.load(openfile)
        user = jsonData["username"]
        focus = jsonData["focus"]

    username = request.args.get('username')
    if username != user:
        abort(401)
    
    # Create a directory called 'capture' if it doesn't exist
    if not os.path.exists("capture"):
        os.makedirs("capture")

    if len(imagePath) != 0:
        for item in os.listdir(imagePath):
            item_path = os.path.join(imagePath, item)
            os.remove(item_path)
    
    # Initialize the camera
    cap = cv2.VideoCapture(1)  # 0 represents the default camera (usually the built-in webcam)

    # Sets camera to its max resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2592)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1944)

    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_FOCUS, focus) # min: 0, max: 255, increment:5

    if not cap.isOpened():
        imageInfo = {"status": "Fail", "type": "Request"}
        requests.post(url, data=imageInfo)
        return

    # Capture a frame
    for _ in range(5):
        time.sleep(1)
        ret, frame = cap.read()

    if not ret:
        imageInfo = {"status": "Fail", "type": "Request"}
        requests.post(url, data=imageInfo)
        return
    
    # Generate a unique filename or use a timestamp
    dateTime = datetime.now().strftime("%Y-%m-%d %H-%M")
    imageDate = datetime.now().strftime("%Y-%m-%d")
    imageTime = datetime.now().strftime("%H:%M:%S")
    filename = dateTime + ".png"

    # Save the frame as an image inside the 'capture' directory
    cv2.imwrite(os.path.join('capture', filename), frame)

    # Release the camera
    cap.release()

    # Define the image file you want to upload
    image_filename = 'capture/' + filename

    # Create a dictionary with the file data
    files = {'image': open(image_filename, 'rb')}
    
    imageInfo = {"status": "Success",
                    "type": "Request",
                    "user": f"{user}",
                    "url": "xxx",
                    "date": f"{imageDate}",
                    "time": f"{imageTime}"}

    data = {'data': json.dumps(imageInfo)}
    requests.post(url, files=files, data=data)

    return jsonify({"message": "Image successfully transfered!"})

@app.route('/setuser', methods=['GET', 'POST'])
def setuser():
    query = request.args
    if not query:
        abort(401)

    username = query['username']
    if username is None or username == '':
        abort(405, "No username given!")

    if 'focus' in query.keys():
        focus = query['focus']
    else:
        focus = float(100) # CHANGE DEFAULT LATER

    data = {"username": f"{username}", "focus": focus}
    jsonData = json.dumps(data, indent=4)
    
    with open("settings.json", "w") as outfile:
        outfile.write(jsonData)
        
    return jsonify({"success": "Device linked!"})

def grab():
    if not os.path.exists("settings.json"):
        return

    with open('settings.json', 'r') as openfile:
        jsonData = json.load(openfile)
        user = jsonData["username"]
        focus = jsonData["focus"]

    # Create a directory called 'capture' if it doesn't exist
    if not os.path.exists("capture"):
        os.makedirs("capture")

    if len(imagePath) != 0:
        for item in os.listdir(imagePath):
            item_path = os.path.join(imagePath, item)
            os.remove(item_path)

    # Initialize the camera
    cap = cv2.VideoCapture(1)  # 0 represents the default camera (usually the built-in webcam)

    # Sets camera to its max resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2592)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1944)

    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_FOCUS, focus) # min: 0, max: 255, increment:5

    if not cap.isOpened():
        imageInfo = {"status": "Fail", "type": "Schedule"}
        requests.post(url, data=imageInfo)
        return

    # Capture a frame
    for _ in range(5):
        time.sleep(1)
        ret, frame = cap.read()

    if not ret:
        imageInfo = {"status": "Fail", "type": "Schedule"}
        requests.post(url, data=imageInfo)
        return
    
    # Generate a unique filename or use a timestamp
    dateTime = datetime.now().strftime("%Y-%m-%d %H-%M")
    imageDate = datetime.now().strftime("%Y-%m-%d")
    imageTime = datetime.now().strftime("%H:%M:%S")
    filename = dateTime + ".png"

    # Save the frame as an image inside the 'capture' directory
    cv2.imwrite(os.path.join('capture', filename), frame)

    # Release the camera
    cap.release()

    # Define the image file you want to upload
    image_filename = 'capture/' + filename

    # Create a dictionary with the file data
    files = {'image': open(image_filename, 'rb')}
    
    imageInfo = {"status": "Success",
                    "type": "Schedule",
                    "user": f"{user}",
                    "url": "legal-mastiff-optimal.ngrok-free.app",
                    "date": f"{imageDate}",
                    "time": f"{imageTime}"}

    data = {'data': json.dumps(imageInfo)}
    requests.post(url, files=files, data=data)

    print("Image sent!")

if __name__ == "__main__":
    with app.app_context():
        sched.add_job(id="1", func=grab, trigger="cron", day_of_week="mon-sun", hour="8", minute="0")
        sched.start()
        app.run(debug=True, host="0.0.0.0")
