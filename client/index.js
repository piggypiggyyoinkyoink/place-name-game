const width = 600;
const height = 750;

const svg = d3.select("#map");
let projection;
let enteredPlaces = [];
let numPlaces = 0;
let totalPlaces;
let type;
window.addEventListener("DOMContentLoaded", async () => {
    async function drawMap(){
        let response;
        switch(type){
            case "uk":
                response = await fetch("/static/geo/uk-counties.geojson");
                break;
            default:
                console.log("Unknown type, defaulting to UK");
                response = await fetch("/static/geo/uk-counties.geojson");
        }
        let geoData = await response.json();
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
            const response = await fetch(`/query?text=${encodeURIComponent(placeName)}&type=${type}`, { credentials: 'include' });
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
        const response = await fetch(`/init?type=${type}`, { credentials: 'include' });
        const data = await response.json();
        for (const place of data.guesses) {
            addPlace(place);
            enteredPlaces.push(place.name.toLowerCase().trim().replaceAll(" ",""));
        }
        const total = await fetch("/howmany");
        const totalData = await total.json();
        totalPlaces = totalData.total;
        document.getElementById("placesHeader").textContent = `Places Entered: ${numPlaces} / ${totalPlaces}`;
        console.log(data);
    }
    init();

    



    // async function addAllPlaces(a,b){
    //     const response = await fetch(`http://127.0.0.1:8000/all`);
    //     let places = await response.json();
    //     for (const place of places.results.slice(a,b)) {
    //         addPlace(place);
    //     }
    // }
    // addAllPlaces(0, 36000);


});



