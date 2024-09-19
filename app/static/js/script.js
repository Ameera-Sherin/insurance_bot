document.getElementById('toggle-button').addEventListener('click', function() {
    const policyForm = document.getElementById('policy-form');
    const claimForm = document.getElementById('claim-form');
    const toggleButton = document.getElementById('toggle-button'); // Define toggleButton here
    policyForm.classList.toggle('hidden');
    claimForm.classList.toggle('hidden');

    if (policyForm.classList.contains('hidden')) {
        toggleButton.textContent = 'Compare Claim';
    } else {
        toggleButton.textContent = 'Upload Policy';
    }
});