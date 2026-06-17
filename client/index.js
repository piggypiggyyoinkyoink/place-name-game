const width = 800;
const height = 1000;

const svg = d3.select("#map");
let projection;
window.addEventListener("DOMContentLoaded", async () => {
    let response = await fetch("/static/gb.json");
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

    function addPlace(place) {

        const [x, y] = projection([
            place.longitude,
            place.latitude
        ]);

        svg.append("circle")
            .attr("cx", x)
            .attr("cy", y)
            .attr("r", 4)
            .attr("fill", "rgba(255, 0, 0, 0.5)");
    }
    document.getElementById("placeInput").addEventListener("input", async (event) => {
        // console.log("hello");
        const placeName = event.target.value;
        if (placeName.length >= 2) {
            const response = await fetch(`http://127.0.0.1:8000/query?text=${encodeURIComponent(placeName)}`);
            const places = await response.json();
            // console.log(places.results);
            if (places.results.length > 0) {
                // console.log("beep");
                for (const place of places.results) {
                    addPlace({ latitude: place.lat, longitude: place.lon });
                }
                event.target.value = "";
            }
        }
    });
    // addPlace({ latitude: 51.5074, longitude: -0.1278 }); // Example: London
});



