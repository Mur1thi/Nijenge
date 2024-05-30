/*
 * Start Bootstrap - Scrolling Nav v5.0.6 (https://startbootstrap.com/template/scrolling-nav)
 * Copyright 2013-2023 Start Bootstrap
 * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-scrolling-nav/blob/master/LICENSE)
 */
// Login and Register Modal
document.addEventListener("DOMContentLoaded", (event) => {
  // Get the modals
  var loginModal = document.getElementById("loginModal");
  var registerModal = document.getElementById("registerModal");

  // Get the buttons that open the modals
  var loginBtn = document.getElementById("login-btn");
  var registerBtn = document.getElementById("register-btn");

  // Get the <span> elements that close the modals
  var loginSpan = document.getElementsByClassName("close")[0];
  var registerSpan = document.getElementsByClassName("register-close")[0];

  // When the user clicks the button, open the login modal
  loginBtn.onclick = function () {
    loginModal.style.display = "block";
  };

  // When the user clicks on <span> (x), close the login modal
  loginSpan.onclick = function () {
    loginModal.style.display = "none";
  };

  // When the user clicks the button, open the register modal
  registerBtn.onclick = function () {
    registerModal.style.display = "block";
  };

  // When the user clicks on <span> (x), close the register modal
  registerSpan.onclick = function () {
    registerModal.style.display = "none";
  };

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function (event) {
    if (event.target == loginModal) {
      loginModal.style.display = "none";
    } else if (event.target == registerModal) {
      registerModal.style.display = "none";
    }
  };

  // Check if the URL contains the login_error parameter
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has("login_error")) {
    loginModal.style.display = "block";
  }
  // Check if the URL contains the register_error parameter
  if (urlParams.has("register_error")) {
    registerModal.style.display = "block";
    toastr.error("An error occurred during registration");
  }
});

// contact form
// Add an event listener to the form
document.addEventListener("DOMContentLoaded", function () {
  var contactForm = document.getElementById("contactForm");

  contactForm.addEventListener("submit", function (e) {
    e.preventDefault();

    var form = e.target;
    var formData = new FormData(form);
    console.log("Form data:", formData);

    // Show a loading spinner or animation
    var loadingSpinner = document.createElement("div");
    loadingSpinner.classList.add("loading-spinner");
    loadingSpinner.innerHTML =
      '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><span>Sending email...</span>';
    form.appendChild(loadingSpinner);

    fetch("/contact", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("AJAX Success:", data);
        if (data.status === "success") {
          toastr.success(data.message);
          form.reset(); // Clear the form fields
          loadingSpinner.remove(); // Remove the loading spinner
        } else {
          var errors = data.message.split("\n");
          errors.forEach(function (error) {
            toastr.error(error);
          });
          loadingSpinner.remove(); // Remove the loading spinner
        }
      })
      .catch((error) => {
        console.log("AJAX Error:", error);
        toastr.error("An error occurred during form submission");
        loadingSpinner.remove(); // Remove the loading spinner
      });
  });
});

// Fundraiser_success
// Add an event listener to the form
$(document).ready(function () {
  $("#update-button").click(function (event) {
    event.preventDefault(); // Prevent the form from submitting normally

    var message = $("#message").val();
    var fundraiserId = $("#fundraiserId").val();

    $.ajax({
      type: "POST",
      url: "/fundraiser_success/" + fundraiserId,
      data: {
        message: message,
      },
      success: function (response) {
        if (response.status === "success") {
          toastr.success(response.message);
          // Update Funds Raised
          $("#funds-raised").text(
            response.data.funds_raised.toLocaleString("en-US", {
              style: "currency",
              currency: "KES",
            })
          );
          // Clear the message input field
          $("#message").val("");
          // Refresh the page
          window.location.reload();
        } else {
          toastr.error(response.message);
        }
      },
      error: function (xhr, status, error) {
        toastr.error("An error occurred during form submission");
      },
    });
  });
});
