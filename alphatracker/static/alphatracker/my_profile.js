"use strict"

function setActive(item) {
  const profile_items = [];
  var my_collection = document.getElementById("my_collection");
  var my_following = document.getElementById("my_following");
  var my_followers = document.getElementById("my_followers");
  var my_transactions = document.getElementById("my_transactions")
  profile_items.push(my_collection, my_following, my_followers, my_transactions);

  
  for (let i = 0; i < profile_items.length; i++) {
    if (i === item) {
        profile_items[i].className = 'profile-item-active';
    } else {
        profile_items[i].className = 'profile-item';
    }
  }
}