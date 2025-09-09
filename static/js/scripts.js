// Global toast helper usable across pages
function showToast(message, type = 'info') {
	const toast = document.getElementById('toast');
	if (!toast) return;
	const toastMessage = document.getElementById('toast-message');
	const toastHeader = toast.querySelector('.toast-header');
	toastMessage.textContent = message;
	const icon = toastHeader.querySelector('i');
	icon.className = type === 'success' ? 'fas fa-check-circle me-2 text-success' :
					 type === 'error' ? 'fas fa-exclamation-circle me-2 text-danger' :
					 type === 'warning' ? 'fas fa-exclamation-triangle me-2 text-warning' :
					 'fas fa-info-circle me-2 text-info';
	const bsToast = typeof bootstrap !== 'undefined' ? new bootstrap.Toast(toast) : null;
	bsToast && bsToast.show();
}

// Global error handler
window.addEventListener('error', function(e) {
	if (e && e.error) console.error('JavaScript error:', e.error);
	showToast('An error occurred. Please check the console for details.', 'error');
});

// Helper to fetch JSON with CSRF
function csrfToken() {
	const el = document.querySelector('[name=csrfmiddlewaretoken]');
	return el ? el.value : '';
}

async function fetchJson(url, opts = {}) {
	const headers = Object.assign({'X-CSRFToken': csrfToken()}, opts.headers || {});
	const res = await fetch(url, Object.assign({}, opts, { headers }));
	if (!res.ok) throw new Error('Request failed');
	return res.json();
}

// Initialize Bootstrap components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
	// Wait for Bootstrap to be fully loaded
	setTimeout(function() {
		// Check if Bootstrap is available
		if (typeof bootstrap === 'undefined') {
			console.error('Bootstrap not loaded');
			return;
		}
		
		// Initialize all dropdowns with explicit configuration
		const dropdownElements = document.querySelectorAll('[data-bs-toggle="dropdown"]');
		console.log('Found dropdown elements:', dropdownElements.length);
		
		dropdownElements.forEach(function(element, index) {
			try {
				const dropdown = new bootstrap.Dropdown(element, {
					autoClose: true,
					boundary: 'viewport'
				});
				console.log('Initialized dropdown', index + 1);
			} catch (error) {
				console.error('Error initializing dropdown:', error);
			}
		});
		
		// Initialize all tooltips
		const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
		tooltipElements.forEach(function(element) {
			try {
				new bootstrap.Tooltip(element);
			} catch (error) {
				console.error('Error initializing tooltip:', error);
			}
		});
		
		// Initialize all modals
		const modalElements = document.querySelectorAll('.modal');
		modalElements.forEach(function(element) {
			try {
				new bootstrap.Modal(element);
			} catch (error) {
				console.error('Error initializing modal:', error);
			}
		});
		
		console.log('Bootstrap components initialized successfully');
	}, 100); // Small delay to ensure Bootstrap is loaded
});

// Filter calls function for Live Calls dropdown
function filterCalls(status) {
	try {
		// If on dispatcher dashboard, filter the calls
		if (window.location.pathname.includes('dashboard')) {
			const callCards = document.querySelectorAll('.call-card');
			callCards.forEach(card => {
				const cardStatus = card.dataset.status;
				if (status === 'active' && ['DISPATCHED', 'EN_ROUTE', 'ON_SCENE', 'TRANSPORTING'].includes(cardStatus)) {
					card.style.display = 'block';
				} else if (status === 'pending' && cardStatus === 'RECEIVED') {
					card.style.display = 'block';
				} else if (status === 'completed' && ['AT_HOSPITAL', 'CLOSED'].includes(cardStatus)) {
					card.style.display = 'block';
				} else {
					card.style.display = 'none';
				}
			});
			showToast(`Filtered calls: ${status}`, 'info');
		} else {
			// Redirect to dashboard with filter
			window.location.href = `/dashboard/?filter=${status}`;
		}
	} catch (error) {
		console.error('Error filtering calls:', error);
		showToast('Error filtering calls', 'error');
	}
}

// Show new emergency modal
function showNewEmergencyModal() {
	try {
		// Check if modal exists, if not create it
		let modal = document.getElementById('newEmergencyModal');
		if (!modal) {
			createNewEmergencyModal();
			modal = document.getElementById('newEmergencyModal');
		}
		
		const bsModal = new bootstrap.Modal(modal);
		bsModal.show();
	} catch (error) {
		console.error('Error showing new emergency modal:', error);
		// Fallback: redirect to emergency form
		window.location.href = '/emergency/';
	}
}

// Create new emergency modal dynamically
function createNewEmergencyModal() {
	const modalHTML = `
		<div class="modal fade" id="newEmergencyModal" tabindex="-1">
			<div class="modal-dialog modal-lg">
				<div class="modal-content">
					<div class="modal-header">
						<h5 class="modal-title">Create New Emergency Call</h5>
						<button type="button" class="btn-close" data-bs-dismiss="modal"></button>
					</div>
					<div class="modal-body">
						<form id="newEmergencyForm">
							<div class="row">
								<div class="col-md-6">
									<div class="mb-3">
										<label class="form-label">Caller Name</label>
										<input type="text" class="form-control" name="caller_name" required>
									</div>
									<div class="mb-3">
										<label class="form-label">Phone Number</label>
										<input type="tel" class="form-control" name="caller_phone" required>
									</div>
									<div class="mb-3">
										<label class="form-label">Emergency Type</label>
										<select class="form-control" name="emergency_type" required>
											<option value="">Select Type</option>
											<option value="MEDICAL">Medical Emergency</option>
											<option value="TRAUMA">Trauma</option>
											<option value="CARDIAC">Cardiac Arrest</option>
											<option value="STROKE">Stroke</option>
											<option value="RESPIRATORY">Respiratory Distress</option>
											<option value="FIRE">Fire Emergency</option>
											<option value="OTHER">Other</option>
										</select>
									</div>
								</div>
								<div class="col-md-6">
									<div class="mb-3">
										<label class="form-label">Location Address</label>
										<textarea class="form-control" name="location_address" rows="2" required></textarea>
									</div>
									<div class="mb-3">
										<label class="form-label">Description</label>
										<textarea class="form-control" name="description" rows="4" required></textarea>
									</div>
								</div>
							</div>
						</form>
					</div>
					<div class="modal-footer">
						<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
						<button type="button" class="btn btn-danger" onclick="submitNewEmergency()">Create Emergency Call</button>
					</div>
				</div>
			</div>
		</div>
	`;
	
	document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// Submit new emergency call
async function submitNewEmergency() {
	try {
		const form = document.getElementById('newEmergencyForm');
		const formData = new FormData(form);
		
		const response = await fetch('/api/emergencies/', {
			method: 'POST',
			headers: {
				'X-CSRFToken': csrfToken(),
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(Object.fromEntries(formData))
		});
		
		if (response.ok) {
			const data = await response.json();
			showToast(`Emergency call ${data.call_id} created successfully`, 'success');
			
			// Close modal
			const modal = bootstrap.Modal.getInstance(document.getElementById('newEmergencyModal'));
			modal.hide();
			
			// Refresh page or update dashboard
			if (window.location.pathname.includes('dashboard')) {
				location.reload();
			}
		} else {
			throw new Error('Failed to create emergency call');
		}
	} catch (error) {
		console.error('Error creating emergency call:', error);
		showToast('Error creating emergency call', 'error');
	}
}

