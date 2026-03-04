// ── Toggle ────────────────────────────────────────────────────────────────────

$("#toggle-btn").on("click", function () {
  $("#toggle-error").hide();
  $("#toggle-btn").prop("disabled", true);

  $.ajax({
    url: "/api/elections/settings",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ isOpen: !currentlyOpen }),
    success: function (data) {
      currentlyOpen = data.isOpen;
      const $label = $("#elections-status-label");
      if (currentlyOpen) {
        $label.text("OPEN").removeClass("badge-closed").addClass("badge-open");
        $("#toggle-btn").text("Close Elections");
      } else {
        $label.text("CLOSED").removeClass("badge-open").addClass("badge-closed");
        $("#toggle-btn").text("Open Elections");
      }
    },
    error: function () {
      $("#toggle-error").text("Failed to update election status.").show();
    },
    complete: function () {
      $("#toggle-btn").prop("disabled", false);
    },
  });
});

// ── Results ───────────────────────────────────────────────────────────────────

function loadResults() {
  $.ajax({
    url: "/api/elections/results",
    method: "GET",
    success: function (data) {
      $("#results-loading").hide();

      if (!data.length) {
        $("#results-container").html("<p>No votes recorded yet.</p>").show();
        return;
      }

      let html = "";
      data.forEach(function (category) {
        html += `<div class="admin-category-block">`;
        html += `<h3 class="admin-category-title">${category.name}</h3>`;

        category.positions.forEach(function (position) {
          html += `<div class="admin-position-block">`;
          html += `<h4 class="admin-position-title">${position.title}</h4>`;
          html += `
            <table class="admin-results-table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Points</th>
                  <th>1st</th>
                  <th>2nd</th>
                  <th>3rd</th>
                </tr>
              </thead>
              <tbody>
          `;
          position.candidates.forEach(function (c, i) {
            const rowClass = i === 0 && c.points > 0 ? "admin-results-leader" : "";
            html += `
              <tr class="${rowClass}">
                <td>${c.name}</td>
                <td><strong>${c.points}</strong></td>
                <td>${c.rank1}</td>
                <td>${c.rank2}</td>
                <td>${c.rank3}</td>
              </tr>
            `;
          });
          html += `</tbody></table></div>`;
        });

        html += `</div>`;
      });

      $("#results-container").html(html).show();
    },
    error: function () {
      $("#results-loading").text("Failed to load results.");
    },
  });
}

loadResults();
