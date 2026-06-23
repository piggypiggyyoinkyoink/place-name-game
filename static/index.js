const width = 600;
const height = 750;

const svg = d3.select("#map");
let projection;
let enteredPlaces = [];
let numPlaces = 0;
let totalPlaces;
let type;
let regionName;
window.addEventListener("DOMContentLoaded", async () => {
    async function fetchGeoJSON(type) {
        const res = await fetch("./typemap");
        const typemap = await res.json();
        console.log(typemap);
        if (!typemap[type]) {
            throw new Error(`Invalid type: ${type}`);
            window.location.href = "./"; 
            return;
        }
        const filename = typemap[type].geofile;
        regionName = typemap[type].name;
        document.getElementById("h1").textContent = "How many places can you name in " + regionName + "?";
        const response = await fetch(`./static/geo/${filename}`);
        const geoData = await response.json();
        return geoData;
    }
        
    async function drawMap(){
        let geoData = await fetchGeoJSON(type);
        // Create projection
        projection = d3.geoConicConformal()
            .fitSize([width, height], geoData);

        // Create path generator
        const path = d3.geoPath()
            .projection(projection);

        // Draw all features
        svg.selectAll("path")
            .data(geoData.features)
            .enter()
            .append("path")
            .attr("d", path)
            .attr("fill", "#eeeeee")
            .attr("stroke", "#444")
            .attr("stroke-width", 0.5);

        }
    function addToMap(place) {

        const [x, y] = projection([
            place.longitude,
            place.latitude
        ]);

        svg.append("circle")
            .attr("cx", x)
            .attr("cy", y)
            .attr("r", 3)
            .attr("fill", "rgba(255, 0, 0, 0.5)");
    }
    

    function addToTable(name, county){
        const table = document.getElementById("placesTable");
        const row = table.insertRow(0);
        const cell0 = row.insertCell(0);
        cell0.textContent = numPlaces;
        const cell1 = row.insertCell(1);
        cell1.textContent = name + ", " + county;
        const tableContainer = document.getElementById("tableContainer");
        if (tableContainer.style.overflowY != "scroll" && tableContainer.offsetHeight >= parseInt(window.getComputedStyle(tableContainer).maxHeight)) {
            tableContainer.style.overflowY = "scroll";
        }
    }
    function addPlace(place){
        addToMap({ latitude: place.lat, longitude: place.lon });
        numPlaces++;
        addToTable(place.name, place.county);
    }
    document.getElementById("placeInput").addEventListener("keypress", async (event) => {
        if (event.key !== "Enter") return;
        // console.log("hello");
        const placeName = event.target.value;
        if (enteredPlaces.includes(placeName.toLowerCase().trim().replaceAll(" ",""))) {
            document.getElementById("message").textContent = "Place already entered!";
            return;
        }
        document.getElementById("message").textContent = "⠀";
        if (placeName.length >= 2) {
            const response = await fetch(`./query?text=${encodeURIComponent(placeName)}&type=${type}`, { credentials: 'include' });
            if (!response.ok) {
                console.error("Failed to query place");
                return;
            }
            const places = await response.json();
            console.log(places);
            if (places.results.length > 0) {
                // console.log("beep");
                for (const place of places.results) {
                    addPlace(place);
                    document.getElementById("placesHeader").textContent = `Places Entered: ${numPlaces} / ${totalPlaces}`;
                }
                enteredPlaces.push(event.target.value.toLowerCase().trim().replaceAll(" ",""));
                event.target.value = "";
            } else if (places.already_guessed) {
                document.getElementById("message").textContent = "Place already entered!";
            }
        }
    
    });
    async function init(){
        const paramsString = window.location.search;
        const searchParams = new URLSearchParams(paramsString)
        type = searchParams.get("type")|| "uk";
        await drawMap();
        const response = await fetch(`./init?type=${type}`, { credentials: 'include' });
        if (!response.ok) {
            console.error("Failed to initialize session");
            return;
        }
        const data = await response.json();
        for (const place of data.guesses) {
            addPlace(place);
            enteredPlaces.push(place.name.toLowerCase().trim().replaceAll(" ",""));
        }
        document.getElementById("nameInput").value = data.name || "";
        const total = await fetch(`./howmany?type=${type}`);
        const totalData = await total.json();
        totalPlaces = totalData.total;
        document.getElementById("placesHeader").textContent = `Places Entered: ${numPlaces} / ${totalPlaces}`;
        console.log(data);
    }
    init();

    document.getElementById("nameInput").addEventListener("blur", async (event) => {
        const name = event.target.value.trim();
        if (name) {
            const response = await fetch(`./setname?type=${type}&name=${encodeURIComponent(name)}`, { credentials: 'include' });
            if (!response.ok) {
                console.error("Failed to set name");
                return;
            }
            const data = await response.json();
            console.log(data);
        }
    });

    document.getElementById("finishButton").addEventListener("click", async () => {
        const name = document.getElementById("nameInput").value.trim();
        const response = await fetch(`./finish?type=${type}&name=${encodeURIComponent(name)}`, { credentials: 'include' });
        if (!response.ok) {
            console.error("Failed to finish game");
            window.location.reload();
            return;
        }
        const data = await response.json();
        console.log(data);
        window.location.href = `./results?uid=${data.uid}`;
    });
    
    document.getElementById("resetButton").addEventListener("click", async () => {
        const response = await fetch(`./reset?type=${type}`, { credentials: 'include' });
        if (!response.ok) {
            console.error("Failed to reset game");
            return;
        }
        const data = await response.json();
        console.log(data);
        window.location.href = `./game?type=${type}`;
    });

});



