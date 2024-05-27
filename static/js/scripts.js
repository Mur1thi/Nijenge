/*
* Start Bootstrap - Scrolling Nav v5.0.6 (https://startbootstrap.com/template/scrolling-nav)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-scrolling-nav/blob/master/LICENSE)
*/
//
// Scripts
//
document.addEventListener("DOMContentLoaded", (event) => {
  // Get the modal
  var modal = document.getElementById("loginModal");

  // Get the button that opens the modal
  var btn = document.getElementById("login-btn");

  // Get the <span> element that closes the modal
  var span = document.getElementsByClassName("close")[0];

  // When the user clicks the button, open the modal
  btn.onclick = function () {
    modal.style.display = "block";
  };

  // When the user clicks on <span> (x), close the modal
  span.onclick = function () {
    modal.style.display = "none";
  };

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function (event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };
});

window.addEventListener('DOMContentLoaded', event => {

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            rootMargin: '0px 0px -40%',
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

});

document.addEventListener('DOMContentLoaded', function() {
    var contactForm = document.getElementById('contactForm');

    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();

        var form = e.target;
        var formData = new FormData(form);
        console.log('Form data:', formData);

        // Show a loading spinner or animation
        var loadingSpinner = document.createElement('div');
        loadingSpinner.classList.add('loading-spinner');
        loadingSpinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><span>Sending email...</span>';
        form.appendChild(loadingSpinner);

        fetch('/contact', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('AJAX Success:', data);
            if (data.status === 'success') {
                toastr.success(data.message);
                form.reset(); // Clear the form fields
                loadingSpinner.remove(); // Remove the loading spinner
            } else {
                var errors = data.message.split('\n');
                errors.forEach(function(error) {
                    toastr.error(error);
                });
                loadingSpinner.remove(); // Remove the loading spinner
            }
        })
        .catch(error => {
            console.log('AJAX Error:', error);
            toastr.error('An error occurred during form submission');
            loadingSpinner.remove(); // Remove the loading spinner
        });
    });
});

    $(document).ready(function() {
    $('#update-button').click(function(event) {
        event.preventDefault(); // Prevent the form from submitting normally

        var message = $('#message').val();
        var fundraiserId = $('#fundraiserId').val();

        $.ajax({
            type: 'POST',
            url: '/fundraiser_success/' + fundraiserId,
            data: {
                message: message
            },
            success: function(response) {
                if (response.status === 'success') {
                    toastr.success(response.message);
                    // Update Funds Raised
                    $('#funds-raised').text(
                        response.data.funds_raised.toLocaleString('en-US', { 
                            style: 'currency', currency: 'KES' 
                        })
                    ); 
                    // Clear the message input field
                    $('#message').val('');
                    // Refresh the page
                    window.location.reload();
                } else {
                    toastr.error(response.message);
                }
            },
            error: function(xhr, status, error) {
                toastr.error('An error occurred during form submission');
            }
        });
    });
});