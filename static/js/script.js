
updateStats();
setInterval(updateStats, 500);

async function updateStats() {
  try {
    const response = await fetch("/detection_stats");
    const data = await response.json();

    document.getElementById("totalCount").textContent = data.total;
    // Display class breakdown
    const classList = document.getElementById("classList");
    classList.innerHTML = "";

    if (Object.keys(data.classes).length > 0) {
      const header = document.createElement("div");
      header.innerHTML = "<strong>Detected Objects:</strong>";
      header.style.marginTop = "10px";
      classList.appendChild(header);

      for (const [className, count] of Object.entries(data.classes)) {
        const item = document.createElement("div");
        item.className = "class-item";
        item.innerHTML = `<span>${className}</span><span><strong>${count}</strong></span>`;
        classList.appendChild(item);
      }
    }
  } catch (error) {
    console.error("Error fetching detection stats:", error);
  }
}