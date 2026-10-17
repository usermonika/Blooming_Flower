document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("productModal");

  // Handle star rating functionality
  modal.addEventListener("shown.bs.modal", function () {
    const stars = modal.querySelectorAll(".star-rating .star");
    const ratingInput = modal.querySelector("#rating-input");

    if (!stars || !ratingInput) return;

    stars.forEach((star) => {
      star.addEventListener("click", function () {
        const rating = parseInt(this.getAttribute("data-value"));
        ratingInput.value = rating;

        stars.forEach((s) => {
          s.classList.remove("zmdi-star");
          s.classList.add("zmdi-star-outline");
        });

        stars.forEach((s) => {
          if (parseInt(s.getAttribute("data-value")) <= rating) {
            s.classList.remove("zmdi-star-outline");
            s.classList.add("zmdi-star");
          }
        });
      });
    });
  });

  // Handle modal close events
  modal.addEventListener("hidden.bs.modal", function () {
    // Go back to previous page when modal is closed
    if (window.history.length > 1) {
      window.history.back();
    } else {
      // If no history, redirect to products page
      window.location.href = "{% url 'product_list' %}";
    }
  });

  // Handle close button click
  const closeButtons = modal.querySelectorAll('[data-bs-dismiss="modal"]');
  closeButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const modalInstance = bootstrap.Modal.getInstance(modal);
      if (modalInstance) {
        modalInstance.hide();
      }
    });
  });

  // Handle backdrop click (clicking outside modal)
  modal.addEventListener('click', function(e) {
    if (e.target === modal) {
      const modalInstance = bootstrap.Modal.getInstance(modal);
      if (modalInstance) {
        modalInstance.hide();
      }
    }
  });

  // Handle ESC key press
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      const modalInstance = bootstrap.Modal.getInstance(modal);
      if (modalInstance) {
        modalInstance.hide();
      }
    }
  });

  // Handle modal form submission for "Add to Cart"
  const modalCartForm = modal.querySelector('form.cart');
  if (modalCartForm) {
    modalCartForm.addEventListener('submit', function(e) {
      // Let the form submit normally (POST request)
      // The backend will handle the redirect
      console.log('Modal add to cart form submitted');
    });
  }

  // Make entire product card clickable to open modal
  document.addEventListener('click', function(e) {
    // Find the closest product card
    const productCard = e.target.closest('.single-product');
    
    if (productCard) {
      // Check if the click was on an action button or link that should not trigger modal
      const isActionElement = e.target.closest('.product-action') || 
                              e.target.closest('button') || 
                              e.target.closest('.cart-plus-minus') ||
                              e.target.closest('.wishlist-toggle') ||
                              e.target.closest('[data-add-to-cart]') ||
                              e.target.closest('a[data-add-to-cart]');
      
      if (isActionElement) {
        // For add to cart buttons, prevent modal from opening
        if (e.target.closest('[data-add-to-cart]') || e.target.closest('a[data-add-to-cart]')) {
          e.stopPropagation();
        }
        return; // Don't open modal for action elements
      }

      // Check if clicked on a quick view link or image link
      const clickedLink = e.target.closest('a');
      if (clickedLink) {
        const href = clickedLink.getAttribute('href');
        const hasModalTarget = clickedLink.getAttribute('data-bs-target') === '#productModal';
        
        // If it's a quick view link with modal target, let it work naturally
        if (hasModalTarget && href) {
          e.preventDefault();
          e.stopPropagation();
          loadProductModal(href);
          return;
        }
        
        // If it's a product detail link, convert to modal
        if (href && (href.includes('product_detail') || href.includes('product/'))) {
          e.preventDefault();
          e.stopPropagation();
          
          const productId = extractProductIdFromUrl(href);
          if (productId) {
            loadProductModalById(productId);
          }
          return;
        }
      }

      // Try to get product ID from data attribute
      const productIdFromData = productCard.getAttribute('data-product-id');
      if (productIdFromData) {
        e.preventDefault();
        e.stopPropagation();
        loadProductModalById(productIdFromData);
        return;
      }

      // Fallback: look for any quick view link in the card
      const quickViewLink = productCard.querySelector('a[href*="quickview"]') || 
                           productCard.querySelector('a[data-bs-target="#productModal"]');
      
      if (quickViewLink) {
        e.preventDefault();
        e.stopPropagation();
        const href = quickViewLink.getAttribute('href');
        if (href) {
          loadProductModal(href);
        }
        return;
      }

      // Final fallback: look for any product link
      const productLink = productCard.querySelector('a[href*="product"]') || 
                         productCard.querySelector('.product-img a') ||
                         productCard.querySelector('.post-title a');
      
      if (productLink) {
        const href = productLink.getAttribute('href');
        if (href) {
          e.preventDefault();
          e.stopPropagation();
          
          const productId = extractProductIdFromUrl(href);
          if (productId) {
            loadProductModalById(productId);
          }
        }
      }
    }
  });

  // // Function to extract product ID from URL
  // function extractProductIdFromUrl(url) {
  //   // Match patterns like /product/123/, /product_detail/123/, or /product/quickview/123/
  //   const match = url.match(/\/product(?:\/quickview|_detail)?\/(\d+)\/?/);
  //   return match ? match[1] : null;
  // }

  // // Function to load product modal by ID
  // function loadProductModalById(productId) {
  //   // Construct the quick view URL using the correct pattern
  //   const quickViewUrl = `/product/quickview/${productId}/`;
  //   loadProductModal(quickViewUrl);
  // }

  // Function to load product modal content
  function loadProductModal(url) {
    console.log('Loading product modal from URL:', url);
    
    fetch(url)
      .then(response => {
        console.log('Response status:', response.status);
        return response.text();
      })
      .then(html => {
        console.log('Received HTML, length:', html.length);
        
        // Create a temporary div to parse the response
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        
        // Look for product_detail data in the response
        const productDetailScript = tempDiv.querySelector('script:contains("product_detail")');
        console.log('Found product detail script:', !!productDetailScript);
        
        // Try to extract modal content from the response
        const modalBody = tempDiv.querySelector('#productModal .modal-body');
        const quickviewWrapper = tempDiv.querySelector('#quickview-wrapper');
        
        console.log('Found modal body:', !!modalBody);
        console.log('Found quickview wrapper:', !!quickviewWrapper);
        
        if (modalBody) {
          // Update the existing modal body with new content
          const existingModalBody = modal.querySelector('.modal-body');
          if (existingModalBody) {
            existingModalBody.innerHTML = modalBody.innerHTML;
            console.log('Updated modal body with new content');
          }
        } else if (quickviewWrapper) {
          // Update the entire modal content
          const existingModalContent = modal.querySelector('.modal-content');
          const newModalContent = quickviewWrapper.querySelector('.modal-content');
          if (existingModalContent && newModalContent) {
            existingModalContent.innerHTML = newModalContent.innerHTML;
            console.log('Updated modal content from quickview wrapper');
          }
        } else {
          // Fallback: Build modal content from available data
          console.log('No modal content found, building from scratch');
          buildModalFromResponse(tempDiv);
        }
        
        // Show the modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Update URL without page reload
        if (history.pushState) {
          history.pushState(null, null, url);
        }
        
        // Re-initialize modal functionality for the new content
        initializeModalContent();
      })
      .catch(error => {
        console.error('Error loading product modal:', error);
        // Fallback: navigate to the URL
        window.location.href = url;
      });
  }

  // Function to build modal content from response data
  function buildModalFromResponse(tempDiv) {
    // Try to extract product data from the page
    const productName = tempDiv.querySelector('h1, h2, .product-title, .post-title a, .product-info h2');
    const productImage = tempDiv.querySelector('.product-img img, .product-image img, .product-images img');
    const productPrice = tempDiv.querySelector('.pro-price, .price, .new-price, .pro-price-2');
    const productDescription = tempDiv.querySelector('.description, .product-description, p');
    
    console.log('Extracted data:', {
      name: productName ? productName.textContent : 'Not found',
      image: productImage ? productImage.src : 'Not found',
      price: productPrice ? productPrice.textContent : 'Not found'
    });
    
    if (productName || productImage || productPrice) {
      const modalBody = modal.querySelector('.modal-body');
      if (modalBody) {
        modalBody.innerHTML = `
          <div class="row">
            <div class="col-md-5 text-center">
              <div class="product-images">
                ${productImage ? `<img src="${productImage.src}" alt="${productImage.alt || 'Product'}" class="img-fluid" style="width: 100%; max-width: 350px; height: 450px; object-fit: cover;" />` : '<p>No image available</p>'}
              </div>
            </div>
            <div class="col-md-7">
              <div class="product-info">
                <h2>${productName ? (productName.textContent || productName.innerText) : 'Product'}</h2>
                <div class="price-box-3">
                  <hr />
                  <div class="s-price-box">
                    <span class="new-price fw-bold text-success fs-5">${productPrice ? (productPrice.textContent || productPrice.innerText) : 'Price not available'}</span>
                  </div>
                  <hr />
                </div>
                <div class="quick-desc mb-3">
                  <h6>Description:</h6>
                  <p>${productDescription ? (productDescription.textContent || productDescription.innerText) : 'Product details will be loaded shortly...'}</p>
                </div>
                <div class="quick-add-to-cart mb-3">
                  <label class="quantity-label">Quantity:</label>
                  <div class="input-group">
                    <input type="number" name="quantity" value="1" min="1" max="99" class="form-control" />
                    <button class="btn btn-primary" type="button">
                      <i class="zmdi zmdi-shopping-cart-plus me-2"></i>Add to Cart
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `;
        console.log('Built enhanced modal content from extracted data');
      }
    } else {
      const modalBody = modal.querySelector('.modal-body');
      if (modalBody) {
        modalBody.innerHTML = '<p>Product details are being loaded. Please try again.</p>';
      }
      console.log('No product data found in response, showing fallback message');
    }
  }

  // Function to initialize modal content (star ratings, form handlers, etc.)
  function initializeModalContent() {
    // Re-initialize star rating functionality
    const stars = modal.querySelectorAll(".star-rating .star");
    const ratingInput = modal.querySelector("#rating-input");

    if (stars && ratingInput) {
      stars.forEach((star) => {
        star.addEventListener("click", function () {
          const rating = parseInt(this.getAttribute("data-value"));
          ratingInput.value = rating;

          stars.forEach((s) => {
            s.classList.remove("zmdi-star");
            s.classList.add("zmdi-star-outline");
          });

          stars.forEach((s) => {
            if (parseInt(s.getAttribute("data-value")) <= rating) {
              s.classList.remove("zmdi-star-outline");
              s.classList.add("zmdi-star");
            }
          });
        });
      });
    }

    // Re-initialize form submission handlers
    const modalCartForm = modal.querySelector('form.cart');
    if (modalCartForm) {
      modalCartForm.addEventListener('submit', function(e) {
        console.log('Modal add to cart form submitted');
      });
    }
  }
});