document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const activitySearch = document.getElementById("activity-search");
  const scheduleFilter = document.getElementById("schedule-filter");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const SEARCH_DEBOUNCE_MS = 300;
  let activityRequest = 0;

  function populateScheduleOptions(activities) {
    [...new Set(Object.values(activities).map(({ schedule }) => schedule))]
      .sort()
      .forEach((schedule) => {
        const option = document.createElement("option");
        option.value = schedule;
        option.textContent = schedule;
        scheduleFilter.appendChild(option);
      });
  }

  function displayActivities(activities) {
    // Clear loading message
    activitiesList.innerHTML = "";
    activitySelect
      .querySelectorAll('option:not([value=""])')
      .forEach((option) => option.remove());

    // Populate activities list
    Object.entries(activities).forEach(([name, details]) => {
      const activityCard = document.createElement("div");
      activityCard.className = "activity-card";

      const spotsLeft = details.max_participants - details.participants.length;

      const title = document.createElement("h4");
      title.textContent = name;
      activityCard.appendChild(title);

      const description = document.createElement("p");
      description.textContent = details.description;
      activityCard.appendChild(description);

      [["Schedule:", details.schedule], ["Availability:", `${spotsLeft} spots left`]]
        .forEach(([label, value]) => {
          const detail = document.createElement("p");
          const heading = document.createElement("strong");
          heading.textContent = `${label} `;
          detail.append(heading, value);
          activityCard.appendChild(detail);
        });

      activitiesList.appendChild(activityCard);

      // Add option to select dropdown
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      activitySelect.appendChild(option);
    });
  }

  function showActivityLoadError(error) {
    activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
    console.error("Error fetching activities:", error);
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const query = new URLSearchParams();
      if (activitySearch.value) query.set("search", activitySearch.value);
      if (scheduleFilter.value) query.set("schedule", scheduleFilter.value);
      const request = ++activityRequest;
      const response = await fetch(`/activities?${query}`);
      const activities = await response.json();
      if (request === activityRequest) displayActivities(activities);
    } catch (error) {
      showActivityLoadError(error);
    }
  }

  async function initializeActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      populateScheduleOptions(activities);
      if (activitySearch.value || scheduleFilter.value) {
        fetchActivities();
      } else {
        displayActivities(activities);
      }
    } catch (error) {
      showActivityLoadError(error);
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
        messageDiv.className = "success";
        signupForm.reset();
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

  let searchTimeout;
  activitySearch.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(fetchActivities, SEARCH_DEBOUNCE_MS);
  });
  scheduleFilter.addEventListener("change", fetchActivities);

  // Initialize app
  initializeActivities();
});
