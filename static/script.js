document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const submitBtn = document.getElementById('submit-btn');
    const resultImage = document.getElementById('result-image');
    const detectionData = document.getElementById('detection-data');

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            const prompt = dropZone.querySelector('.drop-zone-prompt');
            if (prompt) prompt.textContent = fileInput.files[0].name;
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!fileInput.files[0]) {
            alert('Please select an image first.');
            return;
        }

        const formData = new FormData();
        formData.append('image', fileInput.files[0]);

        submitBtn.disabled = true;
        submitBtn.textContent = 'Detecting...';
        detectionData.textContent = 'Processing with YOLOv8...';

        try {
            const response = await fetch('/detect', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server returned error ${response.status}`);
            }

            const data = await response.json();

            if (data.image_url || data.result_image) {
                resultImage.src = data.image_url || data.result_image;
                resultImage.style.display = 'block';
            }

            if (data.detections || data.boxes) {
                detectionData.textContent = JSON.stringify(data.detections || data.boxes, null, 2);
            } else {
                detectionData.textContent = 'Detection complete!';
            }
        } catch (err) {
            console.error(err);
            detectionData.textContent = 'Detection failed: ' + err.message;
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Detect & Annotate';
        }
    });
});
