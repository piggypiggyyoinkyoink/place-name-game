const width = 800;
const height = 1000;

const svg = d3.select("#map");
let projection;
fetch("/static/gb.json")
    .then(response => response.json())
    .then(geoData => {
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

    });

function addPlace(place) {

    const [x, y] = projection([
        place.longitude,
        place.latitude
    ]);

    svg.append("circle")
        .attr("cx", x)
        .attr("cy", y)
        .attr("r", 40)
        .attr("fill", "red");
}

addPlace({ latitude: 51.5074, longitude: -0.1278 }); // Example: London