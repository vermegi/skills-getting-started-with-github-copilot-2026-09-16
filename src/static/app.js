document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const waitlist = details.waitlist || [];
        const renderPeople = (emails, type) =>
          emails
            .map(
              (email) => `
                  <li class="participant-item">
                    <span>${email}</span>
                    <button type="button" class="delete-participant" data-activity="${name}" data-email="${email}" aria-label="Remove ${email} from ${type === "waitlist" ? "the waitlist of" : ""} ${name}">
                      🗑️
                    </button>
                  </li>
                `
            )
            .join("");

        const participantsList = details.participants.length
          ? renderPeople(details.participants, "participants")
          : "<li class=\"participant-empty\">No participants yet</li>";

        const waitlistSection = waitlist.length
          ? `
          <div class="participants waitlist">
            <h5>Waitlist</h5>
            <ul>${renderPeople(waitlist, "waitlist")}</ul>
          </div>
        `
          : "";

        activityCard.innerHTML = `
          <div class="activity-header">
            <h4>${name}</h4>
            <span class="availability-badge${spotsLeft > 0 ? "" : " full"}">${
              spotsLeft > 0
                ? `${spotsLeft} spots left`
                : `Full${waitlist.length ? ` · ${waitlist.length} waitlisted` : ""}`
            }</span>
          </div>
          <p class="activity-description">${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <div class="participants">
            <h5>Participants</h5>
            <ul>${participantsList}</ul>
          </div>
          ${waitlistSection}
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      document.querySelectorAll(".delete-participant").forEach((button) => {
        button.addEventListener("click", async () => {
          const activityName = button.dataset.activity;
          const email = button.dataset.email;

          try {
            const response = await fetch(
              `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
              {
                method: "DELETE",
              }
            );

            const result = await response.json();

            if (!response.ok) {
              throw new Error(result.detail || "Unable to unregister participant");
            }

            messageDiv.textContent = result.message;
            messageDiv.className = "success";
            messageDiv.classList.remove("hidden");
            setTimeout(() => messageDiv.classList.add("hidden"), 5000);

            await fetchActivities();
          } catch (error) {
            messageDiv.textContent = error.message || "Failed to unregister participant.";
            messageDiv.className = "error";
            messageDiv.classList.remove("hidden");
            setTimeout(() => messageDiv.classList.add("hidden"), 5000);
            console.error("Error unregistering participant:", error);
          }
        });
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = result.status === "waitlisted" ? "info" : "success";
        signupForm.reset();
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
