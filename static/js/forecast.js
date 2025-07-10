// Forecast page JavaScript
let temperatureChart = null;

document.addEventListener('DOMContentLoaded', function() {
    // Load forecast data when page loads
    loadForecast();
    
    // Add event listener to refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadForecast);
    }
});

async function loadForecast() {
    const loading = document.getElementById('loading');
    const forecastGrid = document.getElementById('forecastGrid');
    const errorMessage = document.getElementById('errorMessage');
    
    // Show loading
    loading.style.display = 'block';
    forecastGrid.style.display = 'none';
    errorMessage.style.display = 'none';
    
    try {
        const response = await fetch('/api/predict');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Hide loading and show forecast
        loading.style.display = 'none';
        forecastGrid.style.display = 'block';
        
        // Update stats
        updateStats(data.temperatures);
        
        // Create chart
        createChart(data.timestamps, data.temperatures);
        
        // Update hourly breakdown
        updateHourlyBreakdown(data.timestamps, data.temperatures);
        
    } catch (error) {
        console.error('Error loading forecast:', error);
        loading.style.display = 'none';
        errorMessage.style.display = 'block';
        
        const errorText = document.getElementById('errorText');
        errorText.textContent = `Error: ${error.message}`;
    }
}

function updateStats(temperatures) {
    const avgTemp = temperatures.reduce((a, b) => a + b, 0) / temperatures.length;
    const maxTemp = Math.max(...temperatures);
    const minTemp = Math.min(...temperatures);
    
    document.getElementById('avgTemp').textContent = `${avgTemp.toFixed(1)}°C`;
    document.getElementById('maxTemp').textContent = `${maxTemp.toFixed(1)}°C`;
    document.getElementById('minTemp').textContent = `${minTemp.toFixed(1)}°C`;
}

function createChart(timestamps, temperatures) {
    const ctx = document.getElementById('temperatureChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (temperatureChart) {
        temperatureChart.destroy();
    }
    
    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(102, 126, 234, 0.8)');
    gradient.addColorStop(1, 'rgba(102, 126, 234, 0.1)');
    
    temperatureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timestamps.map((timestamp, index) => {
                const date = new Date(timestamp);
                return `${date.getHours()}:00`;
            }),
            datasets: [{
                label: 'Temperature (°C)',
                data: temperatures,
                borderColor: '#667eea',
                backgroundColor: gradient,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#333'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#667eea',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `Temperature: ${context.parsed.y.toFixed(1)}°C`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#333'
                    },
                    ticks: {
                        maxTicksLimit: 12,
                        color: '#666'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Temperature (°C)',
                        font: {
                            size: 14,
                            weight: 'bold'
                        },
                        color: '#333'
                    },
                    ticks: {
                        color: '#666'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

function updateHourlyBreakdown(timestamps, temperatures) {
    const hourlyGrid = document.getElementById('hourlyGrid');
    hourlyGrid.innerHTML = '';
    
    // Show first 24 hours for better readability
    const hoursToShow = Math.min(24, timestamps.length);
    
    for (let i = 0; i < hoursToShow; i++) {
        const hourlyItem = document.createElement('div');
        hourlyItem.className = 'hourly-item';
        
        const date = new Date(timestamps[i]);
        const time = date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            hour12: true
        });
        
        hourlyItem.innerHTML = `
            <div class="time">${time}</div>
            <div class="temp">${temperatures[i].toFixed(1)}°C</div>
        `;
        
        hourlyGrid.appendChild(hourlyItem);
    }
}

// Add smooth animations
function addAnimations() {
    const elements = document.querySelectorAll('.stat-card, .hourly-item');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    }, {
        threshold: 0.1
    });
    
    elements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });
}

// Initialize animations when forecast loads
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(addAnimations, 500);
});