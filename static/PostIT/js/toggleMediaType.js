window.addEventListener("pageshow", hideVidForm);

function hideVidForm() {
    document.getElementById("vid-form").style.display = 'none';
}


document.getElementById('toggle-media-type').addEventListener('click', function () {
    let elem = document.getElementById('toggle-media-type');
    form1 = document.getElementById("img-form")
    form2 = document.getElementById("vid-form")
    if (elem.innerHTML == "Add video") {
        elem.innerHTML = "Add images";

        form1.style.display = 'none';
        form2.style.display = 'block';
    }
    else {
        elem.innerHTML = "Add video";
        form1.style.display = 'block';
        form2.style.display = 'none';
    }

})