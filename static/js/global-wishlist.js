document.addEventListener('DOMContentLoaded', function() {
			// Initialize wishlist toggle functionality
			initWishlistToggle();
			
			// Re-initialize after AJAX content loads
			document.addEventListener('contentLoaded', function() {
				initWishlistToggle();
			});
		});

		function initWishlistToggle() {
			document.querySelectorAll('.wishlist-toggle').forEach(el => {
				// Remove existing event listeners to prevent duplicates
				el.removeEventListener('click', handleWishlistToggle);
				el.addEventListener('click', handleWishlistToggle);
			});
		}

		function handleWishlistToggle(e) {
			e.preventDefault();
			e.stopPropagation();
			
			const icon = this.querySelector('i');
			const productId = this.dataset.productId;
			
			if (!icon || !productId) return;
			
			// Add loading state
			const originalClass = icon.className;
			icon.className = 'zmdi zmdi-refresh zmdi-hc-spin';
			this.style.pointerEvents = 'none';
			
			fetch(`/add-to-wishlist/${productId}/`, {
				method: 'POST',
				headers: {
					'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '{{ csrf_token }}',
					'X-Requested-With': 'XMLHttpRequest',
				},
			})
			.then(res => res.json())
			.then(data => {
				if (data.status === 'added') {
					icon.className = 'zmdi zmdi-favorite';
					icon.style.color = '#e74c3c';
					showNotification('Added to wishlist!', 'success');
				} else if (data.status === 'removed') {
					icon.className = 'zmdi zmdi-favorite-outline';
					icon.style.color = '';
					showNotification('Removed from wishlist!', 'info');
				}
				
				// Update wishlist count if element exists
				const wishlistCount = document.querySelector('.wishlist-count');
				if (wishlistCount && data.wishlist_count !== undefined) {
					wishlistCount.textContent = data.wishlist_count;
				}
				
				// Trigger custom event for other components to listen
				document.dispatchEvent(new CustomEvent('wishlistUpdated', {
					detail: { productId, status: data.status, count: data.wishlist_count }
				}));
			})
			.catch(error => {
				console.error('Error:', error);
				icon.className = originalClass;
				showNotification('Failed to update wishlist. Please try again.', 'error');
			})
			.finally(() => {
				this.style.pointerEvents = '';
			});
		}

		// Enhanced notification function that works with existing alert system
		function showNotification(message, type = 'info') {
			// Try to use existing alert system first
			if (typeof showAlert === 'function') {
				showAlert(message, type);
				return;
			}
			
			// Fallback to custom toast
			const existingToast = document.querySelector('.toast-notification');
			if (existingToast) {
				existingToast.remove();
			}

			const toast = document.createElement('div');
			toast.className = `toast-notification toast-${type}`;
			toast.style.cssText = `
				position: fixed;
				top: 20px;
				right: 20px;
				background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : '#3498db'};
				color: white;
				padding: 15px 20px;
				border-radius: 5px;
				z-index: 10000;
				box-shadow: 0 4px 12px rgba(0,0,0,0.15);
				transform: translateX(300px);
				transition: transform 0.3s ease;
				font-weight: 500;
			`;
			toast.textContent = message;
			
			document.body.appendChild(toast);
			
			// Animate in
			setTimeout(() => {
				toast.style.transform = 'translateX(0)';
			}, 10);
			
			// Remove after 3 seconds
			setTimeout(() => {
				toast.style.transform = 'translateX(300px)';
				setTimeout(() => {
					if (toast.parentNode) {
						toast.parentNode.removeChild(toast);
					}
				}, 300);
			}, 3000);
		}
		
