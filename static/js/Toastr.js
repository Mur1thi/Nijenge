document.addEventListener("DOMContentLoaded", function () {
  // Fetch and display initial flash messages (if any)
  const flashMessage = getFlashMessageFromCookie();
  if (flashMessage) {
    toastr.success(flashMessage);
    clearFlashMessageCookie(); // Clear the cookie immediately after displaying the message
  } else {
    console.log("No flash message found in cookie.");
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
