// Rent Dashboard Functionality

document.addEventListener('DOMContentLoaded', function() {
    let rentals = [];

    // Load user's rentals
    loadMyRentals();

    // Load rentals from API
    async function loadMyRentals() {
        const loadingState = document.getElementById('loading-state');
        const emptyState = document.getElementById('empty-state');
        const rentalsGrid = document.getElementById('rentals-grid');

        try {
            loadingState.style.display = 'block';
            rentalsGrid.innerHTML = '';
            emptyState.style.display = 'none';

            const response = await fetch('/api/my_rentals');
            const data = await response.json();

            rentals = data;

            if (rentals.length === 0) {
                emptyState.style.display = 'block';
                rentalsGrid.innerHTML = '';
            } else {
                displayRentals(rentals);
            }
        } catch (error) {
            console.error('Error loading rentals:', error);
            rentalsGrid.innerHTML = '<p style="text-align: center; color: #c94843; padding: 2rem;">Error loading rentals. Please try again.</p>';
        } finally {
            loadingState.style.display = 'none';
        }
    }

    // Display rentals as cards
    function displayRentals(rentals) {
        const rentalsGrid = document.getElementById('rentals-grid');
        rentalsGrid.innerHTML = '';

        rentals.forEach(rental => {
            const card = createRentalCard(rental);
            rentalsGrid.appendChild(card);
        });
    }

    // Create rental card
    function createRentalCard(rental) {
        const card = document.createElement('div');
        card.className = 'rental-card';
        
        const imageUrl = rental.main_image ? `/static/${rental.main_image}` : '/assets/carousel1.jpg';
        
        // Format dates
        const startDate = new Date(rental.start_date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        const endDate = new Date(rental.end_date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        // Determine status and styling
        let statusClass = '';
        let statusText = rental.status;
        let expiryClass = '';
        let expiryText = '';
        
        if (rental.is_expired) {
            statusClass = 'expired';
            statusText = 'Expired';
            expiryClass = 'expired';
            expiryText = 'Expired';
        } else if (rental.days_remaining <= 3) {
            statusClass = 'expiring-soon';
            statusText = 'Expiring Soon';
            expiryClass = 'expiring-soon';
            expiryText = `${rental.days_remaining} day${rental.days_remaining !== 1 ? 's' : ''} left`;
        } else {
            statusClass = '';
            statusText = 'Active';
            expiryClass = 'active';
            expiryText = `${rental.days_remaining} day${rental.days_remaining !== 1 ? 's' : ''} remaining`;
        }
        
        card.innerHTML = `
            <div class="card-image-wrapper">
                <img src="${imageUrl}" alt="${rental.title}" class="card-image" onerror="this.src='/assets/carousel1.jpg'">
                <div class="card-status ${statusClass}">${statusText}</div>
            </div>
            <div class="card-body">
                <div class="card-category">${rental.category}</div>
                <h3 class="card-title">${rental.title}</h3>
                <div class="card-details">
                    <div class="card-detail">
                        <i class="fas fa-tag"></i>
                        <span>${rental.equipment_name}</span>
                    </div>
                    <div class="card-detail">
                        <i class="fas fa-industry"></i>
                        <span>${rental.brand}</span>
                    </div>
                </div>
                <div class="card-price">
                    ₹${rental.total_amount.toLocaleString()}
                    <span class="card-price-type">Total Amount</span>
                </div>
                <div class="card-location">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>${rental.location}</span>
                </div>
                <div class="rental-dates">
                    <div class="rental-dates-header">
                        <i class="fas fa-calendar-alt"></i>
                        Rental Period
                    </div>
                    <div class="date-row">
                        <span class="date-label">Start Date:</span>
                        <span class="date-value">${startDate}</span>
                    </div>
                    <div class="date-row">
                        <span class="date-label">End Date:</span>
                        <span class="date-value">${endDate}</span>
                    </div>
                    <div class="date-row">
                        <span class="date-label">Duration:</span>
                        <span class="date-value">${rental.days} day${rental.days !== 1 ? 's' : ''}</span>
                    </div>
                    <div class="expiry-info">
                        <span class="expiry-label">Status:</span>
                        <span class="expiry-value ${expiryClass}">${expiryText}</span>
                    </div>
                </div>
                <div class="owner-info">
                    <div class="owner-info-header">
                        <i class="fas fa-user"></i>
                        Owner Information
                    </div>
                    <div class="owner-detail">
                        <i class="fas fa-user-circle"></i>
                        <span>${rental.owner_name}</span>
                    </div>
                    <div class="owner-detail">
                        <i class="fas fa-phone"></i>
                        <span>${rental.phone} (${rental.contact_method})</span>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <a href="/renting" class="btn-view-listing">
                    <i class="fas fa-search"></i> Rent More Equipment
                </a>
            </div>
        `;

        return card;
    }
});


