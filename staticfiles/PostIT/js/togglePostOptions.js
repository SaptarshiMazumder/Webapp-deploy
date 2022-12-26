$(document).on('click', '#three-dots', function (e) {
    var this_ = $(this);
    postid = this_.attr("value").valueOf();
    console.log("POST OPTIONS POST ID: " + postid)
    var containers = document.querySelectorAll("#post-options-list")
    containers.forEach(container => {
        if (postid === container.getAttribute('value')) {
            container.classList.add("show")
            console.log("post-options-list " + container.getAttribute('value'))

        }

    })

})

$(document).on('click', '#post-options-list-close', function (e) {
    var this_ = $(this);
    postid = this_.attr("value").valueOf();
    console.log("POST OPTIONS CLOSE BUTTON POST ID: " + postid)
    var containers = document.querySelectorAll("#post-options-list")
    containers.forEach(container => {
        if (postid === container.getAttribute('value')) {
            container.classList.remove("show")
            console.log("post-options-list " + container.getAttribute('value'))

        }

    })
});

$(document).on('click', '#blocker', function (e) {
    var this_ = $(this);
    postid = this_.attr("value").valueOf();
    console.log("BLOCKER POST ID: " + postid)
    var containers = document.querySelectorAll("#post-options-list")
    containers.forEach(container => {
        if (postid === container.getAttribute('value')) {
            container.classList.remove("show")
            console.log("post-options-list " + container.getAttribute('value'))

        }

    })
});

