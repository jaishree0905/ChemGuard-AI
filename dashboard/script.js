// =====================================================
// CHEM-GUARD AI - DASHBOARD SCRIPT
// =====================================================

// -----------------------------
// GET HTML ELEMENTS
// -----------------------------

const temperature = document.getElementById("temperature");
const pressure = document.getElementById("pressure");
const flow = document.getElementById("flow");
const level = document.getElementById("level");
const updatedTime = document.getElementById("updatedTime");

const diagnosisStatus = document.getElementById("diagnosisStatus");
const anomalyStatus = document.getElementById("anomalyStatus");
const diagnosisConfidence = document.getElementById("diagnosisConfidence");
const riskStatus = document.getElementById("riskStatus");
const recommendedAction = document.getElementById("recommendedAction");

const rootCauseList = document.getElementById("rootCauseList");

// =====================================================
// GRAPH DATA
// =====================================================

const labels = [];

const temperatureData = [];
const pressureData = [];
const flowData = [];
const levelData = [];

// =====================================================
// CREATE SENSOR GRAPH
// =====================================================

const canvas = document.getElementById("sensorChart");

let sensorChart = null;

if (canvas && typeof Chart !== "undefined") {

    const ctx = canvas.getContext("2d");

    sensorChart = new Chart(ctx, {

        type: "line",

        data: {
            labels: labels,

            datasets: [

                {
                    label: "Temperature",
                    data: temperatureData,
                    yAxisID: "yTemperature",
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 2
                },

                {
                    label: "Pressure",
                    data: pressureData,
                    yAxisID: "yPressure",
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 2
                },

                {
                    label: "Flow",
                    data: flowData,
                    yAxisID: "yFlow",
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 2
                },

                {
                    label: "Level",
                    data: levelData,
                    yAxisID: "yLevel",
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 2
                }

            ]
        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            animation: false,

            interaction: {
                mode: "index",
                intersect: false
            },

            plugins: {

                legend: {
                    display: true
                }

            },

            scales: {

                x: {
                    ticks: {
                        maxTicksLimit: 10
                    }
                },

                yTemperature: {

                    type: "linear",

                    position: "left",

                    beginAtZero: false,

                    title: {
                        display: true,
                        text: "Temperature"
                    }

                },

                yPressure: {

                    type: "linear",

                    position: "right",

                    beginAtZero: false,

                    grid: {
                        drawOnChartArea: false
                    },

                    title: {
                        display: true,
                        text: "Pressure"
                    }

                },

                yFlow: {

                    type: "linear",

                    position: "left",

                    beginAtZero: false,

                    display: false

                },

                yLevel: {

                    type: "linear",

                    position: "right",

                    beginAtZero: false,

                    display: false

                }

            }

        }

    });

    console.log("Sensor graph initialized successfully.");

}
else {

    console.error(
        "Graph could not be initialized. Check sensorChart canvas or Chart.js."
    );

}

// =====================================================
// GET DATA FROM FLASK BACKEND
// =====================================================

async function getSensorData() {

    try {

        // IMPORTANT:
        // Use the deployed Flask backend on the same Render domain.
        const response = await fetch("/metrics", {
            method: "GET",
            cache: "no-store"
        });

        if (!response.ok) {

            throw new Error(
                "Backend returned HTTP " + response.status
            );

        }

        const data = await response.json();

        console.log("TEP data:", data);

        // =================================================
        // SENSOR VALUES
        // =================================================

        if (temperature) {

            temperature.textContent =
                data.temperature + " °C";

        }

        if (pressure) {

            pressure.textContent =
                data.pressure;

        }

        if (flow) {

            flow.textContent =
                data.flow;

        }

        if (level) {

            level.textContent =
                data.level + "%";

        }

        if (updatedTime) {

            updatedTime.textContent =
                "Sample: " + data.sample;

        }

        // =================================================
        // AI DIAGNOSIS
        // =================================================

        if (diagnosisStatus) {

            diagnosisStatus.textContent =
                data.diagnosis || "Analyzing";

        }

        if (anomalyStatus) {

            anomalyStatus.textContent =
                data.anomaly || "Analyzing";

        }

        if (diagnosisConfidence) {

            diagnosisConfidence.textContent =
                data.confidence !== undefined
                    ? data.confidence + "%"
                    : "--";

        }

        if (riskStatus) {

            riskStatus.textContent =
                data.risk || "Analyzing";

        }

        // =================================================
        // RECOMMENDED ACTION
        // =================================================

        if (recommendedAction) {

            if (
                data.diagnosis === "Fault 1" ||
                data.diagnosis === "Process Fault Detected"
            ) {

                recommendedAction.textContent =
                    "Investigate the abnormal process pattern and inspect the highest-impact sensor signals identified by SHAP.";

            }
            else {

                recommendedAction.textContent =
                    "Process appears normal. Continue monitoring sensor conditions.";

            }

        }

        // =================================================
        // SHAP ROOT CAUSES
        // =================================================

        if (rootCauseList) {

            rootCauseList.innerHTML = "";

            if (
                data.root_causes &&
                data.root_causes.length > 0
            ) {

                data.root_causes.forEach(function (cause) {

                    const li =
                        document.createElement("li");

                    const direction =
                        Number(cause.impact) >= 0
                            ? "↑"
                            : "↓";

                    li.innerHTML =
                        `<strong>${cause.feature}</strong>
                         ${direction}
                         Impact: ${cause.impact}
                         | Value: ${cause.value}`;

                    rootCauseList.appendChild(li);

                });

            }
            else {

                const li =
                    document.createElement("li");

                li.textContent =
                    "No significant root-cause signals detected.";

                rootCauseList.appendChild(li);

            }

        }

        // =================================================
        // ADD DATA TO GRAPH
        // =================================================

        labels.push(
            "S" + data.sample
        );

        temperatureData.push(
            Number(data.temperature)
        );

        pressureData.push(
            Number(data.pressure)
        );

        flowData.push(
            Number(data.flow)
        );

        levelData.push(
            Number(data.level)
        );

        // =================================================
        // KEEP ONLY LAST 30 SAMPLES
        // =================================================

        if (labels.length > 30) {

            labels.shift();

            temperatureData.shift();

            pressureData.shift();

            flowData.shift();

            levelData.shift();

        }

        // =================================================
        // UPDATE GRAPH
        // =================================================

        if (sensorChart) {

            sensorChart.update();

        }

    }
    catch (error) {

        console.error(
            "Backend connection error:",
            error
        );

        if (updatedTime) {

            updatedTime.textContent =
                "Backend Offline";

        }

    }

}

// =====================================================
// START DASHBOARD
// =====================================================

// Get first TEP sample immediately
getSensorData();

// Get new TEP sample every 2 seconds
setInterval(
    getSensorData,
    2000
);