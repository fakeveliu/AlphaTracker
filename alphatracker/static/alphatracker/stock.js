"use strict"

function loadStock(id) {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function () {
        if (this.readyState != 4) return
        updatePage(xhr)
    }

    xhr.open("GET", `get-chart/${id}`, true)
    xhr.send()
}

function updatePage(xhr) {
    if (xhr.status == 200) {
        let response = JSON.parse(xhr.responseText)
        updateStock(response)
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

function makePriceInfo(latest_open, latest_max, latest_min) {
    var current = Math.random() * (latest_max - latest_min) + latest_min;
    var change = current - latest_open;
    var rel_change = change / latest_open;
    var priceInfoElem = document.getElementById("price-info");
    var price_str = `Latest Price: ${current.toString().substr(0, 4)}`;
    const separator = `<span style="display:inline-block; width: 10px;"></span>`;
    var change_str = 
        `Change: ${change.toString().substr(0, 4)}(${(rel_change * 100).toString().substr(0, 5)}%)`;
    priceInfoElem.innerHTML = price_str + separator + change_str;
}

function updateStock(response) {
    var dataArr = [];
    const sticks = response['sticks'];
    for (let i = 0; i < sticks.length; i++) {
        let stick = sticks[i];
        let date = stick.date;
        let prices = [];
        prices.push(stick.open_price, stick.close_price, stick.min_price, stick.max_price);
        dataArr.push([date, prices]);
    }
    goChart(document.getElementById("chart"), dataArr);
}

// https://github.com/sutianbinde/charts

function goChart(cBox, dataArr) {
    console.log(dataArr)

    // canvas settings
    var canvas, ctx;
    var cWidth, cHeight, cMargin, cSpace;
    var originX, originY;
    // chart settings
    var bMargin, tobalBars, bWidth, maxValue, minValue;
    var totalYNomber;
    var gradient;
    var showArr;
    // dragging and animation
    var dragBarX, dragBarWidth;
    var ctr, numctr, speed;
    var infoBox;
    var mousePosition = {};

    // initialize canvas and chart
    canvas = document.createElement("canvas");
    if (canvas && canvas.getContext) {
        ctx = canvas.getContext("2d");
    }

    canvas.innerHTML = "Your browser does not support HTML5 canvas";
    cBox.appendChild(canvas);

    initChart();
    drawLineLabelMarkers();
    drawBarAnimate();
    drawDragBar();
    drawInfoBox();

    // listen to mouse move
    var mouseTimer = null;
    addMouseMove();
    function addMouseMove() {
        canvas.addEventListener("mousemove", function (e) {
            e = e || window.event;
            if (e.offsetX || e.offsetX == 0) {
                mousePosition.x = e.offsetX;
                mousePosition.y = e.offsetY;
            } else if (e.layerX || e.layerX == 0) {
                mousePosition.x = e.layerX;
                mousePosition.y = e.layerY;
            }

            clearTimeout(mouseTimer);
            mouseTimer = setTimeout(function () {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                drawLineLabelMarkers();
                drawBarAnimate(true);
                drawDragBar();
                drawInfoBox();
            }, 10);
        });
    }

    function initChart() {
        cMargin = 60;
        cSpace = 80;
        // resize canvas for HD display
        canvas.width = cBox.getAttribute("width") * 2;
        canvas.height = cBox.getAttribute("height") * 2;
        canvas.style.height = canvas.height / 2 + "px";
        canvas.style.width = canvas.width / 2 + "px";
        cHeight = canvas.height - cMargin * 2 - cSpace * 2;
        cWidth = canvas.width - cMargin * 2 - cSpace * 2;
        originX = cMargin + cSpace;
        originY = cMargin + cHeight;

        showArr = dataArr.slice(0, parseInt(dataArr.length / 2));

        // chart info
        tobalBars = showArr.length;
        bWidth = parseInt(cWidth / tobalBars / 3);
        bMargin = parseInt((cWidth - bWidth * tobalBars) / (tobalBars + 1));
        maxValue = 0;
        minValue = 9999999;
        for (var i = 0; i < dataArr.length; i++) {
            var barVal = dataArr[i][1][3];
            if (barVal > maxValue) {
                maxValue = barVal;
            }
            var barVal2 = dataArr[i][1][2];
            if (barVal2 < minValue) {
                minValue = barVal2;
            }

        }
        maxValue += 0.01 * maxValue;
        minValue -= 0.01 * minValue;
        totalYNomber = 10;

        // animation info
        ctr = 1;
        numctr = 50;
        speed = 2;
        infoBox = {
            "display": false, "x": null, "y": null,
            "open": null, "close": null, "high": null, "low": null
        };

        dragBarWidth = 30;
        dragBarX = cWidth / 2 + cSpace + cMargin - dragBarWidth / 2;

    }

    function drawLineLabelMarkers() {
        ctx.font = "24px Arial";
        ctx.lineWidth = 2;
        ctx.fillStyle = "#000";
        ctx.strokeStyle = "#000";

        drawLine(originX, originY, originX, cMargin); // y axis
        drawLine(originX, originY, originX + cWidth, originY); // x axis
        drawMarkers();
    }

    function drawLine(x, y, X, Y) {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(X, Y);
        ctx.stroke();
        ctx.closePath();
    }

    function drawMarkers() {
        ctx.strokeStyle = "#E0E0E0";
        // y axis
        var oneVal = (maxValue - minValue) / totalYNomber;
        ctx.textAlign = "right";
        for (var i = 0; i <= totalYNomber; i++) {
            var markerVal = parseInt(i * oneVal + minValue);;
            var xMarker = originX - 10;
            var yMarker = parseInt(originY - cHeight * (markerVal - minValue) / (maxValue - minValue));

            ctx.fillText(markerVal, xMarker, yMarker + 3, cSpace); // prices
            if (i > 0) {
                drawLine(originX + 2, yMarker, originX + cWidth, yMarker);
            }
        }
        // x axis
        var textNb = 6;
        ctx.textAlign = "center";
        for (var i = 0; i < tobalBars; i++) {
            if (tobalBars > textNb && i % parseInt(tobalBars / 6) != 0) {
                continue;
            }
            var markerVal = dataArr[i][0];
            var xMarker = parseInt(originX + cWidth * (i / tobalBars) + bMargin + bWidth / 2);
            var yMarker = originY + 30;
            ctx.fillText(markerVal, xMarker, yMarker, cSpace); // dates
        }
        // y label
        ctx.save();
        ctx.rotate(-Math.PI / 2);
        ctx.fillText("Price", -canvas.height / 2, cSpace - 20);
        ctx.restore();
        // x label
        ctx.fillText("Date", originX + cWidth / 2, originY + cSpace - 20);
    };

    function drawBarAnimate(mouseMove) {
        infoBox["display"] = false;
        var parsent = ctr / numctr;
        for (var i = 0; i < tobalBars; i++) {
            var oneVal = parseInt(maxValue / totalYNomber);
            const data = dataArr[i][1];
            var color = "#30C7C9";
            var barVal = data[0];
            var disY = 0;
            // [Open, Close, Low, High], + 30C7C9, - D7797F
            if (data[1] > data[0]) {
                color = "#D7797F";
                barVal = data[1];
                disY = data[1] - data[0];
            } else {
                disY = data[0] - data[1];
            }
            var showH = disY / (maxValue - minValue) * cHeight * parsent;
            showH = showH > 2 ? showH : 2;

            var barH = parseInt(cHeight * (barVal - minValue) / (maxValue - minValue));
            var y = originY - barH;
            var x = originX + ((bWidth + bMargin) * i + bMargin) * parsent;

            drawRect(x, y, bWidth, showH, mouseMove, color, true, false, data);  // Open and Close

            // High and Low
            showH = (data[3] - data[2]) / (maxValue - minValue) * cHeight * parsent;
            showH = showH > 2 ? showH : 2;

            y = originY - parseInt(cHeight * (data[3] - minValue) / (maxValue - minValue));
            drawRect(parseInt(x + bWidth / 2 - 1), y, 2, showH, mouseMove, color);
        }
        if (ctr < numctr) {
            ctr++;
            setTimeout(function () {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                drawLineLabelMarkers();
                drawBarAnimate();
                drawDragBar();
                drawInfoBox();
            }, speed *= 0.03);
        }
    }

    function drawRect(x, y, X, Y, mouseMove, color, ifBigBar, ifDrag, prices) {

        ctx.beginPath();

        if (parseInt(x) % 2 !== 0) {
            x += 1;
        }
        if (parseInt(y) % 2 !== 0) {
            y += 1;
        } if (parseInt(X) % 2 !== 0) {
            X += 1;
        }
        if (parseInt(Y) % 2 !== 0) {
            Y += 1;
        }
        ctx.rect(parseInt(x), parseInt(y), parseInt(X), parseInt(Y));

        // if hovering on candle stick
        if (ifBigBar && mouseMove && ctx.isPointInPath(mousePosition.x * 2, mousePosition.y * 2)) {
            ctx.strokeStyle = color;
            ctx.strokeWidth = 20;
            ctx.stroke();
            // display prices
            infoBox["display"] = true;
            infoBox["x"] = mousePosition.x * 2;
            infoBox["y"] = mousePosition.y * 2;
            infoBox["open"] = prices[0].toString().substr(0, 4);
            infoBox["close"] = prices[1].toString().substr(0, 4);
            infoBox["low"] = prices[2].toString().substr(0, 4);
            infoBox["high"] = prices[3].toString().substr(0, 4);
        }

        // if hovering on dragbar
        canvas.style.cursor = "default";
        if (ifDrag && ctx.isPointInPath(mousePosition.x * 2, mousePosition.y * 2)) {
            canvas.style.cursor = "all-scroll";
        }
        ctx.fillStyle = color;
        ctx.fill();
        ctx.closePath();

    }

    // drawDragBar();
    function drawDragBar() {
        drawRect(originX, originY + cSpace, cWidth, cMargin, false, "#E8E4F0");
        drawRect(originX, originY + cSpace, dragBarX - originX, cMargin, false, "#BCCEF5");
        drawRect(dragBarX, originY + cSpace, dragBarWidth, cMargin, false, "#078ACB", false, true);
    }

    function drawInfoBox() {
        if (!infoBox["display"]) return;
        // mouse inside a candle stick
        console.log("got here");
        var boxX = infoBox["x"], boxY = infoBox["y"];
        var topMargin = 45;
        var leftMargin = 15;
        var textStartX = infoBox["x"] + leftMargin;
        var textStartY = infoBox["y"] + topMargin;
        var spacing = 40;
        // box
        ctx.beginPath();
        ctx.fillStyle = 'rgba(225,225,225,0.7)';
        ctx.fillRect(boxX, boxY, 180, 200);
        // text
        ctx.fillStyle = "#000000";
        ctx.textAlign = "left";
        ctx.font = "28px Helvetica"
        ctx.fillText(`Open: ${infoBox["open"]}`, textStartX, textStartY);
        ctx.fillText(`High: ${infoBox["high"]}`, textStartX, textStartY + 1 * spacing);
        ctx.fillText(`Low: ${infoBox["low"]}`, textStartX, textStartY + 2 * spacing);
        ctx.fillText(`Close: ${infoBox["close"]}`, textStartX, textStartY + 3 * spacing);
        ctx.closePath();
    }

    // listen to mouse drag
    canvas.onmousedown = function (e) {

        if (canvas.style.cursor != "all-scroll") {
            return false;
        }

        document.onmousemove = function (e) {
            e = e || window.event;
            if (e.offsetX || e.offsetX == 0) {
                dragBarX = e.offsetX * 2 - dragBarWidth / 2;
            } else if (e.layerX || e.layerX == 0) {
                dragBarX = e.layerX * 2 - dragBarWidth / 2;
            }

            if (dragBarX <= originX) {
                dragBarX = originX
            }
            if (dragBarX > originX + cWidth - dragBarWidth) {
                dragBarX = originX + cWidth - dragBarWidth
            }

            var nb = Math.ceil(dataArr.length * ((dragBarX - cMargin - cSpace) / cWidth));
            showArr = dataArr.slice(0, nb || 1);

            tobalBars = showArr.length;
            bWidth = parseInt(cWidth / tobalBars / 3);
            bMargin = parseInt((cWidth - bWidth * tobalBars) / (tobalBars + 1));

        }

        document.onmouseup = function () {
            document.onmousemove = null;
            document.onmouseup = null;
        }
    }


}