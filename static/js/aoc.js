$(function () {
    loadLeaderboard();
});

function loadLeaderboard() {
    $.ajax({
        url: '/api/aoc/leaderboard',
        method: 'GET',
        success: function(data) {
            displayLeaderboard(data);
        },
        error: function(xhr, status, error) {
            showError();
            console.error('Error loading leaderboard:', error);
        }
    });
}

function displayLeaderboard(data) {
    // Hide loading state
    $('#loadingState').hide();

    // Parse members into array and sort by local_score
    const members = Object.values(data.members);
    members.sort((a, b) => b.local_score - a.local_score);

    // Calculate statistics
    const totalMembers = members.length;
    const totalStars = members.reduce((sum, member) => sum + member.stars, 0);
    const daysActive = calculateActiveDays(data);

    // Update stats
    $('#totalMembers').text(totalMembers);
    $('#totalStars').text(totalStars);
    $('#daysActive').text(daysActive + ' / ' + data.num_days);

    // Generate leaderboard table
    const tbody = $('#leaderboardBody');
    tbody.empty();

    members.forEach((member, index) => {
        const rank = index + 1;
        const name = member.name || 'Anonymous User #' + member.id;
        const stars = member.stars;
        const score = member.local_score;

        // Determine rank class for top 3
        let rankClass = '';
        let rowClass = '';
        if (rank === 1) {
            rankClass = 'first';
            rowClass = 'top-3';
        } else if (rank === 2) {
            rankClass = 'second';
            rowClass = 'top-3';
        } else if (rank === 3) {
            rankClass = 'third';
            rowClass = 'top-3';
        }

        const row = `
            <tr class="${rowClass}">
                <td class="rank ${rankClass}">${rank}</td>
                <td class="member-name">${escapeHtml(name)}</td>
                <td class="stars">${stars}</td>
                <td class="score">${score}</td>
            </tr>
        `;

        tbody.append(row);
    });

    // Show table
    $('#leaderboardTable').show();

    // Update last updated time
    const now = new Date();
    $('#lastUpdated').text('Last updated: ' + now.toLocaleString());
}

function calculateActiveDays(data) {
    // Count how many different days have been completed by at least one member
    const completedDays = new Set();

    Object.values(data.members).forEach(member => {
        if (member.completion_day_level) {
            Object.keys(member.completion_day_level).forEach(day => {
                completedDays.add(parseInt(day));
            });
        }
    });

    return completedDays.size;
}

function showError() {
    $('#loadingState').hide();
    $('#errorState').show();
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}
