const temperature = document.getElementById("temperature");
const pressure = document.getElementById("pressure");
const flow = document.getElementById("flow");
const level = document.getElementById("level");
const updatedTime = document.getElementById("updatedTime");

// Chart history
const labels = [];
const temperatureData = [];
const pressureData = [];
const flowData = [];
const levelData = [];

const ctx = document.getElementById("sensorChart").getContext("2d");

const sensorChart = new Chart(ctx, {
    type: "line",
    data: {
        labels: labels,
        datasets: [
            {
                label: "Temperature (°C)",
                data: temperatureData,
                tension: 0.4
            },
            {
                label: "Pressure (bar)",
                data: pressureData,
                tension: 0.4
            },
            {
                label: "Flow Rate (m³/h)",
                data: flowData,
                tension: 0.4
            },
            {
                label: "Level (%)",
                data: levelData,
                tension: 0.4
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false
    }
});


async function getSensorData() {

    try {

        const response = await fetch("http://127.0.0.1:5000/metrics");

        const data = await response.json();

        // Update sensor cards
        temperature.textContent = data.temperature + " °C";
        pressure.textContent = data.pressure + " bar";
        flow.textContent = data.flow + " m³/h";
        level.textContent = data.level + "%";

        updatedTime.textContent = "Updated: " + data.timestamp;


        // Add data to chart
        labels.push(data.timestamp);
        temperatureData.push(data.temperature);
        pressureData.push(data.pressure);
        flowData.push(data.flow);
        levelData.push(data.level);


        // Keep only latest 30 readings
        if (labels.length > 30) {
            labels.shift();
            temperatureData.shift();
            pressureData.shift();
            flowData.shift();
            levelData.shift();
        }

        sensorChart.update();

    } catch (error) {

        console.error("Backend connection error:", error);

        updatedTime.textContent = "Backend Offline";

    }
}


// Get new sensor data every 2 seconds
setInterval(getSensorData, 2000);

// Get data immediately
getSensorData();