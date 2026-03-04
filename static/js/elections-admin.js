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
        html += `
          <div class="admin-category-header">
            <h3 class="admin-category-title">${category.name}</h3>
            <button class="elections-btn elections-btn-admin admin-reset-btn"
                    data-slug="${category.slug}" data-name="${category.name}">
              Reset votes
            </button>
          </div>`;

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

// ── CSV Interpreter ───────────────────────────────────────────────────────────

$("#csv-parse-btn").on("click", function () {
  $("#csv-error").hide();
  $("#csv-results").hide().empty();

  const raw = $("#csv-input").val().trim();
  if (!raw) {
    $("#csv-error").text("Paste a CSV first.").show();
    return;
  }

  const lines = raw.split("\n").map((l) => l.trim()).filter(Boolean);
  if (lines.length < 2) {
    $("#csv-error").text("CSV must have a header row and at least one data row.").show();
    return;
  }

  const header = lines[0].split(",").map((h) => h.trim());
  const idx = {
    category_slug:  header.indexOf("category_slug"),
    position_title: header.indexOf("position_title"),
    rank:           header.indexOf("rank"),
    points:         header.indexOf("points"),
    candidate_name: header.indexOf("candidate_name"),
  };

  const missing = Object.entries(idx).filter(([, v]) => v === -1).map(([k]) => k);
  if (missing.length) {
    $("#csv-error").text(`Missing columns: ${missing.join(", ")}`).show();
    return;
  }

  // { category_slug: { position_title: { candidate_name: {points, r1, r2, r3} } } }
  const agg = {};

  for (let i = 1; i < lines.length; i++) {
    const cols = lines[i].split(",");
    const slug = (cols[idx.category_slug]  || "").trim();
    const pos  = (cols[idx.position_title] || "").trim();
    const name = (cols[idx.candidate_name] || "").trim();
    const rank = parseInt(cols[idx.rank],   10);
    const pts  = parseInt(cols[idx.points], 10);

    if (!slug || !pos || !name || isNaN(rank) || isNaN(pts)) continue;

    if (!agg[slug]) agg[slug] = {};
    if (!agg[slug][pos]) agg[slug][pos] = {};
    if (!agg[slug][pos][name]) agg[slug][pos][name] = { points: 0, r1: 0, r2: 0, r3: 0 };

    agg[slug][pos][name].points += pts;
    if (rank === 1) agg[slug][pos][name].r1++;
    else if (rank === 2) agg[slug][pos][name].r2++;
    else if (rank === 3) agg[slug][pos][name].r3++;
  }

  if (!Object.keys(agg).length) {
    $("#csv-error").text("No valid rows found in CSV.").show();
    return;
  }

  let html = "";
  for (const [slug, positions] of Object.entries(agg)) {
    html += `<div class="admin-category-block">`;
    html += `<div class="admin-category-header"><h3 class="admin-category-title">${slug}</h3></div>`;

    for (const [pos, candidates] of Object.entries(positions)) {
      const rows = Object.entries(candidates)
        .map(([name, d]) => ({ name, ...d }))
        .sort((a, b) => b.points - a.points);

      html += `<div class="admin-position-block">
        <h4 class="admin-position-title">${pos}</h4>
        <table class="admin-results-table">
          <thead><tr><th>Candidate</th><th>Points</th><th>1st</th><th>2nd</th><th>3rd</th></tr></thead>
          <tbody>`;
      rows.forEach((r, i) => {
        const leader = i === 0 && r.points > 0 ? "admin-results-leader" : "";
        html += `<tr class="${leader}">
          <td>${r.name}</td><td><strong>${r.points}</strong></td>
          <td>${r.r1}</td><td>${r.r2}</td><td>${r.r3}</td>
        </tr>`;
      });
      html += `</tbody></table></div>`;
    }
    html += `</div>`;
  }

  $("#csv-results").html(html).show();
});

$(document).on("click", ".admin-reset-btn", function () {
  const slug = $(this).data("slug");
  const name = $(this).data("name");
  const $btn = $(this);

  if (!confirm(`Reset all votes for "${name}"? A CSV dump will be saved first.`)) return;

  $btn.prop("disabled", true).text("Resetting…");

  $.ajax({
    url: `/api/elections/votes/reset/${slug}`,
    method: "POST",
    success: function (data) {
      alert(`Done. ${data.count} vote(s) dumped to ${data.filename} and removed.`);
      loadResults();
    },
    error: function (xhr) {
      alert((xhr.responseJSON && xhr.responseJSON.error) || "Reset failed.");
      $btn.prop("disabled", false).text("Reset votes");
    },
  });
});
