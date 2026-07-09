from flask import Flask, render_template, request, jsonify, send_from_directory
from flask import send_from_directory
from ultralytics import YOLO
import cv2
import os
import json

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load YOLO model (downloads automatically on first run)
model = YOLO("yolov8n.pt")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"})

    image = request.files["image"]

    filepath = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(filepath)

    results = model(filepath)

    img = cv2.imread(filepath)

    detections = []

    for result in results:

        boxes = result.boxes

        for box in boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            confidence = float(box.conf[0])

            class_id = int(box.cls[0])

            label = model.names[class_id]

            detections.append({
                "label": label,
                "confidence": round(confidence,2),
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            })

            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)

            cv2.putText(
                img,
                f"{label} {confidence:.2f}",
                (x1,y1-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0,255,0),
                2
            )

    output_path = os.path.join(OUTPUT_FOLDER,image.filename)

    cv2.imwrite(output_path,img)

    with open("annotation.json","w") as f:
        json.dump(detections,f,indent=4)

    return jsonify({
        "detections":detections,
        "output_image":image.filename
    })

@app.route("/outputs/<filename>")
def get_outputs(filename):
    return send_from_directory("outputs", filename)

if __name__ == "__main__":

    port = int(os.environ.get("PORT",5000))

    app.run(host="0.0.0.0",port=port,debug=True)