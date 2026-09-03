document.addEventListener("DOMContentLoaded", () => {
    const imageInput = document.getElementById("imageInput");
    const detectBtn = document.getElementById("detectBtn");
    const originalImg = document.getElementById("originalImg");
    const detectedImg = document.getElementById("detectedImg");
    const statusMsg = document.getElementById("status-msg");
    const detectionsList = document.getElementById("detectionsList");

    imageInput.addEventListener("change", () => {
        if (imageInput.files && imageInput.files[0]) {
            const reader = new FileReader();
            reader.onload = (e) => {
                originalImg.src = e.target.result;
                originalImg.style.display = "block";
            };
            reader.readAsDataURL(imageInput.files[0]);
            detectedImg.style.display = "none";
            detectionsList.innerHTML = "";
            statusMsg.textContent = "";
        }
    });

    detectBtn.addEventListener("click", async () => {
        if (!imageInput.files || !imageInput.files[0]) {
            alert("Please choose an image file first!");
            return;
        }

        const formData = new FormData();
        formData.append("image", imageInput.files[0]);

        detectBtn.disabled = true;
        statusMsg.textContent = "Processing image with YOLOv8...";
        statusMsg.style.color = "#1565c0";

        try {
            const response = await fetch("/detect", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok || data.error) {
                throw new Error(data.error || `Server error: ${response.status}`);
            }

            detectedImg.src = data.image_url + "?t=" + new Date().getTime();
            detectedImg.style.display = "block";

            if (data.detections && data.detections.length > 0) {
                let html = "<strong>Objects Detected:</strong><ul>";
                data.detections.forEach(item => {
                    html += `<li>${item.class} (${Math.round(item.confidence * 100)}%)</li>`;
                });
                html += "</ul>";
                detectionsList.innerHTML = html;
            } else {
                detectionsList.innerHTML = "<em>No objects detected above threshold.</em>";
            }

            statusMsg.textContent = "Detection Complete! ✅";
            statusMsg.style.color = "#2e7d32";

        } catch (err) {
            console.error(err);
            statusMsg.textContent = "Detection failed: " + err.message;
            statusMsg.style.color = "#c62828";
        } finally {
            detectBtn.disabled = false;
        }
    });
});
