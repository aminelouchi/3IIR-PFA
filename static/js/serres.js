// Gestion de la modal d'ajout
const addButton = document.getElementById('addButton');
const addModal = document.getElementById('addModal');

addButton.addEventListener('click', () => {
    addModal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Empêche le scroll
});

// Fermer le modal ajout en cliquant à l'extérieur
addModal.addEventListener('click', (e) => {
    if (e.target === addModal) {
        addModal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
});

// Validation du formulaire d'ajout
const form = document.getElementById('serreForm');

form.addEventListener('submit', (e) => {
    let isValid = true;

    // Vérifications
    if (!document.getElementById('serreName').value) {
        document.getElementById('nameError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('nameError').style.display = 'none';
    }

    if (!document.getElementById('adresse').value) {
        document.getElementById('adresseError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('adresseError').style.display = 'none';
    }

    if (!document.getElementById('city').value) {
        document.getElementById('cityError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('cityError').style.display = 'none';
    }

    if (!document.getElementById('superficie').value || isNaN(document.getElementById('superficie').value)) {
        document.getElementById('superficieError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('superficieError').style.display = 'none';
    }

    if (!isValid) {
        e.preventDefault();
        const firstError = document.querySelector('.error[style="display: block;"]');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    } else {
        addModal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
});

// Fermer la modal avec Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && addModal.classList.contains('active')) {
        addModal.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
});

// Ouverture du modal d'édition
document.querySelectorAll('.btn-edit').forEach(button => {
    button.addEventListener('click', function() {
        const serreId = this.getAttribute('data-id');

        fetch(`/get_serre/${serreId}`)
            .then(response => response.json())
            .then(data => {
                // Remplir les champs du formulaire de modification
                document.getElementById('editId').value = serreId; // 🔥 Ajout important !
                document.getElementById('editSerreName').value = data.nom_serre;
                document.getElementById('editAdresse').value = data.adresse;
                document.getElementById('editCity').value = data.ville;
                document.getElementById('editSuperficie').value = data.superficie;

                // Afficher le modal d'édition
                document.getElementById('editModal').style.display = 'block';
            })
            .catch(error => {
                console.error('Erreur lors du chargement des données de la serre:', error);
                alert('Impossible de charger les données de la serre.');
            });
    });
});

// Soumission du formulaire de modification
document.getElementById('editSerreForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const serreId = document.getElementById('editId').value;
    
    fetch(`/edit_serre/${serreId}`, {
        method: 'POST',
        body: new FormData(this),
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            // ✅ Fermer le modal
            document.getElementById('editModal').style.display = 'none';
            document.body.style.overflow = 'auto'; // Réactive le scroll du body

            location.reload();
        } else {
            throw new Error('Erreur lors de la modification');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.message);
    });
});


// Script pour la suppression
document.querySelectorAll('.btn-delete').forEach(button => {
    button.addEventListener('click', function() {
        const serreId = this.getAttribute('data-id');

        if (confirm("Êtes-vous sûr de vouloir supprimer cette serre ?")) {
            fetch(`/delete_serre/${serreId}`, { method: 'POST' })
                .then(response => {
                    if (response.ok) {
                        location.reload();
                    } else {
                        alert('Erreur lors de la suppression.');
                    }
                })
                .catch(error => {
                    console.error('Erreur lors de la suppression:', error);
                    alert('Erreur lors de la suppression.');
                });
        }
    });
});

// Debug console (optionnel, utile en développement)
document.getElementById('serreForm').addEventListener('submit', function(e) {
    console.log('Formulaire d\'ajout soumis !');
    console.log('Données envoyées:', Object.fromEntries(new FormData(this)));
});
