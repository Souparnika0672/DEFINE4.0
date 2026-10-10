/**
 * EmergencyPass — Interactive Demo Simulation Engine
 */

let simulationInterval = null;
let currentProgress = 0;
let simulationSpeed = 1.0;

function startInteractiveDemo(tripId) {
    if (simulationInterval) clearInterval(simulationInterval);
    currentProgress = 0;
    
    const statusText = document.getElementById('demo-status-text');
    if (statusText) statusText.innerText = 'Simulation Active: In Transit...';

    runDemoStep(tripId);
}

function setDemoSpeed(speed) {
    simulationSpeed = speed;
    const badge = document.getElementById('demo-speed-badge');
    if (badge) badge.innerText = `${speed}x Speed`;
}

function runDemoStep(tripId) {
    if (simulationInterval) clearInterval(simulationInterval);

    const stepInterval = Math.max(200, 1000 / simulationSpeed);

    simulationInterval = setInterval(() => {
        currentProgress += (1.5 * simulationSpeed);
        if (currentProgress >= 100) {
            currentProgress = 100;
            clearInterval(simulationInterval);
        }

        // Post step to API
        fetch('/api/demo/simulate-step', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ trip_id: tripId, progress: currentProgress })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success && data.result) {
                const res = data.result;
                const progBar = document.getElementById('demo-progress-bar');
                if (progBar) {
                    progBar.style.width = `${currentProgress}%`;
                    progBar.innerText = `${Math.round(currentProgress)}%`;
                }

                if (currentProgress >= 100) {
                    const statusText = document.getElementById('demo-status-text');
                    if (statusText) statusText.innerText = 'SIMULATION COMPLETE: Vehicle Arrived at ER!';
                    alert('Simulation Complete: The vehicle has reached the Emergency Room.');
                }
            }
        })
        .catch(err => console.log('Sim step error', err));

    }, stepInterval);
}

function pauseInteractiveDemo() {
    if (simulationInterval) {
        clearInterval(simulationInterval);
        const statusText = document.getElementById('demo-status-text');
        if (statusText) statusText.innerText = 'Simulation Paused';
    }
}
