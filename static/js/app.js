// ===========================================
// StegaVault 2.0
// Main JavaScript
// ===========================================

document.addEventListener("DOMContentLoaded", () => {

    console.log("✅ StegaVault 2.0 Loaded Successfully");

    // ===========================================
    // Input Focus Effect
    // ===========================================

    const inputs = document.querySelectorAll(
        "input, textarea, select"
    );

    inputs.forEach(input => {

        input.addEventListener("focus", () => {

            input.style.border = "2px solid #3b82f6";
            input.style.boxShadow =
                "0 0 12px rgba(59,130,246,.35)";

        });

        input.addEventListener("blur", () => {

            input.style.border = "";
            input.style.boxShadow = "";

        });

    });

    // ===========================================
    // Button Loading Animation
    // ===========================================

    const forms = document.querySelectorAll("form");

    forms.forEach(form => {

        form.addEventListener("submit", function () {

            const button = this.querySelector(
                'button[type="submit"]'
            );

            if (!button || button.disabled) return;

            button.dataset.originalText = button.innerHTML;

            button.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Please Wait...';

            button.disabled = true;

        });

    });

    // ===========================================
    // Auto Hide Flash Messages
    // ===========================================

    const flashMessages =
        document.querySelectorAll(".flash-message");

    flashMessages.forEach(message => {

        setTimeout(() => {

            message.style.transition =
                "opacity .5s ease";

            message.style.opacity = "0";

            setTimeout(() => {

                message.remove();

            }, 500);

        }, 3500);

    });

    // ===========================================
    // Character Counter
    // ===========================================

    const textarea = document.querySelector(
        'textarea[name="message"]'
    );

    if (textarea) {

        const counter = document.createElement("small");

        counter.style.display = "block";
        counter.style.marginTop = "8px";
        counter.style.opacity = ".75";

        textarea.after(counter);

        const updateCounter = () => {

            counter.textContent =
                `${textarea.value.length}/500 characters`;

        };

        textarea.addEventListener(
            "input",
            updateCounter
        );

        updateCounter();

    }

});
/*=======================================
Password Visibility Toggle
========================================*/
function togglePassword(inputId, button) {

    const input = document.getElementById(inputId);

    if (!input) return;

    const icon = button.querySelector('i');

    if (input.type === 'password') {

        input.type = 'text';

        if (icon) {
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        }

    } else {

        input.type = 'password';

        if (icon) {
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }

    }
}