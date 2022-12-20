"use strict"

const HEADER_TO_COL = {
    "name"      : 0,
    "est"       : 1,
    "size"      : 2,
    "creator"   : 3,
    "modified"  : 4,
    "collected" : 5,

    "transaction_time": 6,
    "shares_held": 7,
}

function modify_date(date) {
    var newday = new Date(date)
    return newday
}

function modify_time(date) {
    console.log(date)
    var array = date.split(' ')
    var date = array[0].split('/')
    var time = array[1].split(':')
    var newday = new Date(date[2], date[0], date[1], time[0], time[1])
    console.log(newday)
    return newday
}

function sortTable(h) {
    const n = HEADER_TO_COL[h]
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0
    table = document.getElementById("table")
    switching = true
    // Set the sorting direction to ascending:
    dir = "asc"
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
        // Start by saying: no switching is done:
        switching = false
        rows = table.rows
        /* Loop through all table rows (except the
        first, which contains table headers): */
        for (i = 1; i < (rows.length - 1); i++) {
            // Start by saying there should be no switching:
            shouldSwitch = false
            /* Get the two elements you want to compare,
            one from current row and one from the next: */
            x = rows[i].getElementsByTagName("TD")[n]
            y = rows[i + 1].getElementsByTagName("TD")[n]
            /* Check if the two rows should switch place,
            based on the direction, asc or desc: */
            if (dir == "asc") {
                if (h == "name" || h == "creator" || h == "account") {
                    if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                        // If so, mark as a switch and break the loop:
                        shouldSwitch = true
                        break
                    }
                }
                else if (h == "est") {
                    if (modify_date(x.innerHTML) > modify_date(y.innerHTML)) {
                        shouldSwitch = true
                        break
                    }
                }
                else if (h == "size" || h == "collected") {
                    if (Number(x.innerHTML) > Number(y.innerHTML)) {
                        console.log(x.innerHTML)
                        //if so, mark as a switch and break the loop:
                        shouldSwitch = true
                        break
                    }
                }
                else if (h == "modified" || x == "transaction_time" ) {
                    // TODO: not working yet 
                    if (modify_time(x.innerHTML) > modify_time(y.innerHTML)) {
                        shouldSwitch = true
                        break
                    }
                }
            } else if (dir == "desc") {
                if (n == 0 || n == 2 || n == 4) {
                    if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                        // If so, mark as a switch and break the loop:
                        shouldSwitch = true
                        break
                    }
                }
                else if (h == "est") {
                    if (modify_date(x.innerHTML) < modify_date(y.innerHTML)) {
                        shouldSwitch = true
                        break
                    }
                }
                else if (h == "size" || h == "collected") {
                    if (Number(x.innerHTML) < Number(y.innerHTML)) {
                        //if so, mark as a switch and break the loop:
                        shouldSwitch = true
                        break
                    }
                }
                else if (h == "modified" || x == "transaction_time") {
                    // TODO: not working yet
                    if (modify_time(x.innerHTML) < modify_time(y.innerHTML)) {
                        shouldSwitch = true
                        break
                    }
                }
            }
        }
        if (shouldSwitch) {
            /* If a switch has been marked, make the switch
            and mark that a switch has been done: */
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i])
            switching = true
            // Each time a switch is done, increase this count by 1:
            switchcount++
        } else {
            /* If no switching has been done AND the direction is "asc",
            set the direction to "desc" and run the while loop again. */
            if (switchcount == 0 && dir == "asc") {
                dir = "desc"
                switching = true
            }
        }
    }
}

function searchTable() {
    var td, i, txtValue
    let input = document.getElementById("search-input")
    let filter = input.value.toUpperCase()
    let table = document.getElementById("table")
    let tr = table.getElementsByTagName("tr")

    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[0]
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = ""
            } else {
                tr[i].style.display = "none"
            }
        }
    }
}