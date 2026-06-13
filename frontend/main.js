const menuButton = document.getElementById("menu-button");
const mobileNav = document.getElementById("sideBar");
const menuBackdrop = document.getElementById("menu-backdrop");

function setMenuState(isOpen) {
    if (!menuButton || !mobileNav) return;

    menuButton.classList.toggle("is-open", isOpen);
    mobileNav.classList.toggle("is-open", isOpen);
    menuBackdrop?.classList.toggle("is-open", isOpen);
    menuButton.setAttribute("aria-expanded", String(isOpen));
    menuButton.setAttribute("aria-label", isOpen ? "Close navigation menu" : "Open navigation menu");
    mobileNav.setAttribute("aria-hidden", String(!isOpen));
    document.body.classList.toggle("menu-open", isOpen);
}

menuButton?.addEventListener("click", () => {
    setMenuState(menuButton.getAttribute("aria-expanded") !== "true");
});

menuBackdrop?.addEventListener("click", () => setMenuState(false));

mobileNav?.addEventListener("click", (event) => {
    if (event.target === mobileNav) setMenuState(false);
});

mobileNav?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setMenuState(false));
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuButton?.getAttribute("aria-expanded") === "true") {
        setMenuState(false);
        menuButton.focus();
    }
});

const progressButton = document.getElementById("percentage");

function updateScrollProgress() {
    if (!progressButton) return;

    const scrollableHeight = document.documentElement.scrollHeight - window.innerHeight;
    const percentage = scrollableHeight > 0
        ? Math.min(100, Math.round((window.scrollY / scrollableHeight) * 100))
        : 0;

    progressButton.textContent = `${percentage}%`;
}

window.addEventListener("scroll", updateScrollProgress, { passive: true });
window.addEventListener("resize", updateScrollProgress);
progressButton?.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
});
updateScrollProgress();

const animatedElements = document.querySelectorAll(".lazy_box");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if ("IntersectionObserver" in window && !reducedMotion) {
    const observer = new IntersectionObserver((entries, currentObserver) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                currentObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    animatedElements.forEach((element) => observer.observe(element));
} else {
    animatedElements.forEach((element) => element.classList.add("visible"));
}

const scriptURL = "https://script.google.com/macros/s/AKfycbwp-cEadhXFnp-sazapIqnGvG8pmF21cdy6CpwjTqs7GkzlWe6W5Oui1xEBsuJNnPF8/exec";
const form = document.forms["submit-to-google-sheet"];
const submitButton = document.getElementById("submit-button");
const formStatus = document.getElementById("form-status");

form?.addEventListener("submit", async (event) => {
    event.preventDefault();

    submitButton.disabled = true;
    submitButton.textContent = "Sending...";
    formStatus.className = "form-status";
    formStatus.textContent = "Sending your message...";

    try {
        const response = await fetch(scriptURL, {
            method: "POST",
            body: new FormData(form)
        });

        if (!response.ok) {
            throw new Error("Message submission failed");
        }

        form.reset();
        formStatus.classList.add("success");
        formStatus.textContent = "Your message was sent successfully. Thank you.";
    } catch {
        formStatus.classList.add("error");
        formStatus.textContent = "Your message could not be sent. Please try again or use the contact details provided.";
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Send Message";
    }
});

const modal = document.getElementById("myModal");
const profileButton = document.getElementById("profile-button");
const profileImage = document.getElementById("profile-pic");
const modalImage = document.getElementById("modalImage");
const closeModalButton = document.getElementById("closeModal");

function openModal() {
    if (!modal || !profileImage || !modalImage || !closeModalButton) return;

    modalImage.src = profileImage.src;
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("menu-open");
    closeModalButton.focus();
}

function closeModal() {
    if (!modal || !profileButton) return;

    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("menu-open");
    profileButton.focus();
}

profileButton?.addEventListener("click", openModal);
closeModalButton?.addEventListener("click", closeModal);
modal?.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal?.classList.contains("is-open")) {
        closeModal();
    }
});

const currentYear = document.getElementById("currentYear");
if (currentYear) currentYear.textContent = new Date().getFullYear();

const ASSISTANT_API_BASE_URL = "https://personal-assistant-bot-y2ye.onrender.com";
const ASSISTANT_HEALTH_TIMEOUT_MS = 75000;
const ASSISTANT_HEALTH_RETRY_MS = 3000;
const ASSISTANT_HEALTH_REQUEST_TIMEOUT_MS = 10000;
const ASSISTANT_WAKE_MESSAGES = [
    "The assistant is waking up. This may take a moment.",
    "Connecting to the assistant service...",
    "Loading portfolio knowledge and project details...",
    "Almost ready. Thank you for waiting..."
];

const assistantDrawer = document.getElementById("assistant-drawer");
const assistantBackdrop = document.getElementById("assistant-backdrop");
const assistantLauncher = document.getElementById("assistant-launcher");
const assistantClose = document.getElementById("assistant-close");
const assistantMessages = document.getElementById("assistant-messages");
const assistantForm = document.getElementById("assistant-form");
const assistantInput = document.getElementById("assistant-input");
const assistantSend = document.getElementById("assistant-send");
const assistantWakeStatus = document.getElementById("assistant-wake-status");
const assistantWakeTitle = document.getElementById("assistant-wake-title");
const assistantWakeMessage = document.getElementById("assistant-wake-message");
const assistantRetry = document.getElementById("assistant-retry");
let assistantBusy = false;
let assistantHealthState = "idle";
let assistantHealthPromise = null;
let assistantWakeMessageTimer = null;

function setAssistantState(isOpen) {
    if (!assistantDrawer || !assistantBackdrop || !assistantLauncher) return;

    assistantDrawer.classList.toggle("is-open", isOpen);
    assistantBackdrop.classList.toggle("is-open", isOpen);
    assistantDrawer.setAttribute("aria-hidden", String(!isOpen));
    assistantBackdrop.setAttribute("aria-hidden", String(!isOpen));
    assistantLauncher.setAttribute("aria-expanded", String(isOpen));
    document.body.classList.toggle("assistant-open", isOpen);

    if (isOpen) {
        setMenuState(false);
        void ensureAssistantReady();
    } else {
        assistantLauncher.focus();
    }
}

document.querySelectorAll("[data-open-assistant]").forEach((button) => {
    button.addEventListener("click", () => setAssistantState(true));
});

assistantClose?.addEventListener("click", () => setAssistantState(false));
assistantBackdrop?.addEventListener("click", () => setAssistantState(false));
assistantRetry?.addEventListener("click", () => {
    assistantHealthState = "idle";
    void ensureAssistantReady();
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && assistantDrawer?.classList.contains("is-open")) {
        setAssistantState(false);
    }
});

document.querySelectorAll("[data-assistant-question]").forEach((button) => {
    button.addEventListener("click", () => {
        if (!assistantInput) return;
        assistantInput.value = button.dataset.assistantQuestion;
        sendAssistantMessage();
    });
});

assistantInput?.addEventListener("input", () => {
    assistantInput.style.height = "auto";
    assistantInput.style.height = `${Math.min(assistantInput.scrollHeight, 128)}px`;
});

assistantInput?.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendAssistantMessage();
    }
});

assistantForm?.addEventListener("submit", (event) => {
    event.preventDefault();
    sendAssistantMessage();
});

async function sendAssistantMessage() {
    const message = assistantInput?.value.trim();
    if (
        !message
        || assistantBusy
        || assistantHealthState !== "ready"
        || !assistantMessages
    ) return;

    assistantBusy = true;
    assistantSend.disabled = true;
    appendAssistantMessage(message, "user");
    assistantInput.value = "";
    assistantInput.style.height = "auto";
    const typingMessage = appendAssistantTyping();

    try {
        const response = await fetch(`${ASSISTANT_API_BASE_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        const answer = await response.json();
        typingMessage.remove();

        if (!response.ok) {
            throw new Error(answer.response || "The assistant could not answer.");
        }

        appendAssistantMessage(answer.response, "ai");
        renderAssistantSuggestions(answer.suggestions || []);
    } catch (error) {
        typingMessage.remove();
        appendAssistantMessage(
            error.message || "Sorry, I could not reach the assistant. Please try again.",
            "ai"
        );
    } finally {
        assistantBusy = false;
        assistantSend.disabled = false;
        assistantInput.focus();
    }
}

async function ensureAssistantReady() {
    if (assistantHealthState === "ready") {
        setAssistantAvailability(true);
        assistantInput?.focus();
        return true;
    }

    if (assistantHealthPromise) return assistantHealthPromise;

    assistantHealthState = "checking";
    setAssistantAvailability(false);
    showAssistantWakeStatus();
    startAssistantWakeMessages();

    assistantHealthPromise = checkAssistantHealth()
        .then(() => {
            assistantHealthState = "ready";
            stopAssistantWakeMessages();
            hideAssistantWakeStatus();
            setAssistantAvailability(true);
            assistantInput?.focus();
            return true;
        })
        .catch(() => {
            assistantHealthState = "delayed";
            stopAssistantWakeMessages();
            showAssistantDelayedStatus();
            setAssistantAvailability(false);
            return false;
        })
        .finally(() => {
            assistantHealthPromise = null;
        });

    return assistantHealthPromise;
}

async function checkAssistantHealth() {
    const deadline = Date.now() + ASSISTANT_HEALTH_TIMEOUT_MS;

    while (Date.now() < deadline) {
        const controller = new AbortController();
        const requestTimeout = window.setTimeout(
            () => controller.abort(),
            ASSISTANT_HEALTH_REQUEST_TIMEOUT_MS
        );

        try {
            const response = await fetch(`${ASSISTANT_API_BASE_URL}/health`, {
                method: "GET",
                cache: "no-store",
                signal: controller.signal
            });

            if (response.ok) return;
        } catch {
            // Render may reject early requests while a free service is starting.
        } finally {
            window.clearTimeout(requestTimeout);
        }

        const remainingTime = deadline - Date.now();
        if (remainingTime > 0) {
            await waitForAssistantHealthRetry(
                Math.min(ASSISTANT_HEALTH_RETRY_MS, remainingTime)
            );
        }
    }

    throw new Error("Assistant health check timed out");
}

function waitForAssistantHealthRetry(delay) {
    return new Promise((resolve) => window.setTimeout(resolve, delay));
}

function setAssistantAvailability(isAvailable) {
    if (assistantInput) assistantInput.disabled = !isAvailable;
    if (assistantSend) assistantSend.disabled = !isAvailable || assistantBusy;

    document.querySelectorAll("[data-assistant-question]").forEach((button) => {
        button.disabled = !isAvailable;
    });
}

function showAssistantWakeStatus() {
    if (!assistantWakeStatus || !assistantWakeTitle || !assistantWakeMessage) return;

    assistantWakeStatus.hidden = false;
    assistantWakeStatus.classList.remove("is-delayed");
    assistantWakeTitle.textContent = "Starting Ashely JT Assistant...";
    assistantWakeMessage.textContent = ASSISTANT_WAKE_MESSAGES[0];
    if (assistantRetry) assistantRetry.hidden = true;
}

function hideAssistantWakeStatus() {
    if (assistantWakeStatus) assistantWakeStatus.hidden = true;
}

function showAssistantDelayedStatus() {
    if (!assistantWakeStatus || !assistantWakeTitle || !assistantWakeMessage) return;

    assistantWakeStatus.hidden = false;
    assistantWakeStatus.classList.add("is-delayed");
    assistantWakeTitle.textContent = "Still connecting";
    assistantWakeMessage.textContent = "The assistant is taking longer than usual. You can wait a moment or try again.";
    if (assistantRetry) assistantRetry.hidden = false;
}

function startAssistantWakeMessages() {
    stopAssistantWakeMessages();
    let messageIndex = 0;

    assistantWakeMessageTimer = window.setInterval(() => {
        messageIndex = (messageIndex + 1) % ASSISTANT_WAKE_MESSAGES.length;
        if (assistantWakeMessage) {
            assistantWakeMessage.textContent = ASSISTANT_WAKE_MESSAGES[messageIndex];
        }
    }, 3500);
}

function stopAssistantWakeMessages() {
    if (!assistantWakeMessageTimer) return;
    window.clearInterval(assistantWakeMessageTimer);
    assistantWakeMessageTimer = null;
}

function appendAssistantMessage(message, sender) {
    const row = document.createElement("div");
    row.className = `assistant-message assistant-message-${sender}`;

    const avatar = document.createElement("div");
    avatar.className = "assistant-avatar";
    avatar.textContent = sender === "user" ? "You" : "AI";

    const bubble = document.createElement("div");
    bubble.className = "assistant-bubble";
    bubble.innerHTML = sender === "user"
        ? escapeAssistantHtml(message)
        : formatAssistantResponse(message);

    row.appendChild(avatar);
    row.appendChild(bubble);
    assistantMessages.appendChild(row);
    assistantMessages.scrollTop = assistantMessages.scrollHeight;
    return row;
}

function appendAssistantTyping() {
    const row = document.createElement("div");
    row.className = "assistant-message assistant-message-ai";
    row.innerHTML = `
        <div class="assistant-avatar" aria-hidden="true">AI</div>
        <div class="assistant-bubble">
            <div class="assistant-typing" aria-label="Assistant is typing">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    assistantMessages.appendChild(row);
    assistantMessages.scrollTop = assistantMessages.scrollHeight;
    return row;
}

function renderAssistantSuggestions(suggestions) {
    const container = document.getElementById("assistant-suggestions");
    if (!container) return;

    container.innerHTML = "";
    suggestions.slice(0, 3).forEach((suggestion) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = suggestion;
        button.addEventListener("click", () => {
            assistantInput.value = suggestion;
            sendAssistantMessage();
        });
        container.appendChild(button);
    });
}

function formatAssistantResponse(text) {
    const lines = text.split(/\r?\n/);
    const blocks = [];
    let listItems = [];

    const flushList = () => {
        if (!listItems.length) return;
        blocks.push(`<ul>${listItems.join("")}</ul>`);
        listItems = [];
    };

    lines.forEach((rawLine) => {
        const line = rawLine.trim();
        if (!line) {
            flushList();
            return;
        }
        if (line.startsWith("- ")) {
            listItems.push(`<li>${formatAssistantInline(line.slice(2))}</li>`);
            return;
        }
        flushList();
        const heading = line.match(/^\*\*(.+?)\*\*$/);
        blocks.push(heading
            ? `<h3>${formatAssistantInline(heading[1])}</h3>`
            : `<p>${formatAssistantInline(line)}</p>`);
    });

    flushList();
    return `<div class="assistant-response">${blocks.join("")}</div>`;
}

function formatAssistantInline(text) {
    return escapeAssistantHtml(text)
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(
            /(https?:\/\/[^\s<]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
}

function escapeAssistantHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
