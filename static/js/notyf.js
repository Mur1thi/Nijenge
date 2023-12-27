// Get DOM elements
const messageInput = document.getElementById('message');
// Get reference to button
const updateButton = document.getElementById('update-button');


// Save contribution handler
updateButton.addEventListener('click',
    function () {

      // Get data
      const message = messageInput.value;
      const fundraiserIdInput = document.getElementById('fundraiserId');

      // Call save contribution
      saveContribution(fundraiserId, message);

    });


// Save contribution function
function saveContribution(fundraiserId, message) {

  $.post('/save_contribution/' + fundraiserId, {
    message: message
  })
  .done(function(response) {

    // Check response
    if (response.status === 'success') {

      // Show success notification
      new Notyf({
        type: 'success',
        message: response.message
      }).open();

      // Clear input
      messageInput.value = '';

    } else {
      // Show error notification
      new Notyf({
        type: 'error',
        message: response.message
      }).open();
    }

  })
  .fail(function(xhr, status, error) {

    // Show error notification
    new Notyf({
      type: 'error',
      message: 'Error saving contribution'
    }).open();

  });

}