// Renting Page Functionality

document.addEventListener('DOMContentLoaded', function() {
    let allListings = [];
    let currentListing = null;

    // Initialize
    loadListings();
    initEventListeners();

    // Load listings from API
    async function loadListings() {
        const loadingState = document.getElementById('loading-state');
        const emptyState = document.getElementById('empty-state');
        const listingsGrid = document.getElementById('listings-grid');

        try {
            loadingState.style.display = 'block';
            listingsGrid.innerHTML = '';
            toggleEmptyState(false);

            const response = await fetch('/api/listings');
            const listings = await response.json();

            allListings = listings;

            if (listings.length === 0) {
                toggleEmptyState(true);
                listingsGrid.innerHTML = '';
            } else {
                displayListings(listings);
                toggleEmptyState(false);
            }
        } catch (error) {
            console.error('Error loading listings:', error);
            listingsGrid.innerHTML = '<p style="text-align: center; color: #c94843;">Error loading listings. Please try again.</p>';
        } finally {
            loadingState.style.display = 'none';
        }
    }

    // Display listings as cards
    function displayListings(listings) {
        const listingsGrid = document.getElementById('listings-grid');
        listingsGrid.innerHTML = '';

        listings.forEach(listing => {
            const card = createListingCard(listing);
            listingsGrid.appendChild(card);
        });
    }

    // Create listing card
    function createListingCard(listing) {
        const card = document.createElement('div');
        card.className = 'listing-card';
        
        const imageUrl = listing.main_image ? `/static/${listing.main_image}` : '/assets/carousel1.jpg';
        const priceDisplay = `₹${listing.price.toLocaleString()}`;
        
        card.innerHTML = `
            <img src="${imageUrl}" alt="${listing.title}" class="card-image" onerror="this.src='/assets/carousel1.jpg'">
            <div class="card-body">
                <div class="card-category">${listing.category}</div>
                <h3 class="card-title">${listing.title}</h3>
                <div class="card-details">
                    <div class="card-detail">
                        <i class="fas fa-tag"></i>
                        <span>${listing.equipment_name}</span>
                    </div>
                    <div class="card-detail">
                        <i class="fas fa-industry"></i>
                        <span>${listing.brand}</span>
                    </div>
                    ${listing.power_spec ? `
                    <div class="card-detail">
                        <i class="fas fa-bolt"></i>
                        <span>${listing.power_spec}</span>
                    </div>
                    ` : ''}
                    <div class="card-detail">
                        <i class="fas fa-check-circle"></i>
                        <span>${listing.condition}</span>
                    </div>
                </div>
                <div class="card-price">
                    ${priceDisplay}
                    <span class="card-price-type">/${listing.pricing_type}</span>
                </div>
                <div class="card-location">
                    <i class="fas fa-map-marker-alt"></i>
                    <span>${listing.village_city}, ${listing.district}, ${listing.state}</span>
                </div>
            </div>
            <div class="card-footer">
                <button class="btn-view-details" onclick="viewDetails(${listing.id})">
                    <i class="fas fa-info-circle"></i> View More Details
                </button>
            </div>
        `;

        return card;
    }

    // View listing details
    window.viewDetails = async function(listingId) {
        try {
            const response = await fetch(`/api/listing/${listingId}`);
            const listing = await response.json();

            currentListing = listing;
            showDetailsModal(listing);
        } catch (error) {
            console.error('Error loading listing details:', error);
            alert('Error loading listing details. Please try again.');
        }
    };

    // Show details modal
    function showDetailsModal(listing) {
        const modal = document.getElementById('details-modal');
        const modalBody = document.getElementById('modal-body');

        const mainImageUrl = listing.main_image ? `/static/${listing.main_image}` : '/assets/carousel1.jpg';
        const additionalImages = listing.additional_images || [];
        const allImages = [mainImageUrl, ...additionalImages.map(img => `/static/${img}`)].filter(Boolean);

        modalBody.innerHTML = `
            <div class="modal-image-gallery">
                <img src="${allImages[0]}" alt="${listing.title}" class="modal-main-image" id="main-modal-image">
                ${allImages.length > 1 ? `
                <div class="modal-thumbnails">
                    ${allImages.slice(1, 5).map((img, idx) => `
                        <img src="${img}" alt="Thumbnail ${idx + 1}" class="modal-thumbnail" onclick="changeMainImage('${img}')">
                    `).join('')}
                </div>
                ` : ''}
            </div>
            <h2 class="modal-title">${listing.title}</h2>
            <div class="modal-info-grid">
                <div class="modal-info-item">
                    <i class="fas fa-tag"></i>
                    <div>
                        <div class="modal-info-label">Equipment</div>
                        <div class="modal-info-value">${listing.equipment_name}</div>
                    </div>
                </div>
                <div class="modal-info-item">
                    <i class="fas fa-industry"></i>
                    <div>
                        <div class="modal-info-label">Brand</div>
                        <div class="modal-info-value">${listing.brand}</div>
                    </div>
                </div>
                <div class="modal-info-item">
                    <i class="fas fa-calendar"></i>
                    <div>
                        <div class="modal-info-label">Year</div>
                        <div class="modal-info-value">${listing.year || 'N/A'}</div>
                    </div>
                </div>
                <div class="modal-info-item">
                    <i class="fas fa-check-circle"></i>
                    <div>
                        <div class="modal-info-label">Condition</div>
                        <div class="modal-info-value">${listing.condition}</div>
                    </div>
                </div>
                ${listing.power_spec ? `
                <div class="modal-info-item">
                    <i class="fas fa-bolt"></i>
                    <div>
                        <div class="modal-info-label">Power/Spec</div>
                        <div class="modal-info-value">${listing.power_spec}</div>
                    </div>
                </div>
                ` : ''}
                <div class="modal-info-item">
                    <i class="fas fa-rupee-sign"></i>
                    <div>
                        <div class="modal-info-label">Price</div>
                        <div class="modal-info-value">₹${listing.price.toLocaleString()} / ${listing.pricing_type}</div>
                    </div>
                </div>
                <div class="modal-info-item">
                    <i class="fas fa-map-marker-alt"></i>
                    <div>
                        <div class="modal-info-label">Location</div>
                        <div class="modal-info-value">${listing.village_city}, ${listing.district}, ${listing.state} - ${listing.pincode}</div>
                    </div>
                </div>
                <div class="modal-info-item">
                    <i class="fas fa-route"></i>
                    <div>
                        <div class="modal-info-label">Service Radius</div>
                        <div class="modal-info-value">${listing.service_radius}</div>
                    </div>
                </div>
                <div class="modal-info-item">
                    <i class="fas fa-truck"></i>
                    <div>
                        <div class="modal-info-label">Transport</div>
                        <div class="modal-info-value">${listing.transport_included === 'Yes' ? 'Included' : 'Not Included'}${listing.transport_charge ? ` (₹${listing.transport_charge})` : ''}</div>
                    </div>
                </div>
                <div class="modal-info-item">
                    <i class="fas fa-calendar-check"></i>
                    <div>
                        <div class="modal-info-label">Available From</div>
                        <div class="modal-info-value">${new Date(listing.available_from).toLocaleDateString()}</div>
                    </div>
                </div>
                ${listing.available_till ? `
                <div class="modal-info-item">
                    <i class="fas fa-calendar-times"></i>
                    <div>
                        <div class="modal-info-label">Available Till</div>
                        <div class="modal-info-value">${new Date(listing.available_till).toLocaleDateString()}</div>
                    </div>
                </div>
                ` : ''}
                <div class="modal-info-item">
                    <i class="fas fa-phone"></i>
                    <div>
                        <div class="modal-info-label">Contact</div>
                        <div class="modal-info-value">${listing.phone} (${listing.contact_method})</div>
                    </div>
                </div>
            </div>
            <div class="modal-description">
                <h3>Description</h3>
                <p>${listing.description}</p>
            </div>
            ${listing.rules ? `
            <div class="modal-rules">
                <h3>Rules & Terms</h3>
                <p>${listing.rules}</p>
            </div>
            ` : ''}
            <div class="modal-actions">
                <button class="btn-rent" onclick="openRentalForm(${listing.id})">
                    <i class="fas fa-calendar-check"></i> Rent This Equipment
                </button>
            </div>
        `;

        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    // Change main image in modal
    window.changeMainImage = function(imageUrl) {
        const mainImage = document.getElementById('main-modal-image');
        if (mainImage) {
            mainImage.src = imageUrl;
        }
        // Update active thumbnail
        document.querySelectorAll('.modal-thumbnail').forEach(thumb => {
            thumb.classList.remove('active');
            if (thumb.src.includes(imageUrl)) {
                thumb.classList.add('active');
            }
        });
    };

    // Open rental form
    window.openRentalForm = function(listingId) {
        if (!currentListing || currentListing.id !== listingId) {
            // Reload listing details if needed
            viewDetails(listingId);
            setTimeout(() => showRentalForm(listingId), 500);
        } else {
            showRentalForm(listingId);
        }
    };

    // Show rental form
    function showRentalForm(listingId) {
        const listing = currentListing;
        if (!listing) return;

        const rentalModal = document.getElementById('rental-modal');
        const rentalFormContainer = document.getElementById('rental-form-container');

        const today = new Date().toISOString().split('T')[0];
        const maxDate = listing.available_till ? new Date(listing.available_till).toISOString().split('T')[0] : '';

        rentalFormContainer.innerHTML = `
            <div class="rental-form">
                <h2><i class="fas fa-calendar-check"></i> Rent Equipment</h2>
                <form id="rental-form" onsubmit="submitRental(event, ${listing.id})">
                    <div class="rental-form-group">
                        <label for="start_date">Start Date <span style="color: #c94843;">*</span></label>
                        <input type="date" id="start_date" name="start_date" required min="${today}" ${maxDate ? `max="${maxDate}"` : ''}>
                    </div>
                    <div class="rental-form-group">
                        <label for="days">Number of Days <span style="color: #c94843;">*</span></label>
                        <input type="number" id="days" name="days" min="1" required onchange="calculateTotal(${listing.price}, '${listing.pricing_type}', ${listing.transport_charge || 0}, '${listing.transport_included}')">
                    </div>
                    <div class="rental-summary" id="rental-summary">
                        <div class="rental-summary-item">
                            <span>Price per ${listing.pricing_type}:</span>
                            <span>₹${listing.price.toLocaleString()}</span>
                        </div>
                        ${listing.transport_included === 'No' && listing.transport_charge ? `
                        <div class="rental-summary-item" id="transport-item" style="display: none;">
                            <span>Transport Charge:</span>
                            <span>₹${listing.transport_charge.toLocaleString()}</span>
                        </div>
                        ` : ''}
                        <div class="rental-summary-item" id="total-item">
                            <span>Total Amount:</span>
                            <span id="total-amount">₹0</span>
                        </div>
                    </div>
                    <button type="submit" class="btn-rent">
                        <i class="fas fa-check"></i> Confirm Rental
                    </button>
                </form>
            </div>
        `;

        // Close details modal and show rental modal
        document.getElementById('details-modal').classList.remove('show');
        rentalModal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    // Calculate total
    window.calculateTotal = function(price, pricingType, transportCharge, transportIncluded) {
        const days = parseInt(document.getElementById('days').value) || 0;
        let total = 0;

        if (pricingType === 'Per day') {
            total = price * days;
        } else if (pricingType === 'Per hour') {
            total = price * days * 8; // Assuming 8 hours per day
        } else if (pricingType === 'Per acre') {
            total = price * days; // Assuming days = acres
        } else {
            total = price; // Per season
        }

        if (transportIncluded === 'No' && transportCharge) {
            const transportItem = document.getElementById('transport-item');
            if (transportItem) {
                transportItem.style.display = 'flex';
            }
            total += transportCharge;
        }

        const totalAmount = document.getElementById('total-amount');
        if (totalAmount) {
            totalAmount.textContent = `₹${total.toLocaleString()}`;
        }
    };

    // Submit rental
    window.submitRental = async function(event, listingId) {
        event.preventDefault();

        const formData = new FormData(event.target);
        formData.append('listing_id', listingId);
        formData.append('days', document.getElementById('days').value);

        const submitBtn = event.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

        try {
            const response = await fetch('/rent_equipment', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                alert('Rental request submitted successfully!');
                document.getElementById('rental-modal').classList.remove('show');
                document.body.style.overflow = 'visible';
            } else {
                alert('Error: ' + (data.message || 'Failed to submit rental request'));
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        } catch (error) {
            console.error('Error submitting rental:', error);
            alert('An error occurred. Please try again.');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    };

    // Initialize event listeners
    function initEventListeners() {
        // Close modals
        document.getElementById('close-modal').addEventListener('click', function() {
            document.getElementById('details-modal').classList.remove('show');
            document.body.style.overflow = 'visible';
        });

        document.getElementById('close-rental-modal').addEventListener('click', function() {
            document.getElementById('rental-modal').classList.remove('show');
            document.body.style.overflow = 'visible';
        });

        // Close on overlay click
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', function(e) {
                if (e.target === overlay) {
                    overlay.closest('.details-modal, .rental-modal').classList.remove('show');
                    document.body.style.overflow = 'visible';
                }
            });
        });

        const searchInput = document.getElementById('search-filter');
        const clearSearchBtn = document.getElementById('clear-search');
        const categorySelect = document.getElementById('category-filter');
        const locationInput = document.getElementById('location-filter');
        const priceMinInput = document.getElementById('price-min');
        const priceMaxInput = document.getElementById('price-max');
        const sortSelect = document.getElementById('sort-order');
        const applyBtn = document.getElementById('apply-filters');
        const resetBtn = document.getElementById('clear-filters');

        const debouncedFilter = debounce(applyFilters, 250);

        applyBtn.addEventListener('click', applyFilters);
        searchInput.addEventListener('input', debouncedFilter);
        locationInput.addEventListener('input', debouncedFilter);
        categorySelect.addEventListener('change', applyFilters);
        sortSelect.addEventListener('change', applyFilters);
        priceMinInput.addEventListener('input', debouncedFilter);
        priceMaxInput.addEventListener('input', debouncedFilter);

        clearSearchBtn.addEventListener('click', function() {
            if (searchInput.value.trim() === '') return;
            searchInput.value = '';
            applyFilters();
        });

        resetBtn.addEventListener('click', function() {
            resetFilters({
                searchInput,
                categorySelect,
                locationInput,
                priceMinInput,
                priceMaxInput,
                sortSelect
            });
        });

        locationInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                applyFilters();
            }
        });
    }

    // Apply filters
    function applyFilters() {
        const categoryFilter = document.getElementById('category-filter').value.toLowerCase();
        const locationFilter = document.getElementById('location-filter').value.trim().toLowerCase();
        const searchQuery = document.getElementById('search-filter').value.trim().toLowerCase();
        const priceMin = parseInt(document.getElementById('price-min').value, 10);
        const priceMax = parseInt(document.getElementById('price-max').value, 10);
        const sortOption = document.getElementById('sort-order').value;

        let filtered = [...allListings];

        if (categoryFilter) {
            filtered = filtered.filter(listing => 
                listing.category && listing.category.toLowerCase() === categoryFilter
            );
        }

        if (locationFilter) {
            filtered = filtered.filter(listing => {
                const locations = [
                    listing.state,
                    listing.district,
                    listing.village_city
                ].filter(Boolean).map(loc => loc.toLowerCase());
                return locations.some(loc => loc.includes(locationFilter));
            });
        }

        if (searchQuery) {
            filtered = filtered.filter(listing => {
                const searchableFields = [
                    listing.title,
                    listing.equipment_name,
                    listing.brand,
                    listing.description,
                    listing.category
                ];

                return searchableFields.filter(Boolean).some(field =>
                    field.toLowerCase().includes(searchQuery)
                );
            });
        }

        if (!isNaN(priceMin)) {
            filtered = filtered.filter(listing => listing.price >= priceMin);
        }

        if (!isNaN(priceMax)) {
            filtered = filtered.filter(listing => listing.price <= priceMax);
        }

        filtered = sortListings(filtered, sortOption);

        displayListings(filtered);
        toggleEmptyState(filtered.length === 0);
    }

    function sortListings(listings, sortOption) {
        const sorted = [...listings];

        switch (sortOption) {
            case 'price-asc':
                return sorted.sort((a, b) => a.price - b.price);
            case 'price-desc':
                return sorted.sort((a, b) => b.price - a.price);
            case 'newest':
                return sorted.sort((a, b) => getListingTimestamp(b) - getListingTimestamp(a));
            default:
                return sorted;
        }
    }

    function getListingTimestamp(listing) {
        const candidates = [listing.created_at, listing.updated_at, listing.available_from];
        for (const value of candidates) {
            const timestamp = value ? new Date(value).getTime() : NaN;
            if (!isNaN(timestamp)) {
                return timestamp;
            }
        }
        return 0;
    }

    function toggleEmptyState(showEmpty) {
        const emptyState = document.getElementById('empty-state');
        emptyState.style.display = showEmpty ? 'block' : 'none';
    }

    function resetFilters(elements) {
        elements.searchInput.value = '';
        elements.categorySelect.value = '';
        elements.locationInput.value = '';
        elements.priceMinInput.value = '';
        elements.priceMaxInput.value = '';
        elements.sortSelect.value = 'recommended';
        applyFilters();
    }

    function debounce(fn, delay = 250) {
        let timeoutId;
        return function(...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => fn.apply(this, args), delay);
        };
    }
});


