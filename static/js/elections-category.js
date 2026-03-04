// rankings[positionTitle] = { candidateId: rank }
const rankings = {};

let studentId = null;

// ── Verify ────────────────────────────────────────────────────────────────────

$("#verify-btn").on("click", function () {
  const id = $("#student-id-input").val().trim();
  if (!id) return;

  $("#verify-btn").prop("disabled", true).text("Verifying…");
  $("#verify-error").hide();

  $.ajax({
    url: "/api/elections/verify",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ student_id: id, category_slug: CATEGORY_SLUG }),
    success: function (data) {
      if (data.valid) {
        studentId = id;
        if (data.alreadyVoted) {
          $("#verify-section").hide();
          $("#already-voted-section").show();
        } else {
          $("#voter-name").text(data.name);
          $("#verify-section").hide();
          $("#voting-section").show();
        }
      } else {
        showVerifyError(data.error || "Verification failed");
      }
    },
    error: function () {
      showVerifyError("Something went wrong. Please try again.");
    },
    complete: function () {
      $("#verify-btn").prop("disabled", false).text("Verify");
    },
  });
});

$("#student-id-input").on("keydown", function (e) {
  if (e.key === "Enter") $("#verify-btn").click();
});

function showVerifyError(msg) {
  $("#verify-error").text(msg).show();
}

// ── Ranking logic ─────────────────────────────────────────────────────────────

$(document).on("click", ".candidate-card", function () {
  const $card = $(this);
  const positionTitle = $card.closest(".position-block").data("position");
  const candidateId = $card.data("candidate-id");

  if (!rankings[positionTitle]) rankings[positionTitle] = {};

  const current = rankings[positionTitle][candidateId];

  if (current) {
    // Deselect
    delete rankings[positionTitle][candidateId];
  } else {
    // Assign next free rank (1 → 2 → 3)
    const usedRanks = Object.values(rankings[positionTitle]);
    const nextRank = [1, 2, 3].find((r) => !usedRanks.includes(r));
    if (!nextRank) return; // All 3 slots full — ignore click
    rankings[positionTitle][candidateId] = nextRank;
  }

  updatePositionDisplay(positionTitle);
});

function updatePositionDisplay(positionTitle) {
  const $block = $(`.position-block[data-position="${CSS.escape(positionTitle)}"]`);
  const posRankings = rankings[positionTitle] || {};

  // Update rank slots
  $block.find(".rank-slot").each(function () {
    const rank = parseInt($(this).data("rank"));
    const candidateId = Object.keys(posRankings).find(
      (id) => posRankings[id] === rank
    );
    if (candidateId) {
      const name = $block
        .find(`.candidate-card[data-candidate-id="${candidateId}"]`)
        .data("candidate-name");
      $(this).find(".rank-slot-name").text(name);
      $(this).addClass("rank-slot-filled");
    } else {
      $(this).find(".rank-slot-name").text("—");
      $(this).removeClass("rank-slot-filled");
    }
  });

  // Update candidate cards
  $block.find(".candidate-card").each(function () {
    const id = $(this).data("candidate-id").toString();
    const rank = posRankings[id];
    const $badge = $(this).find(".candidate-rank-badge");
    if (rank) {
      const labels = { 1: "1st", 2: "2nd", 3: "3rd" };
      $badge.text(labels[rank]).show();
      $(this).addClass("candidate-ranked");
    } else {
      $badge.hide();
      $(this).removeClass("candidate-ranked");
    }
  });
}

// Allow clicking a filled rank slot to clear that rank
$(document).on("click", ".rank-slot.rank-slot-filled", function (e) {
  e.stopPropagation();
  const rank = parseInt($(this).data("rank"));
  const positionTitle = $(this).closest(".position-block").data("position");
  const posRankings = rankings[positionTitle] || {};
  const candidateId = Object.keys(posRankings).find(
    (id) => posRankings[id] === rank
  );
  if (candidateId) {
    delete rankings[positionTitle][candidateId];
    updatePositionDisplay(positionTitle);
  }
});

// ── Submit ────────────────────────────────────────────────────────────────────

$("#submit-btn").on("click", function () {
  $("#submit-error").hide();

  const votes = [];
  for (const candRanks of Object.values(rankings)) {
    for (const [candId, rank] of Object.entries(candRanks)) {
      votes.push({ candidate_id: parseInt(candId), rank: rank });
    }
  }

  if (votes.length === 0) {
    $("#submit-error").text("Please rank at least one candidate before submitting.").show();
    return;
  }

  $("#submit-btn").prop("disabled", true).text("Submitting…");

  $.ajax({
    url: "/api/elections/vote",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      student_id: studentId,
      category_slug: CATEGORY_SLUG,
      votes: votes,
    }),
    success: function () {
      $("#voting-section").hide();
      $("#confirmation-section").show();
    },
    error: function (xhr) {
      const msg =
        (xhr.responseJSON && xhr.responseJSON.error) ||
        "Submission failed. Please try again.";
      $("#submit-error").text(msg).show();
      $("#submit-btn").prop("disabled", false).text("Submit Votes");
    },
  });
});
