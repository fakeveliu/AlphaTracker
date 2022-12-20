"use strict"

function topNavSetActive(nav_item) {
    const nav_items = [];
    var nav_title = document.getElementById("nav_title");
    var nav_companies = document.getElementById("nav_companies");
    var nav_investors = document.getElementById("nav_investors");
    var nav_market = document.getElementById("nav_market");
    var nav_instructions = document.getElementById("nav_instructions");
    var nav_username = document.getElementById("nav_username");
    var nav_notifications = document.getElementById("nav_notifications");
    nav_items.push(nav_title, nav_companies, nav_investors, nav_market, 
        nav_instructions, nav_username, nav_notifications);
    
    if (nav_item < 0) return;

    for (let i = 0; i < nav_items.length; i++) {
        nav_items[i].className = (i === nav_item) ? 'active' : '';
    }
}

function toggleNotifications() {
    var style = document.getElementById("notification_popup").style;
    if (style.display === "none") {
        style.display = "block";
        // topNavSetActive(6);
    } else {
        style.display = "none";
        // topNavSetActive(-1);
    }
}
