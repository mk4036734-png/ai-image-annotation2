from flask import Flask, render_template, request
from ultralytics import YOLO
import cv2
import os

app = Flask(__name__)

model = YOLO("yolov8n.pt")

UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect():

    if "image" not in request.files:
        return "No image uploaded"

    file = request.files["image"]

    if file.filename == "":
        return "No image selected"

    # Save uploaded image
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    # Run YOLO
    results = model(input_path)

    # Save detection image
    result_path = os.path.join(RESULT_FOLDER, "result.jpg")

    annotated = results[0].plot()
    cv2.imwrite(result_path, annotated)

    return render_template(
        "index.html",
        original_image="/" + input_path,
        result_image="/" + result_path
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
