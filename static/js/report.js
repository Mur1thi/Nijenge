document.addEventListener("DOMContentLoaded", function () {
  fetchReportData(getFundraiserId());

  function getFundraiserId() {
    const fundraiserIdElement = document.getElementById("fundraiser-id");
    if (fundraiserIdElement) {
      const fundraiserId = fundraiserIdElement.value;
      if (fundraiserId) {
        return fundraiserId;
      } else {
        console.error("Fundraiser ID is empty or invalid");
      }
    } else {
      console.error("Fundraiser ID element not found!");
    }
    return null;
  }
  // Fetch report data from the server
  function fetchReportData(fundraiserId) {
    fetch(`/report/${fundraiserId}`) 
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            `Network response was not ok: ${response.statusText}`
          );
        }
        return response.json();
      })
      .then((data) => {
        updateContributionsTable(data.items);
      })
      .catch((error) => console.error("Error:", error));
  }

  function updateContributionsTable(contributions) {
    const tableBody = document.querySelector("#contributions-table-body");
    tableBody.innerHTML = ""; // Clear the table body

    contributions.forEach((contribution) => {
      const row = tableBody.insertRow();

      // Create and append cells for each column (replace with your actual data)
      row.insertCell().textContent = contribution.contribution_reference;
      row.insertCell().textContent = contribution.contributor_name;
      row.insertCell().textContent = contribution.amount;
      row.insertCell().textContent = contribution.date;
      row.insertCell().textContent = contribution.time;
      row.insertCell().textContent = contribution.timestamp;
    });
  }
});
