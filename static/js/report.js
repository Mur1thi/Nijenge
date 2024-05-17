document.addEventListener("DOMContentLoaded", function () {
  const rowsPerPage = 10;
  let currentPage = 1;
  let contributions = [];

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
    fetch(`/report/${fundraiserId}?format=json`)
      .then((response) => {
        if (!response.ok) {
          throw new Error(
            `Network response was not ok: ${response.statusText}`
          );
        }
        return response.json();
      })
      .then((data) => {
        contributions = data.items;
        updateContributionsTable();
      })
      .catch((error) => console.error("Error:", error));
  }

  function updateContributionsTable() {
    const tableBody = document.querySelector("#contributions-table-body");
    tableBody.innerHTML = ""; // Clear the table body

    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const pageContributions = contributions.slice(start, end);

    pageContributions.forEach((contribution) => {
      const row = tableBody.insertRow();
      row.insertCell().textContent = contribution.reference;
      row.insertCell().textContent = contribution.name;
      row.insertCell().textContent = contribution.amount;
      row.insertCell().textContent = contribution.date;
      row.insertCell().textContent = contribution.time;
      row.insertCell().textContent = contribution.timestamp;
    });

    updatePaginationControls();
  }

  function updatePaginationControls() {
    const totalPages = Math.ceil(contributions.length / rowsPerPage);
    document.getElementById(
      "page-info"
    ).textContent = `Page ${currentPage} of ${totalPages}`;
    document.getElementById("prev-page").disabled = currentPage === 1;
    document.getElementById("next-page").disabled = currentPage === totalPages;
  }

  document.getElementById("prev-page").addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      updateContributionsTable();
    }
  });

  document.getElementById("next-page").addEventListener("click", () => {
    const totalPages = Math.ceil(contributions.length / rowsPerPage);
    if (currentPage < totalPages) {
      currentPage++;
      updateContributionsTable();
    }
  });
});
