window.mechanicDashboard = window.mechanicDashboard || {};

document.addEventListener('DOMContentLoaded', () => {
    const detailsModal = document.getElementById('detailsModal');
    const requestModal = document.getElementById('requestModal');
    const requestForm = document.getElementById('requestForm');
    const requestFeedback = document.getElementById('requestFeedback');

    const openModal = (modal) => modal && modal.classList.add('active');
    const closeModal = (modal) => modal && modal.classList.remove('active');

    document.querySelectorAll('[data-close]').forEach(btn => {
        btn.addEventListener('click', () => closeModal(btn.closest('.modal')));
    });

    [detailsModal, requestModal].forEach(modal => {
        if (!modal) return;
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeModal(modal);
            }
        });
    });

    document.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('detailsName').textContent = btn.dataset.name;
            document.getElementById('detailsSpecialization').textContent = `Specialization: ${btn.dataset.specialization}`;
            document.getElementById('detailsExperience').textContent = btn.dataset.experience === 'NA'
                ? 'Experience: info not provided'
                : `Experience: ${btn.dataset.experience} years`;
            document.getElementById('detailsCharge').textContent = `Base visit: ${btn.dataset.charge}`;
            document.getElementById('detailsLocations').textContent = `Service areas: ${btn.dataset.location}`;
            document.getElementById('detailsDescription').textContent = btn.dataset.description;
            openModal(detailsModal);
        });
    });

    document.querySelectorAll('.request-service-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            if (!requestForm) return;
            requestForm.reset();
            document.getElementById('requestMechanicName').textContent = btn.dataset.mechanicName;
            document.getElementById('requestMechanicId').value = btn.dataset.mechanicId;
            if (requestFeedback) requestFeedback.textContent = '';
            openModal(requestModal);
        });
    });

    if (requestForm) {
        requestForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (requestFeedback) {
                requestFeedback.textContent = 'Sending request...';
                requestFeedback.style.color = '#1f2933';
            }
            const mechanicId = document.getElementById('requestMechanicId').value;
            const formData = new FormData(requestForm);
            try {
                const response = await fetch(`/mechanics/${mechanicId}/request`, {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if (requestFeedback) {
                    requestFeedback.textContent = data.message;
                    requestFeedback.style.color = data.success ? '#2e7d32' : '#b91c1c';
                }
                if (data.success) {
                    requestForm.reset();
                    setTimeout(() => closeModal(requestModal), 1500);
                }
            } catch (error) {
                if (requestFeedback) {
                    requestFeedback.textContent = 'Unable to send request at the moment.';
                    requestFeedback.style.color = '#b91c1c';
                }
            }
        });
    }

    const availabilityToggle = document.getElementById('availabilityToggle');
    const availabilityStatus = document.getElementById('availabilityStatus');
    if (availabilityToggle && window.mechanicDashboard?.hasProfile) {
        availabilityToggle.addEventListener('change', async () => {
            const desiredState = availabilityToggle.checked;
            availabilityStatus.textContent = 'Updating...';
            try {
                const res = await fetch(window.mechanicDashboard.availabilityEndpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ is_available: desiredState })
                });
                const data = await res.json();
                if (!data.success) {
                    throw new Error(data.message || 'Failed');
                }
                availabilityStatus.textContent = data.is_available ? 'Currently visible on listing' : 'Hidden from listing';
            } catch (error) {
                availabilityToggle.checked = !desiredState;
                availabilityStatus.textContent = 'Update failed, please retry.';
            }
        });
    }

    document.querySelectorAll('.request-status-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const requestCard = btn.closest('.request-card');
            if (!requestCard || !window.mechanicDashboard?.requestEndpointTemplate) return;
            const requestId = requestCard.dataset.requestId;
            const targetStatus = btn.dataset.status;
            const statusPill = requestCard.querySelector('.status-pill');
            const endpoint = window.mechanicDashboard.requestEndpointTemplate.replace('/0/', `/${requestId}/`);

            btn.textContent = 'Updating...';
            btn.disabled = true;
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: targetStatus })
                });
                const data = await response.json();
                if (!data.success) {
                    throw new Error(data.message || 'Failed to update');
                }
                statusPill.textContent = data.status;
                statusPill.className = `status-pill ${data.status}`;
                requestCard.querySelectorAll('.request-status-btn').forEach(actionBtn => {
                    if (data.status === 'Completed') {
                        actionBtn.remove();
                    } else if (actionBtn.dataset.status === data.status) {
                        actionBtn.remove();
                    } else {
                        actionBtn.textContent = data.status === 'Pending' ? 'Mark as Accepted' : 'Mark as Completed';
                        actionBtn.disabled = false;
                    }
                });
            } catch (error) {
                btn.textContent = `Retry ${targetStatus}`;
                btn.disabled = false;
            }
        });
    });
});

