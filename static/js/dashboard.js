function fetchLiveData() {
    fetch("/latest_data")
        .then(response => response.json())
        .then(data => {
            if (!data || data.error) {
                console.error("Erreur dans les données :", data.error);
                return;
            }

            const valeurs = data.valeurs;
            const alertes = data.alertes;

            // Mise à jour des valeurs
            document.getElementById('temperature-value').textContent = valeurs["Température"];
            document.getElementById('luminosite-value').textContent = valeurs["Luminosité"];
            document.getElementById('humidite_sol-value').textContent = valeurs["Humidité du sol"];
            document.getElementById('humidite_air-value').textContent = valeurs["Humidité air"];
            document.getElementById('co2-value').textContent = valeurs["CO2"];
            document.getElementById('arrosage-value').textContent = valeurs["Arrosage"];
            document.getElementById('fertilisation-value').textContent = valeurs["Fertilisation"];

            // Gestion des alertes visuelles (clignotement)
            toggleAlert('temperature', alertes["Température"]);
            toggleAlert('luminosite', alertes["Luminosité"]);
            toggleAlert('humidite_sol', alertes["Humidité du sol"]);
            toggleAlert('humidite_air', alertes["Humidité air"]);
            toggleAlert('co2', alertes["CO2"]);
        })
        .catch(err => {
            console.error("Erreur lors du fetch /latest_data :", err);
        });
}

function toggleAlert(id, isAlerting) {
    const container = document.getElementById(id);
    if (!container) return;

    if (isAlerting) {
        container.classList.add("alert-blink");
    } else {
        container.classList.remove("alert-blink");
    }
}

// Exécution au chargement + toutes les 5 secondes
setInterval(fetchLiveData, 5000);
fetchLiveData();

function updateNotifications() {
    fetch("/notifications")
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById("messages");
            container.innerHTML = "";

            data.forEach((n, i) => {
                const div = document.createElement("div");
                div.className = n.seuil === "max" ? "message notification-high" : "message notification-low";
                div.innerHTML = `
                    <p><strong>Notification ${i + 1} :</strong> ${n.message}</p>
                    <p>Solution : ${n.solution}</p>
                `;
                container.appendChild(div);
            });
        });
}

setInterval(updateNotifications, 5000);
updateNotifications();


function fetchHistorique() {
    fetch("/historique")
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('historique-body');
            tbody.innerHTML = "";

            data.forEach(row => {
                const tr = document.createElement("tr");
                tr.style.textAlign = "center";
                tr.innerHTML = `
                    <td style="padding: 10px;">${row.Température} °C</td>
                    <td style="padding: 10px;">${row.Humidité_sol} %</td>
                    <td style="padding: 10px;">${row.Humidité_air} %</td>
                    <td style="padding: 10px;">${row.CO2} ppm</td>
                    <td style="padding: 10px;">${row.Luminosité} lux</td>
                    <td style="padding: 10px;">-</td>
                    <td style="padding: 10px;">-</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Erreur historique:", err));
}

fetchHistorique();


function renderLineChart(id, labels, data, label, color = "rgba(0, 199, 214, 0.8)") {
    new Chart(document.getElementById(id).getContext("2d"), {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                fill: false,
                borderColor: color,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: "#fff" }
                }
            },
            scales: {
                x: {
                    ticks: { color: "#aaa" }
                },
                y: {
                    ticks: { color: "#aaa" }
                }
            }
        }
    });
}

function fetchGraphData() {
    fetch("/graph_data")
	.then(response => response.json())
	.then(data => {
		console.log("📊 Données reçues :", data);  // ✅ ici c’est bon
		renderLineChart("tempChart", data.labels, data.Température, "Température (°C)");
		renderLineChart("soilChart", data.labels, data.Humidité_sol, "Humidité du sol (%)");
		renderLineChart("airChart", data.labels, data.Humidité_air, "Humidité de l'air (%)");
		renderLineChart("co2Chart", data.labels, data.CO2, "CO₂ (ppm)");
		renderLineChart("lightChart", data.labels, data.Luminosité, "Luminosité (lux)");
	})
	.catch(error => {
		console.error("❌ Erreur lors du chargement des données graphiques :", error);
	});

}

fetchGraphData();
