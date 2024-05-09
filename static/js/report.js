window.addEventListener("DOMContentLoaded", () => {
  let currentPageNumber = 1; // Start on page 1

  function fetchContributionsData() {
    fetch(`/report/${fundraiserId}/page/${currentPageNumber}`)
      .then((response) => response.json())
      .then((data) => {
        renderFundraiserInfo(data.fundraiser);
        updateContributionsTable(data.items);
        updatePaginationLinks(data.has_prev, data.has_next, data.prev_num, data.next_num);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }

  function renderFundraiserInfo(fundraiser) {
    const fundraiserCard = document.querySelector(".card-body");
    fundraiserCard.innerHTML = `
      <h4 class="card-title">${fundraiser.name}</h4>
      <p class="card-text">${fundraiser.description}</p>
      <p class="text-muted">
        End Date: ${new Date(fundraiser.end_date).toLocaleDateString("en-US", {
          month: "long",
          day: "numeric",
          year: "numeric",
        })}<br>
        Target Funds: ${new Intl.NumberFormat("en-KE", {
          style: "currency",
          currency: "KES",
        }).format(fundraiser.target_funds)}<br>
        Funds Raised: ${new Intl.NumberFormat("en-KE", {
          style: "currency",
          currency: "KES",
        }).format(fundraiser.funds_raised)}
      </p>
    `;
  }

  function updateContributionsTable(contributions) {
    const tableBody = document.querySelector("#contributions-table-body");
    tableBody.innerHTML = ""; // Clear the table

    // Add a new row for each contribution
    contributions.forEach((contribution) => {
      const row = document.createElement("tr");

      const referenceCell = document.createElement("td");
      referenceCell.textContent = contribution.contribution_reference;
      row.appendChild(referenceCell);

      const contributorCell = document.createElement("td");
      contributorCell.textContent = contribution.contributor_name;
      row.appendChild(contributorCell);

      const amountCell = document.createElement("td");
      amountCell.textContent = new Intl.NumberFormat("en-KE", {
        style: "currency",
        currency: "KES",
      }).format(contribution.amount);
      row.appendChild(amountCell);

      const dateCell = document.createElement("td");
      dateCell.textContent = new Date(contribution.contribution_date).toLocaleDateString();
      row.appendChild(dateCell);

      const timeCell = document.createElement("td");
      timeCell.textContent = new Date(contribution.contribution_time).toLocaleTimeString([], {
        hour12: true,
        hour: "2-digit",
        minute: "2-digit",
      });
      row.appendChild(timeCell);

      const timestampCell = document.createElement("td");
      timestampCell.textContent = contribution.timestamp;
      row.appendChild(timestampCell);

      tableBody.appendChild(row);
    });
  }

  function updateContributionsTable(contributions) {
    const tableBody = document.querySelector("#contributions-table-body");
    tableBody.innerHTML = ""; // Clear the table

    // Add a new row for each contribution
    for (const contribution of contributions) {
      const row = document.createElement("tr");

      const referenceCell = document.createElement("td");
      referenceCell.textContent = contribution.contribution_reference;
      row.appendChild(referenceCell);

      const contributorCell = document.createElement("td");
      contributorCell.textContent = contribution.contributor_name;
      row.appendChild(contributorCell);

      const amountCell = document.createElement("td");
      amountCell.textContent = contribution.amount;
      row.appendChild(amountCell);

      const dateCell = document.createElement("td");
      dateCell.textContent = contribution.contribution_date;
      row.appendChild(dateCell);

      const timeCell = document.createElement("td");
      timeCell.textContent = contribution.contribution_time;
      row.appendChild(timeCell);

      const timestampCell = document.createElement("td");
      timestampCell.textContent = contribution.timestamp;
      row.appendChild(timestampCell);

      tableBody.appendChild(row);
    }
  }

  function updatePaginationLinks(hasPrev, hasNext, prevNum, nextNum) {
    const pagination = document.querySelector("#pagination");
    pagination.innerHTML = ""; // Clear the pagination links

    if (hasPrev) {
      const prevLink = document.createElement("a");
      prevLink.textContent = "Previous";
      prevLink.onclick = () => {
        currentPageNumber = prevNum;
        fetchContributionsData();
      };
      pagination.appendChild(prevLink);
    }

    if (hasNext) {
      const nextLink = document.createElement("a");
      nextLink.textContent = "Next";
      nextLink.onclick = () => {
        currentPageNumber = nextNum;
        fetchContributionsData();
      };
      pagination.appendChild(nextLink);
    }
  }

  // Fetch the initial data
  fetchContributionsData();
});
