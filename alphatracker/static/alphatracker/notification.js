"use strict"

function loadnotification(id) {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function () {
        if (this.readyState != 4) return
        updateIcon(xhr)
    }
    xhr.open("GET", "/judge_notifications", true)
    xhr.send()
}

function updateIcon(xhr) {
    if (xhr.status == 200) {
        let response = JSON.parse(xhr.responseText)
        updateNotification(response.flag)
        return
    }
    if (xhr.status == 0) {
        displayError("Cannot connect to server")
        return
    }
    if (!xhr.getResponseHeader('content-type') == 'application/json') {
        displayError("Received status=" + xhr.status)
        return
    }
    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }
    displayError(response)
}

function displayError(message) {
    console.log(message)
    // let errorElement = document.getElementById("error")
    // errorElement.innerHTML = message
}

function updateNotification(response) {
    var no_unread = document.getElementById("no_unread")
    var have_unread = document.getElementById("have_unread")
    if (
        typeof no_unread != "undefined" | typeof have_unread != "undefined"
    ) {
        if (response == 0) {
            // no unread
            console.log("no unread should be 0")
            console.log(response)
            no_unread.style.display = ""
            have_unread.style.display = "none"
        }
        else {
            // have unread
            console.log("unread should be 1")
            console.log(response)
            no_unread.style.display = "none"
            have_unread.style.display = ""
        }
    }
}