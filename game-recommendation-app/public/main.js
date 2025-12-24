const pressMe = document.getElementById("press-me");

async function pressMeClicked(event) {
    const response = await fetch("/get-data");
    const data = await response.json();
    console.log(data);
}

pressMe.addEventListener("click", pressMeClicked);