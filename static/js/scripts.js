
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
  if (loginBtn) {
    loginBtn.onclick = function () {
      loginModal.style.display = "block";
    };

    // When the user clicks on <span> (x), close the login modal
    loginSpan.onclick = function () {
      loginModal.style.display = "none";
    };
  }

  // When the user clicks the button, open the register modal
  if (registerBtn) {
    registerBtn.onclick = function () {
      registerModal.style.display = "block";
    };

    // When the user clicks on <span> (x), close the register modal
    registerSpan.onclick = function () {
      registerModal.style.display = "none";
      // Clear the form fields
      document.getElementById("registerForm").reset();
    };
  }

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

  // Settings dropdown actions
  const toggleDarkModeBtn = document.getElementById("toggleDarkMode");
  const deleteFundraiserBtn = document.getElementById("deleteFundraiser");

  // Toggle dark mode
  if (toggleDarkModeBtn) {
    toggleDarkModeBtn.onclick = function () {
      const themeToggle = document.getElementById("theme-toggle");
      if (themeToggle) {
        themeToggle.checked = !themeToggle.checked;
        themeToggle.dispatchEvent(new Event("change"));
      }
    };
  }

  // Delete fundraiser
  if (deleteFundraiserBtn) {
    deleteFundraiserBtn.onclick = function () {
      if (confirm("Are you sure you want to end and delete your fundraiser?")) {
        fetch("/delete_fundraiser", {
          method: "POST",
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.status === "success") {
              toastr.success(data.message);
              window.location.href = "/";
            } else {
              toastr.error(data.message);
            }
          })
          .catch((error) => {
            toastr.error("An error occurred: " + error);
          });
      }
    };
  }
});

// Function to save contributions and handle flash messages
function saveContribution(fundraiserId, message) {
  console.log("Fundraiser ID:", fundraiserId);
  console.log("Message:", message);

  if (!fundraiserId || !message) {
    toastr.error("Fundraiser ID or message is missing");
    return;
  }

  $.ajax({
    type: "POST",
    url: "/fundraiser_success/" + fundraiserId,
    data: { message: message },
    success: function (response) {
      if (response.status === "success") {
        // Set a cookie with the flash message
        document.cookie = `flash_message=${response.message}; path=/`;
        toastr.success(response.message); // Display the notification
        // Clear the textarea and optionally update the contributions table
        const messageInput = document.getElementById("message");
        if (messageInput) {
          messageInput.value = "";
        }
        // Clear the cookie after setting it
        clearFlashMessageCookie();
      } else {
        toastr.error(response.message);
      }
    },
    error: function (xhr, status, error) {
      toastr.error("Error saving contribution: " + error);
    },
  });
}

// Example usage of saveContribution
const updateButton = document.getElementById("update-button");
if (updateButton) {
  updateButton.addEventListener("click", function (event) {
    event.preventDefault();
    const fundraiserIdInput = document.getElementById("fundraiser-id");
    const fundraiserId = fundraiserIdInput ? fundraiserIdInput.value : null;
    const messageInput = document.getElementById("message");
    const message = messageInput ? messageInput.value : null;
    saveContribution(fundraiserId, message);
  });
}

// Function to get the flash message from the cookie
function getFlashMessageFromCookie() {
  const cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    if (cookie.startsWith("flash_message=")) {
      return decodeURIComponent(
        cookie.substring("flash_message=".length, cookie.length)
      );
    }
  }
  return null;
}

// Function to clear the flash message cookie
function clearFlashMessageCookie() {
  document.cookie =
    "flash_message=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

// contact form
// Add an event listener to the form
document.addEventListener("DOMContentLoaded", function () {
  var contactForm = document.getElementById("contactForm");

  if (contactForm) {
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
  }
});
