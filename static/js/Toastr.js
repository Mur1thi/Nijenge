document.addEventListener("DOMContentLoaded", function () {
  // Fetch and display initial flash messages (if any)
  const flashMessage = getFlashMessageFromCookie();
  if (flashMessage) {
    toastr.success(flashMessage);
    clearFlashMessageCookie(); // Clear the cookie immediately after displaying the message
  } else {
    console.log("No flash message found in cookie.");
  }

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

  function clearFlashMessageCookie() {
    document.cookie =
      "flash_message=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
  }

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

  // Fetch flash messages from the server
  fetch("/messages")
    .then((response) => response.json())
    .then((data) => {
      const messages = data.messages;
      messages.forEach(function (message) {
        const category = message[0];
        const text = message[1];
        toastr[category](text);
      });
    })
    .catch((error) => console.error("Error fetching messages:", error));
});
