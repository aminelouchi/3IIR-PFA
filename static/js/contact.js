// Animation au défilement
document.addEventListener('DOMContentLoaded', function() {
    const animateElements = document.querySelectorAll('.animate');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });

    animateElements.forEach(element => {
        element.style.opacity = 0;
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(element);
    });

    // Gestion du formulaire
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Récupération des valeurs du formulaire
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const subject = document.getElementById('subject').value;
            const message = document.getElementById('message').value;
            
            // Ici vous pourriez ajouter le code pour envoyer les données à votre backend
            console.log('Formulaire soumis:', { name, email, subject, message });
            
            // Message de confirmation
            alert('Merci pour votre message ! Nous vous contacterons bientôt.');
            
            // Réinitialisation du formulaire
            contactForm.reset();
        });
    }
});

   // Gestion de la soumission du formulaire
   const form = document.getElementById("contactForm");
   const formStatus = document.getElementById("form-status");
   
   async function handleSubmit(event) {
       event.preventDefault();
       const submitBtn = form.querySelector('button[type="submit"]');
       
       try {
           // Désactiver le bouton pendant l'envoi
           submitBtn.disabled = true;
           submitBtn.textContent = "Envoi en cours...";
           
           const response = await fetch(form.action, {
               method: "POST",
               body: new FormData(form),
               headers: {
                   'Accept': 'application/json'
               }
           });
           
           if (response.ok) {
               formStatus.innerHTML = '<p style="color: var(--primary);">Merci ! Votre message a été envoyé avec succès.</p>';
               form.reset();
           } else {
               throw new Error('Erreur lors de l\'envoi');
           }
       } catch (error) {
           formStatus.innerHTML = '<p style="color: var(--danger);">Désolé, une erreur s\'est produite. Veuillez réessayer plus tard.</p>';
           console.error('Error:', error);
       } finally {
           submitBtn.disabled = false;
           submitBtn.textContent = "Envoyer le message";
           
           // Masquer le message après 5 secondes
           setTimeout(() => {
               formStatus.innerHTML = '';
           }, 5000);
       }
   }
   
   form.addEventListener("submit", handleSubmit);