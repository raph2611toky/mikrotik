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

function showLimitPopup() {
    const popup = document.getElementById('limit-popup');
    if (popup) {
        popup.classList.add('show');
    }
}

function hideLimitPopup() {
    const popup = document.getElementById('limit-popup');
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

function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    if (toast) {
        toast.textContent = message;
        toast.classList.remove('error');
        if (isError) {
            toast.classList.add('error');
        }
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

function performReset() {
    hideConfirmationPopup();
    showLoader();
    
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
            showToast(data.message || 'Compteurs réinitialisés avec succès !');
            window.location.reload();
        } else {
            showToast(data.error || 'Échec de la réinitialisation', true);
        }
    })
    .catch(error => {
        hideLoader();
        showToast('Erreur réseau: ' + error.message, true);
    });
}

function performSetLimit() {
    const totalLimitInput = document.getElementById('total-limit');
    const unitSelect = document.getElementById('limit-unit');
    
    if (!totalLimitInput || !unitSelect) {
        showToast('Erreur: formulaire incomplet', true);
        return;
    }

    const totalLimit = parseFloat(totalLimitInput.value);
    const unit = unitSelect.value;

    if (isNaN(totalLimit) || totalLimit <= 0) {
        showToast('Veuillez entrer une limite valide', true);
        return;
    }

    hideLimitPopup();
    showLoader();

    fetch('/set_limit', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ total_limit: totalLimit, unit: unit })
    })
    .then(response => response.json())
    .then(data => {
        hideLoader();
        if (data.success) {
            showToast(data.message || 'Limites mises à jour avec succès !');
            window.location.reload();
        } else {
            showToast(data.error || 'Échec de la mise à jour des limites', true);
        }
    })
    .catch(error => {
        hideLoader();
        showToast('Erreur réseau: ' + error.message, true);
    });
}