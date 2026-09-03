from flask import Flask, render_template, request, jsonify, url_for
from ultralytics import YOLO
import cv2
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Load YOLO model
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

    try:
        # Check image
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]

        if file.filename == "":
            return jsonify({"error": "No image selected"}), 400

        # Secure filename
        filename = secure_filename(file.filename)

        if not filename:
            return jsonify({"error": "Invalid filename"}), 400

        # Save uploaded image
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        # Run YOLO
        results = model(input_path)

        # Create unique result filename
        result_filename = "result_" + filename
        result_path = os.path.join(
            RESULT_FOLDER,
            result_filename
        )

        # Draw detections
        annotated = results[0].plot()

        # Save result
        success = cv2.imwrite(result_path, annotated)

        if not success:
            return jsonify({
                "error": "Could not save detection result"
            }), 500

        # Get detected objects
        detections = []

        result = results[0]

        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            class_name = model.names[class_id]

            detections.append({
                "class": class_name,
                "confidence": confidence
            })

        image_url = url_for(
            "static",
            filename=f"results/{result_filename}"
        )

        return jsonify({
            "success": True,
            "image_url": image_url,
            "detections": detections
        })

    except Exception as e:

        print("DETECTION ERROR:", repr(e))

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
