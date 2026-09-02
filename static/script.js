const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const resultImage = document.getElementById("resultImage");
const result = document.getElementById("result");

imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if(file){

        preview.src = URL.createObjectURL(file);

        resultImage.src = "";

        result.innerHTML = "";

    }

});

function detectObjects(){

    const file = imageInput.files[0];

    if(!file){

        alert("Please select an image.");

        return;

    }

    const formData = new FormData();

    formData.append("image", file);

    result.innerHTML = "<div class='loading'>🤖 Detecting Objects...</div>";

    fetch("/detect",{

        method:"POST",

        body:formData

    })

    .then(response=>response.json())

    .then(data=>{

        result.innerHTML="";

        resultImage.src="/outputs/"+data.output_image+"?"+new Date().getTime();

        result.innerHTML+=`
        <h3>Total Objects Detected : ${data.detections.length}</h3>
        <br>
        `;

        data.detections.forEach(obj=>{

            result.innerHTML+=`

            <div class="detect-item">

            <b>${obj.label.toUpperCase()}</b>

            <br>

            Confidence : ${(obj.confidence*100).toFixed(1)} %

            <br>

            Bounding Box :

            (${obj.x1}, ${obj.y1}) →

            (${obj.x2}, ${obj.y2})

            </div>

            `;

        });

    })

    .catch(err=>{

        console.log(err);

        alert("Detection Failed");

    });

}
