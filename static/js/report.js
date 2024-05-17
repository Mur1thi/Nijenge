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

  // Event listener for the download button
  document
    .getElementById("download-pdf")
    .addEventListener("click", generatePDF);

  // Generate PDF
  function generatePDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Add Nijenge and Fundraiser details
    doc.setFont("Times");
    doc.setFontSize(14);
    doc.text("Nijenge", 20, 20);
    doc.text(`Fundraiser: ${fundraiser.name}`, 20, 30);
    doc.text(`Description: ${fundraiser.description}`, 20, 40);
    doc.text(`End Date: ${fundraiser.end_date}`, 20, 50);
    doc.text(`Target Funds: ${fundraiser.target_funds}`, 20, 60);
    doc.text(`Funds Raised: ${fundraiser.funds_raised}`, 20, 70);

    // Add some space before the table
    doc.text("", 20, 80);

    // Add contributions table
    doc.autoTable({
      startY: 90,
      head: [["Reference", "Name", "Amount", "Date", "Time", "Timestamp"]],
      body: contributions.map((contribution) => [
        contribution.reference,
        contribution.name,
        contribution.amount,
        contribution.date,
        contribution.time,
        contribution.timestamp,
      ]),
      margin: { top: 10 },
    });

    // Save the PDF
    doc.save(`Fundraiser_Report_${fundraiser.name}.pdf`);
  }
});
