src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js">

    // Gestion des toggle switches
    document.querySelectorAll('.toggle-switch input').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const methodId = this.id;
            if (methodId === 'faceid-toggle' && this.checked) {
                const faceIdModal = new bootstrap.Modal(document.getElementById('faceIdModal'));
                faceIdModal.show();
            }
            
            if (methodId === 'fingerprint-toggle' && this.checked) {
                if (!confirm("Voulez-vous activer l'authentification par empreinte digitale ?")) {
                    this.checked = false;
                }
            }
        });
    });

    // Simulation de l'enregistrement Face ID
    document.getElementById('saveFaceId').addEventListener('click', function() {
        const progressBar = document.querySelector('.progress-bar');
        let progress = 0;
        
        const interval = setInterval(() => {
            progress += 10;
            progressBar.style.width = progress + '%';
            
            if (progress >= 100) {
                clearInterval(interval);
                document.getElementById('faceid-toggle').checked = true;
                bootstrap.Modal.getInstance(document.getElementById('faceIdModal')).hide();
                alert("Votre Face ID a été enregistré avec succès !");
            }
        }, 200);
    });

    // Bouton ajouter méthode
    document.getElementById('addAuthMethod').addEventListener('click', function() {
        alert("Fonctionnalité d'ajout de méthode d'authentification");
        // Ici vous pourriez ouvrir un modal avec d'autres options d'authentification
    });
