document.getElementById('updateBtn').addEventListener('click', function(event) {
    event.preventDefault(); // Empêche l'envoi direct du formulaire

    Swal.fire({
        title: 'Confirmer la modification',
        text: "Voulez-vous vraiment enregistrer ces modifications ?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Oui, enregistrer',
        cancelButtonText: 'Annuler'
    }).then((result) => {
        if (result.isConfirmed) {
            // Si confirmé, soumettre le formulaire
            this.closest('form').submit();
        }
    });
});
