// Initialisation des datepickers
flatpickr(".datepicker", {
    locale: "fr",
    dateFormat: "d/m/Y",
    defaultDate: new Date()
});

// Sélection rapide de période
document.getElementById('lastWeek').addEventListener('click', function() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - 7);
    
    document.getElementById('startDate')._flatpickr.setDate(startDate);
    document.getElementById('endDate')._flatpickr.setDate(endDate);
});

document.getElementById('lastMonth').addEventListener('click', function() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setMonth(endDate.getMonth() - 1);
    
    document.getElementById('startDate')._flatpickr.setDate(startDate);
    document.getElementById('endDate')._flatpickr.setDate(endDate);
});

document.getElementById('lastYear').addEventListener('click', function() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setFullYear(endDate.getFullYear() - 1);
    
    document.getElementById('startDate')._flatpickr.setDate(startDate);
    document.getElementById('endDate')._flatpickr.setDate(endDate);
});

document.getElementById('allTime').addEventListener('click', function() {
    document.getElementById('startDate')._flatpickr.clear();
    document.getElementById('endDate')._flatpickr.clear();
});

// Sélection/désélection de toutes les serres
document.getElementById('selectAll').addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('.serre-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
    });
});

// Sélection/désélection de toutes les options
document.getElementById('selectAllOptions').addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('.report-option-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = this.checked;
    });
});

// Vérification si toutes les serres sont sélectionnées
document.getElementById('serresList').addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('.serre-checkbox');
    const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
    document.getElementById('selectAll').checked = allChecked;
});

// Génération du PDF
document.getElementById('generateReport').addEventListener('click', function() {
    // Afficher le modal
    const modal = new bootstrap.Modal(document.getElementById('pdfPreviewModal'));
    modal.show();
    
    // Simuler la génération du PDF (dans un vrai projet, vous utiliseriez une vraie génération)
    setTimeout(() => {
        document.getElementById('pdfLoading').style.display = 'none';
        document.getElementById('pdfPreview').style.display = 'block';
        
        // Dans un vrai projet, vous utiliseriez:
        // generateActualPdf();
        // Pour cet exemple, nous affichons juste un message
        document.getElementById('pdfPreview').srcdoc = `
            <html>
                <head>
                    <title>Rapport des Serres</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        .header { text-align: center; margin-bottom: 30px; }
                        .logo { height: 80px; margin-bottom: 20px; }
                        h1 { color: #2c7873; }
                        .section { margin-bottom: 30px; }
                        .section-title { background-color: #f5f7fa; padding: 10px; border-left: 4px solid #2c7873; }
                        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f2f2f2; }
                        .chart-container { width: 100%; height: 300px; margin: 20px 0; }
                        .footer { margin-top: 50px; text-align: center; font-size: 12px; color: #777; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Rapport des Serres</h1>
                        <p>Période du ${document.getElementById('startDate').value || 'N/A'} au ${document.getElementById('endDate').value || 'N/A'}</p>
                    </div>
                    
                    <div class="section">
                        <h2 class="section-title">1. Serres incluses</h2>
                        <ul>
                            ${getSelectedSerres().map(serre => `<li>${serre}</li>`).join('')}
                        </ul>
                    </div>
                    
                    ${document.getElementById('optionHistory').checked ? `
                    <div class="section">
                        <h2 class="section-title">2. Historique des données</h2>
                        <table>
                            <tr>
                                <th>Date</th>
                                <th>Température (°C)</th>
                                <th>Humidité air (%)</th>
                                <th>Humidité sol (%)</th>
                                <th>CO2 (ppm)</th>
                                <th>Luminosité (lux)</th>
                            </tr>
                            <tr>
                                <td>01/06/2023</td>
                                <td>24.5</td>
                                <td>65</td>
                                <td>42</td>
                                <td>450</td>
                                <td>1200</td>
                            </tr>
                            <!-- Plus de données historiques ici -->
                        </table>
                    </div>
                    ` : ''}
                    
                    ${document.getElementById('optionGraphs').checked ? `
                    <div class="section">
                        <h2 class="section-title">3. Graphiques</h2>
                        <div class="chart-container">
                            <!-- Graphique serait rendu ici dans un vrai PDF -->
                            <img src="https://via.placeholder.com/800x300?text=Graphique+des+données" style="width: 100%;">
                        </div>
                    </div>
                    ` : ''}
                    
                    ${document.getElementById('optionAlerts').checked ? `
                    <div class="section">
                        <h2 class="section-title">4. Alertes et notifications</h2>
                        <table>
                            <tr>
                                <th>Date</th>
                                <th>Type</th>
                                <th>Message</th>
                                <th>Solution</th>
                            </tr>
                            <tr>
                                <td>02/06/2023 08:15</td>
                                <td>Température</td>
                                <td>Température a dépassé le seuil min (8°C)</td>
                                <td>Activez le chauffage pour maintenir une température stable</td>
                            </tr>
                            <!-- Plus d'alertes ici -->
                        </table>
                    </div>
                    ` : ''}
                    
                    ${document.getElementById('optionAverages').checked ? `
                    <div class="section">
                        <h2 class="section-title">5. Statistiques</h2>
                        <table>
                            <tr>
                                <th>Paramètre</th>
                                <th>Minimum</th>
                                <th>Maximum</th>
                                <th>Moyenne</th>
                            </tr>
                            <tr>
                                <td>Température</td>
                                <td>8°C</td>
                                <td>28°C</td>
                                <td>22°C</td>
                            </tr>
                            <!-- Plus de statistiques ici -->
                        </table>
                    </div>
                    ` : ''}
                    
                    <div class="footer">
                        <p>Rapport généré le ${new Date().toLocaleDateString()} à ${new Date().toLocaleTimeString()}</p>
                        <p>Système de Gestion des Serres Intelligentes</p>
                    </div>
                </body>
            </html>
        `;
    }, 2000);
});

// Fonction pour obtenir les serres sélectionnées
function getSelectedSerres() {
    const selected = [];
    document.querySelectorAll('.serre-checkbox:checked').forEach(checkbox => {
        selected.push(checkbox.nextElementSibling.textContent.trim());
    });
    return selected.length > 0 ? selected : ['Aucune serre sélectionnée'];
}

// Dans un vrai projet, vous auriez une fonction comme celle-ci pour générer le vrai PDF
function generateActualPdf() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    // Ajouter le titre
    doc.setFontSize(20);
    doc.setTextColor(44, 120, 115);
    doc.text('Rapport des Serres', 105, 20, { align: 'center' });
    
    // Ajouter la période
    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text(`Période du ${document.getElementById('startDate').value || 'N/A'} au ${document.getElementById('endDate').value || 'N/A'}`, 105, 30, { align: 'center' });
    
    // Ajouter les serres sélectionnées
    doc.setFontSize(14);
    doc.text('1. Serres incluses', 14, 45);
    
    doc.setFontSize(12);
    getSelectedSerres().forEach((serre, index) => {
        doc.text(`- ${serre}`, 20, 55 + (index * 7));
    });
    
    // Ajouter les autres sections selon les options sélectionnées
    let yPosition = 90;
    
    if (document.getElementById('optionHistory').checked) {
        // Ajouter l'historique des données
        doc.setFontSize(14);
        doc.text('2. Historique des données', 14, yPosition);
        yPosition += 10;
        
        // Tableau des données historiques
        doc.autoTable({
            startY: yPosition,
            head: [['Date', 'Température', 'Humidité air', 'Humidité sol', 'CO2', 'Luminosité']],
            body: [
                ['01/06/2023', '24.5°C', '65%', '42%', '450ppm', '1200lux'],
                // Plus de données...
            ],
            styles: { fontSize: 10 },
            headStyles: { fillColor: [242, 242, 242] }
        });
        
        yPosition = doc.lastAutoTable.finalY + 10;
    }
    
    // Sauvegarder ou afficher le PDF
    const pdfUrl = URL.createObjectURL(doc.output('blob'));
    document.getElementById('pdfPreview').src = pdfUrl;
}

// Boutons d'impression et de téléchargement
document.getElementById('printPdf').addEventListener('click', function() {
    const iframe = document.getElementById('pdfPreview');
    iframe.contentWindow.print();
});

document.getElementById('downloadPdf').addEventListener('click', function() {
    // Dans un vrai projet, vous téléchargeriez le vrai PDF
    alert('Dans une implémentation réelle, cela téléchargerait le PDF généré.');
});
