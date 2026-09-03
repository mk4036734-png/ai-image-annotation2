import os
import cv2
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from ultralytics import YOLO

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join("static", "uploads")
OUTPUT_FOLDER = os.path.join("static", "output")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

model = YOLO("yolov8n.pt")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/detect", methods=["POST"])
def detect():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    try:
        results = model(input_path)
        annotated_frame = results[0].plot()

        output_filename = f"annotated_{filename}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        cv2.imwrite(output_path, annotated_frame)

        detections = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            detections.append({
                "class": model.names[cls_id],
                "confidence": round(conf, 2)
            })

        return jsonify({
            "image_url": f"/{output_path}",
            "detections": detections
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
