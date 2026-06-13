const card = document.querySelector("#auth-card");
const startingTab = document.body.dataset.startingTab || "login";
const switchButtons = document.querySelectorAll(".switch-button");
const forms = document.querySelectorAll(".auth-form");
const registerPassword = document.querySelector("#register-password");
const confirmPassword = document.querySelector("#confirm-password");
const strengthText = document.querySelector("#strength-text");
const strengthBar = document.querySelector("#strength-bar");
const rulesText = document.querySelector("#rules-text");
const cardTitle = document.querySelector("#card-title");
const cardCopy = document.querySelector("#card-copy");
const serverMessage = document.querySelector(".server-message");
let switchTimer;
const viewText = {
    login: {
        title: "Welcome Back",
        copy: "Sign in with your username and password.",
    },
    register: {
        title: "Create Account",
        copy: "Use a strong password to protect your account.",
    },
};

function showTab(tabName, shouldAnimate = true) {
    // Keep both visual state and tab accessibility state in sync.
    const currentTab = card.dataset.view || "login";

    if (currentTab === tabName && shouldAnimate) {
        return;
    }

    if (shouldAnimate) {
        clearTimeout(switchTimer);
        card.dataset.direction = tabName === "register" ? "forward" : "back";
        card.classList.remove("is-switching");
        void card.offsetWidth;
        card.classList.add("is-switching");
        switchTimer = setTimeout(() => card.classList.remove("is-switching"), 420);
    }

    card.dataset.view = tabName;
    cardTitle.textContent = viewText[tabName].title;
    cardCopy.textContent = viewText[tabName].copy;

    switchButtons.forEach((button) => {
        const isActive = button.dataset.tab === tabName;
        button.classList.toggle("active", isActive);
        button.setAttribute("aria-selected", String(isActive));
    });

    forms.forEach((form) => {
        const formName = form.id.replace("-form", "");
        const isActive = formName === tabName;
        form.classList.toggle("active", isActive);
        form.setAttribute("aria-hidden", String(!isActive));
    });

    if (serverMessage) {
        const messageTab = serverMessage.dataset.messageTab;
        serverMessage.classList.toggle("is-hidden", Boolean(messageTab && messageTab !== tabName));
    }
}

function getPasswordStrength(password) {
    // Mirrors the server-side strength rules used before registration.
    const checks = [
        ["lowercase", /[a-z]/.test(password)],
        ["uppercase", /[A-Z]/.test(password)],
        ["number", /\d/.test(password)],
        ["symbol", /[^A-Za-z0-9]/.test(password)],
        ["at least 12 characters", password.length >= 12],
    ];
    const passed = checks.filter((item) => item[1]).length;
    const missing = checks.filter((item) => !item[1]).map((item) => item[0]);
    const strength = passed === 5 ? "Strong" : passed >= 3 ? "Medium" : "Weak";

    return { passed, missing, strength };
}

function updatePasswordMeter() {
    const result = getPasswordStrength(registerPassword.value);
    strengthText.textContent = result.strength;
    strengthText.dataset.strength = result.strength.toLowerCase();
    strengthBar.style.width = `${(result.passed / 5) * 100}%`;
    strengthBar.dataset.strength = result.strength.toLowerCase();
    rulesText.textContent = result.missing.length
        ? `Needs: ${result.missing.join(", ")}`
        : "All requirements met";

    return result;
}

function setFieldError(input, message) {
    // Inline validation is announced to assistive technology through aria-describedby.
    const field = input.closest(".field");
    const error = field.querySelector(".field-error");

    field.classList.toggle("invalid", Boolean(message));
    input.setAttribute("aria-invalid", String(Boolean(message)));
    input.setAttribute("aria-describedby", error.id);
    error.textContent = message;
}

function validateField(input) {
    let message = "";
    const value = input.value.trim();

    if (input.required && !value) {
        message = "This field is required.";
    } else if (input.id === "register-username" && value.length < 3) {
        message = "Username must be at least 3 characters.";
    } else if (input.id === "register-password") {
        const result = updatePasswordMeter();
        if (result.strength !== "Strong") {
            message = "Use a strong password before registering.";
        }
    } else if (input.id === "confirm-password" && input.value !== registerPassword.value) {
        message = "Passwords must match.";
    }

    setFieldError(input, message);
    return !message;
}

switchButtons.forEach((button) => {
    button.addEventListener("click", () => showTab(button.dataset.tab));
});

document.querySelectorAll(".password-toggle").forEach((button) => {
    button.addEventListener("click", () => {
        // The same icon button pattern works for login, password, and confirmation fields.
        const input = button.parentElement.querySelector("input");
        const isVisible = input.type === "text";

        input.type = isVisible ? "password" : "text";
        button.setAttribute("aria-pressed", String(!isVisible));
        button.setAttribute("aria-label", isVisible ? "Show password" : "Hide password");
    });
});

document.querySelectorAll("input[required]").forEach((input) => {
    input.addEventListener("input", () => validateField(input));
    input.addEventListener("blur", () => validateField(input));
});

registerPassword.addEventListener("input", () => {
    updatePasswordMeter();
    if (confirmPassword.value) {
        validateField(confirmPassword);
    }
});

forms.forEach((form) => {
    form.addEventListener("submit", (event) => {
        // Stop only invalid client-side submissions; valid forms still post to Flask.
        const fields = Array.from(form.querySelectorAll("input[required]"));
        const isValid = fields.every(validateField);

        if (!isValid) {
            event.preventDefault();
            form.classList.remove("shake");
            void form.offsetWidth;
            form.classList.add("shake");
        }
    });
});

showTab(startingTab, false);
updatePasswordMeter();
