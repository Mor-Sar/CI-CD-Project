// static/app.js

// משתמשים ב-relative URLs כי ה-frontend וה-backend רצים מאותו origin
const API_BASE = "";

// state קטן
let selectedTopicId = null;
let currentCards = [];

// Helper: fetch JSON
async function fetchJSON(path, options = {}) {
    const res = await fetch(API_BASE + path, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    let data = null;
    try {
        data = await res.json();
    } catch {
        data = null;
    }

    // אם קיבלנו 401 (לא מחובר) – נעביר לדף login (אבל לא בקריאות ל־auth)
    if (
        res.status === 401 &&
        !path.startsWith("/auth/") &&
        window.location.pathname !== "/login"
    ) {
        window.location.href = "/login";
    }

    return { status: res.status, data };
}

// Toast קטן
let toastTimeout = null;
function showToast(message, type = "info") {
    const toast = document.getElementById("toast");
    if (!toast) return; // במקרה שאין toast בעמוד (login/register)

    toast.textContent = message;
    toast.classList.remove("hidden", "visible");
    toast.style.background =
        type === "error" ? "#7f1d1d" : type === "success" ? "#14532d" : "#111827";

    // Force reflow so animation can restart
    void toast.offsetWidth;
    toast.classList.add("visible");

    if (toastTimeout) clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        toast.classList.remove("visible");
        toastTimeout = null;
    }, 3000);
}

// Backend health check
async function checkHealth() {
    const badge = document.getElementById("healthStatus");
    if (!badge) return; // למשל בעמוד login אין את האלמנט הזה

    badge.textContent = "Checking backend...";
    badge.className = "badge badge-gray";

    try {
        const { status, data } = await fetchJSON("/health");
        if (status === 200 && data && data.status === "ok") {
            badge.textContent = "Backend: OK";
            badge.className = "badge badge-green";
        } else {
            badge.textContent = `Backend error (${status})`;
            badge.className = "badge badge-red";
        }
    } catch (err) {
        badge.textContent = "Backend unreachable";
        badge.className = "badge badge-red";
    }
}

// Load topics
async function loadTopics() {
    const listEl = document.getElementById("topicsList");
    if (!listEl) return; // בעמודים בלי sidebar

    listEl.innerHTML = "<li>Loading...</li>";

    const { status, data } = await fetchJSON("/topics");
    if (status !== 200 || !Array.isArray(data)) {
        listEl.innerHTML = `<li>Error loading topics (${status})</li>`;
        return;
    }

    if (data.length === 0) {
        listEl.innerHTML = "<li>No topics yet. Create one above.</li>";
        return;
    }

    listEl.innerHTML = "";
    data.forEach((topic) => {
        const li = document.createElement("li");
        li.dataset.id = topic.id;
        li.className = topic.id === selectedTopicId ? "active" : "";

        const nameEl = document.createElement("span");
        nameEl.className = "topic-name";
        nameEl.textContent = topic.name;

        const metaEl = document.createElement("span");
        metaEl.className = "topic-meta";
        metaEl.textContent = `#${topic.id}`;

        li.appendChild(nameEl);
        li.appendChild(metaEl);

        li.onclick = () => {
            selectedTopicId = topic.id;
            updateTopicsSelection();
            loadCardsForTopic(topic.id);
        };

        listEl.appendChild(li);
    });
}

function updateTopicsSelection() {
    const listEl = document.getElementById("topicsList");
    if (!listEl) return;

    Array.from(listEl.children).forEach((li) => {
        const id = parseInt(li.dataset.id, 10);
        li.classList.toggle("active", id === selectedTopicId);
    });

    const titleEl = document.getElementById("cardsTitle");
    if (!titleEl) return;

    if (selectedTopicId) {
        titleEl.textContent = `Cards for Topic #${selectedTopicId}`;
    } else {
        titleEl.textContent = "Cards";
    }
}

// Load cards for a given topic
async function loadCardsForTopic(topicId) {
    const container = document.getElementById("cardsContainer");
    if (!container) return;

    container.innerHTML = "<p class='placeholder'>Loading cards...</p>";

    const filterSelect = document.getElementById("cardTypeFilter");
    const typeFilter = filterSelect ? filterSelect.value : "";
    let url = `/topics/${topicId}/cards`;
    if (typeFilter) {
        url += `?type=${encodeURIComponent(typeFilter)}`;
    }

    const { status, data } = await fetchJSON(url);

    if (status !== 200 || !Array.isArray(data)) {
        container.innerHTML = `<p class='placeholder'>Error loading cards (${status})</p>`;
        return;
    }

    currentCards = data;
    renderCards();
}

function renderCards() {
    const container = document.getElementById("cardsContainer");
    if (!container) return;

    container.innerHTML = "";

    if (!currentCards.length) {
        container.innerHTML =
            "<p class='placeholder'>No cards for this topic (or filter hides them).</p>";
        return;
    }

    currentCards.forEach((card) => {
        const cardEl = document.createElement("div");
        cardEl.className = "card";
        cardEl.dataset.id = card.id;

        // Header
        const header = document.createElement("div");
        header.className = "card-header";

        const left = document.createElement("div");
        const typePill = document.createElement("span");
        typePill.className = "card-type-pill";
        typePill.textContent = card.card_type;

        left.appendChild(typePill);

        const right = document.createElement("div");
        right.className = "card-meta";
        right.textContent = `ID: ${card.id} · Topic: ${card.topic_id}`;

        header.appendChild(left);
        header.appendChild(right);

        // Content
        const contentEl = document.createElement("pre");
        contentEl.className = "card-content";
        contentEl.textContent = card.content;

        // Actions: edit + delete
        const actions = document.createElement("div");
        actions.className = "card-actions";

        const editBtn = document.createElement("button");
        editBtn.className = "btn ghost small";
        editBtn.textContent = "Edit";
        editBtn.onclick = () => enterEditMode(cardEl, card);

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "btn ghost small";
        deleteBtn.textContent = "Delete";
        deleteBtn.onclick = () => deleteCard(card.id);

        actions.appendChild(editBtn);
        actions.appendChild(deleteBtn);

        cardEl.appendChild(header);
        cardEl.appendChild(contentEl);
        cardEl.appendChild(actions);

        container.appendChild(cardEl);
    });
}

// Edit mode for card
function enterEditMode(cardEl, card) {
    const pre = cardEl.querySelector(".card-content");
    const actions = cardEl.querySelector(".card-actions");

    // מחליפים pre ב-textarea
    const textarea = document.createElement("textarea");
    textarea.value = card.content;

    cardEl.replaceChild(textarea, pre);

    // Actions חדשים
    const saveBtn = document.createElement("button");
    saveBtn.className = "btn primary small";
    saveBtn.textContent = "Save";
    saveBtn.onclick = async () => {
        await saveCardChanges(card.id, textarea.value, card.card_type);
    };

    const cancelBtn = document.createElement("button");
    cancelBtn.className = "btn ghost small";
    cancelBtn.textContent = "Cancel";
    cancelBtn.onclick = () => {
        // לחזור לתצוגה רגילה
        const newPre = document.createElement("pre");
        newPre.className = "card-content";
        newPre.textContent = card.content;
        cardEl.replaceChild(newPre, textarea);
        renderCards(); // תרנדר הכל מחדש מה-state
    };

    actions.innerHTML = "";
    actions.appendChild(saveBtn);
    actions.appendChild(cancelBtn);
}

// Save card changes
async function saveCardChanges(cardId, newContent, cardType) {
    const payload = {
        content: newContent,
        card_type: cardType,
    };

    const { status, data } = await fetchJSON(`/cards/${cardId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
    });

    if (status === 200) {
        showToast("Card updated", "success");
        // לעדכן את ה-state המקומי
        const idx = currentCards.findIndex((c) => c.id === cardId);
        if (idx !== -1) {
            currentCards[idx] = data;
        }
        renderCards();
    } else {
        showToast(`Error updating card (${status})`, "error");
    }
}

// Delete card
async function deleteCard(cardId) {
    if (!confirm(`Delete card #${cardId}?`)) return;

    const { status } = await fetchJSON(`/cards/${cardId}`, {
        method: "DELETE",
    });

    if (status === 200) {
        showToast("Card deleted", "success");
        currentCards = currentCards.filter((c) => c.id !== cardId);
        renderCards();
    } else {
        showToast(`Error deleting card (${status})`, "error");
    }
}

// Create topic + cards
async function createTopicAndCards() {
    const topicInput = document.getElementById("topicInput");
    const statusEl = document.getElementById("createStatus");
    const createBtn = document.getElementById("createBtn");

    if (!topicInput || !statusEl || !createBtn) return;

    const topic = topicInput.value.trim();
    if (!topic) {
        statusEl.textContent = "Please enter a topic name.";
        return;
    }

    const formats = Array.from(
        document.querySelectorAll(".format-checkbox:checked")
    ).map((el) => el.value);

    if (!formats.length) {
        statusEl.textContent = "Please choose at least one format.";
        return;
    }

    const modeRadio = document.querySelector('input[name="mode"]:checked');
    const mode = modeRadio ? modeRadio.value : "dummy";

    statusEl.textContent = "Creating topic and cards...";
    createBtn.disabled = true;

    const { status, data } = await fetchJSON("/topics", {
        method: "POST",
        body: JSON.stringify({ topic, formats, mode }),
    });

    createBtn.disabled = false;

    if (status === 201) {
        statusEl.textContent = `Created topic "${data.topic.name}" with ${data.cards.length} cards.`;
        topicInput.value = "";
        showToast("Topic created", "success");
        await loadTopics();
    } else {
        const msg = data && data.error ? data.error : "Unknown error";
        statusEl.textContent = `Error (${status}): ${msg}`;
        showToast(`Error creating topic (${status})`, "error");
    }
}

// Global summaries
async function loadGlobalSummaries() {
    selectedTopicId = null;
    updateTopicsSelection();
    const titleEl = document.getElementById("cardsTitle");
    if (titleEl) {
        titleEl.textContent = "Global Summaries";
    }

    const container = document.getElementById("cardsContainer");
    if (!container) return;

    container.innerHTML = "<p class='placeholder'>Loading summaries...</p>";

    const { status, data } = await fetchJSON("/cards?type=summary");

    if (status !== 200 || !Array.isArray(data)) {
        container.innerHTML = `<p class='placeholder'>Error loading summaries (${status})</p>`;
        return;
    }

    currentCards = data;
    renderCards();
}

document.addEventListener("DOMContentLoaded", () => {
    const createBtn = document.getElementById("createBtn");
    const reloadBtn = document.getElementById("reloadTopicsBtn");
    const globalBtn = document.getElementById("globalSummariesBtn");
    const typeFilter = document.getElementById("cardTypeFilter");
    const logoutBtn = document.getElementById("logoutBtn");

    if (createBtn) {
        createBtn.onclick = createTopicAndCards;
    }
    if (reloadBtn) {
        reloadBtn.onclick = loadTopics;
    }
    if (globalBtn) {
        globalBtn.onclick = loadGlobalSummaries;
    }
    if (typeFilter) {
        typeFilter.onchange = () => {
            if (selectedTopicId) {
                loadCardsForTopic(selectedTopicId);
            } else {
                renderCards();
            }
        };
    }
    if (logoutBtn && window.logoutAuth) {
        logoutBtn.onclick = () => window.logoutAuth();
    }

    // לעדכן UI לפי מצב התחברות
    if (window.__refreshAuthUI) {
        window.__refreshAuthUI();
    }

    // בדף הראשי בלבד יש topics וכו', לכן נבדוק
    if (document.getElementById("topicsList")) {
        checkHealth();
        loadTopics();
    }
});


// === Simple Auth layer: login, logout, and auto-attaching JWT to fetch ===
(function () {
  const originalFetch = window.fetch.bind(window);

  let authToken = localStorage.getItem("authToken") || null;
  let currentUser = null;
  try {
    currentUser = JSON.parse(localStorage.getItem("currentUser") || "null");
  } catch {
    currentUser = null;
  }

  function updateAuthUI() {
    const label = document.getElementById("userInfoLabel");
    const loginLink = document.getElementById("loginLink");
    const logoutBtn = document.getElementById("logoutBtn");

    if (!label || !loginLink || !logoutBtn) return;

    if (currentUser) {
      const name = currentUser.username || currentUser.email || "User";
      label.textContent = `Logged in as ${name}`;
      logoutBtn.style.display = "inline-block";
      loginLink.style.display = "none";
    } else {
      label.textContent = "Not logged in";
      logoutBtn.style.display = "none";
      loginLink.style.display = "inline-block";
    }
  }

  function setAuth(data) {
    if (data && data.token) {
      authToken = data.token;
      currentUser = data.user || null;

      localStorage.setItem("authToken", authToken);
      localStorage.setItem("currentUser", JSON.stringify(currentUser));
      console.log("✅ Logged in as:", currentUser?.username || currentUser?.email);
    } else {
      authToken = null;
      currentUser = null;
      localStorage.removeItem("authToken");
      localStorage.removeItem("currentUser");
      console.log("ℹ️ Logged out");
    }
    updateAuthUI();
  }

  // עיטוף ל-fetch – מוסיף Authorization אוטומטית
  window.fetch = function (input, init = {}) {
    const options = { ...(init || {}) };

    options.headers = options.headers instanceof Headers
      ? options.headers
      : new Headers(options.headers || {});

    if (authToken && typeof input === "string" && input.startsWith("/")) {
      options.headers.set("Authorization", "Bearer " + authToken);
    }

    return originalFetch(input, options);
  };

  // פונקציה גלובלית – נשתמש בה בדף ה-login אם נרצה
  window.loginWithEmailPassword = async function (email, password) {
    const res = await originalFetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const errText = await res.text();
      console.error("❌ Login failed:", res.status, errText);
      throw new Error("Login failed");
    }

    const data = await res.json();
    setAuth(data);
    return data;
  };

  // Logout גלובלי
  window.logoutAuth = function () {
    setAuth(null);
    // נחזיר לדף ה-login
    window.location.href = "/login";
  };

  // פונקציה גלובלית לקריאת המשתמש
  window.getCurrentUser = function () {
    return currentUser;
  };

  // נחשוף גם את עדכון ה-UI כדי שנוכל לקרוא בו ב-DOMContentLoaded
  window.__refreshAuthUI = updateAuthUI;

  console.log("🔐 Auth layer loaded.");
})();
