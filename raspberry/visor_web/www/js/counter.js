var downloadButton = document.getElementById("actualizar");
var counter = 30;
var newElement = document.createElement("p");
newElement.innerHTML = "You can download the file in 10 seconds.";
var id;

downloadButton.parentNode.replaceChild(newElement, downloadButton);

id = setInterval(function() {
    counter--;
    if(counter < 0) {
        newElement.parentNode.replaceChild(downloadButton, newElement);
        clearInterval(id);
    } else {
        newElement.innerHTML = "You can download the file in " + counter.toString() + " seconds.";
    }
}, 1000);

