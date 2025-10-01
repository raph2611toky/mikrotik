function showConfirmationPopup() {
    const popup = document.getElementById('confirmation-popup');
    if (popup) {
        popup.classList.add('show');
    }
}

function hideConfirmationPopup() {
    const popup = document.getElementById('confirmation-popup');
    if (popup) {
        popup.classList.remove('show');
    }
}

function showLoader() {
    const loader = document.getElementById('loader-overlay');
    if (loader) {
        loader.classList.add('show');
    }
}

function hideLoader() {
    const loader = document.getElementById('loader-overlay');
    if (loader) {
        loader.classList.remove('show');
    }
}

function showToast(message) {
    const toast = document.getElementById('toast');
    if (toast) {
        toast.textContent = message;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

function performReset() {
    // Cacher le popup
    hideConfirmationPopup();
    
    // Afficher le loader
    showLoader();
    
    // Effectuer la requête PUT
    fetch('/reset', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoader();
        
        if (data.success) {
            // Afficher le toast de succès
            showToast(data.message || 'Compteurs réinitialisés avec succès !');
            // Recharger les données du dashboard (simuler un refresh)
            window.location.reload();
        } else {
            // Afficher un toast d'erreur
            showToast(data.error || 'Échec de la réinitialisation');
        }
    })
    .catch(error => {
        // Cacher le loader
        hideLoader();
        // Afficher un toast d'erreur
        showToast('Erreur réseau: ' + error.message);
    });
}