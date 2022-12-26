var navbarToggleBtn = document.getElementById("navbar-toggle")
navbarToggleBtn.addEventListener('click', () => {
    var navbarLeft = document.getElementById("sidebar-left")
    // if (navbarLeft.classList.contains("show")) {
    //     navbarLeft.classList.remove("show")
    // }
    // else {
    //     navbarLeft.classList.add("show")
    // }

    if (navbarLeft.style.display === "block") {
        navbarLeft.style.display = "none"
    }
    else {
        navbarLeft.style.display = "block"
    }

})

var navbarProfileSettingsToggleBtn = document.getElementById("sidebar-profile-settings-button")
navbarProfileSettingsToggleBtn.addEventListener('click', () => {
    alert("hj")


})

