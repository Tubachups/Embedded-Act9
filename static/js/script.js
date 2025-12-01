updateStats();
setInterval(updateStats, 500);

// Configure alert triggers
const alertRules = {
  objectThreshold: 5,
  watchedClasses: ['person', 'car', 'dog'],
  motionAlert: true,
  voiceEnabled: true  // Enable/disable voice announcements
};

let lastMotionState = false;
let lastAnnouncedClasses = {};
let speechSynthesis = window.speechSynthesis;

// Voice announcement function
function speak(message) {
  if (!alertRules.voiceEnabled || !speechSynthesis) return;
  
  // Cancel any ongoing speech
  speechSynthesis.cancel();
  
  const utterance = new SpeechSynthesisUtterance(message);
  utterance.rate = 1.0;    // Speed (0.1 to 10)
  utterance.pitch = 1.0;   // Pitch (0 to 2)
  utterance.volume = 1.0;  // Volume (0 to 1)
  utterance.lang = 'en-US';
  
  speechSynthesis.speak(utterance);
}

// Announce detected objects
function announceDetections(data) {
  if (!alertRules.voiceEnabled) return;
  
  const classes = data.classes;
  const newDetections = [];
  
  for (const [className, count] of Object.entries(classes)) {
    // Only announce if it's a new detection or count increased
    if (!lastAnnouncedClasses[className] || lastAnnouncedClasses[className] < count) {
      newDetections.push(`${count} ${className}${count > 1 ? 's' : ''}`);
    }
  }
  
  if (newDetections.length > 0) {
    speak(`Detected: ${newDetections.join(', ')}`);
  }
  
  // Update last announced
  lastAnnouncedClasses = { ...classes };
}

function showAlert(message, type = 'info') {
  const container = document.getElementById('alertContainer');
  const alert = document.createElement('div');
  alert.className = `alert alert-${type}`;
  alert.textContent = message;
  container.appendChild(alert);
  
  setTimeout(() => alert.remove(), 5000);
  playAlertSound(type);
}

function playAlertSound(type) {
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const oscillator = audioCtx.createOscillator();
  const gainNode = audioCtx.createGain();
  
  oscillator.connect(gainNode);
  gainNode.connect(audioCtx.destination);
  
  oscillator.frequency.value = type === 'danger' ? 800 : 400;
  oscillator.type = 'sine';
  gainNode.gain.value = 0.1;
  
  oscillator.start();
  setTimeout(() => oscillator.stop(), 200);
}

async function updateStats() {
  try {
    const response = await fetch("/detection_stats");
    const data = await response.json();

    document.getElementById("totalCount").textContent = data.total;
    
    checkAlerts(data);
    
    // Announce detections via voice
    announceDetections(data);
    
    const motionElem = document.getElementById("motionStatus");
    const classList = document.getElementById("classList");
    classList.innerHTML = "";

    if (data.motion_detected) {
      motionElem.textContent = "Motion Detected";
      motionElem.className = "status-badge status-active";
    } else {
      motionElem.textContent = "No Motion";
      motionElem.className = "status-badge status-inactive";
    }

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

function checkAlerts(data) {
  if (alertRules.motionAlert && data.motion_detected && !lastMotionState) {
    // showAlert('⚠️ Motion Detected!', 'warning');
    speak('Motion detected!');
  }
  lastMotionState = data.motion_detected;
  
  if (data.total > alertRules.objectThreshold) {
    showAlert(`🚨 High object count: ${data.total}`, 'danger');
  }
  
  for (const [className, count] of Object.entries(data.classes)) {
    if (alertRules.watchedClasses.includes(className.toLowerCase())) {
      // showAlert(`👁️ ${className} detected (${count})`, 'info');
    }
  }
}