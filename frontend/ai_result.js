const predictionForm = document.getElementById("predictionForm");

const cropName = document.getElementById("cropName");

const cropDescription = document.getElementById("cropDescription");

predictionForm.addEventListener("submit", function(e){

    e.preventDefault();

    const soilType = document.getElementById("soilType").value;

    const temperature = Number(document.getElementById("temperature").value);

    const humidity = Number(document.getElementById("humidity").value);

    const rainfall = Number(document.getElementById("rainfall").value);

    if(
        soilType==="" ||
        temperature==="" ||
        humidity==="" ||
        rainfall===""){
            alert("Please fill all fields.");
            return;
    }

    cropName.innerHTML="Predicting...";

    cropDescription.innerHTML="Analyzing environmental conditions...";

    setTimeout(function(){

        let crop="";
        let description="";

        if(soilType==="Black Soil"){

            crop="Cotton";

            description="Black soil is ideal for Cotton because it retains moisture and nutrients.";

        }

        else if(soilType==="Red Soil"){

            crop="Groundnut";

            description="Red soil supports Groundnut cultivation under moderate rainfall.";

        }

        else if(soilType==="Clay Soil"){

            crop="Rice";

            description="Clay soil retains water making it suitable for Paddy cultivation.";

        }

        else if(soilType==="Sandy Soil"){

            crop="Watermelon";

            description="Sandy soil provides excellent drainage for Watermelon.";

        }

        else{

            crop="Sugarcane";

            description="Loamy soil is highly fertile and supports Sugarcane production.";

        }

        if(temperature>35){

            description+=" High temperature detected. Ensure regular irrigation.";

        }

        if(rainfall<60){

            description+=" Rainfall is low. Consider drip irrigation.";

        }

        if(humidity>80){

            description+=" High humidity may increase fungal diseases.";

        }

        cropName.innerHTML=crop;

        cropDescription.innerHTML=description;

    },1500);

});