document.addEventListener('DOMContentLoaded', function () {
  const updateButton = document.getElementById('update-button');
  const messageInput = document.getElementById('message');
  const fundraiserIdInput = document.getElementById('fundraiserId');

  updateButton.addEventListener('click', function (event) {
    event.preventDefault();  // Prevent the form from submitting normally

    const message = messageInput.value;
    const fundraiserId = fundraiserIdInput.value;

    saveContribution(fundraiserId, message);
  });

  function saveContribution(fundraiserId, message) {
    $.post('/fundraiser_success/' + fundraiserId, {
      message: message
    })
    .done(function(response) {
      if (response.status === 'success') {
        toastr.success(response.message);
      } else {
        toastr.error(response.message);
      }
    })
    .fail(function(xhr, status, error) {
      toastr.error('Error saving contribution');
    });
  }
});
