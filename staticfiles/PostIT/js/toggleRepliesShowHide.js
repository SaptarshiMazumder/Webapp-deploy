function toggleReplies(e) {


    if (e.includes("Show")) {
        return e.replace("Show", "Hide")
    }
    else {
        return e.replace("Hide", "Show")
    }
}