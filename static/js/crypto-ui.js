/**
 * Shared behaviour for the encryption password fields and the image
 * capacity indicator.
 */
(function () {
    "use strict";

    // ----------------------------------------------
    // Show / hide password
    // ----------------------------------------------
    document.addEventListener("click", function (e) {
        var btn = e.target.closest(".password-toggle");
        if (!btn) return;

        var input = document.getElementById(btn.dataset.target);
        if (!input) return;

        var hidden = input.type === "password";
        input.type = hidden ? "text" : "password";

        var icon = btn.querySelector("i");
        if (icon) {
            icon.classList.toggle("fa-eye", !hidden);
            icon.classList.toggle("fa-eye-slash", hidden);
        }
    });

    // ----------------------------------------------
    // Image capacity indicator
    // ----------------------------------------------
    // Encryption adds a fixed overhead, so the usable capacity shrinks
    // once a password is entered.
    var ENCRYPTION_OVERHEAD = 150;
    var DELIMITER_BITS = 16;

    var fileInput = document.getElementById("encodeImage");
    var messageBox = document.getElementById("messageBox");
    var passwordBox = document.getElementById("encodePassword");

    if (!fileInput || !messageBox) return;

    var hint = document.createElement("p");
    hint.className = "capacity-hint";
    messageBox.parentNode.insertBefore(hint, messageBox.nextSibling);

    var capacity = 0;

    function refresh() {
        if (!capacity) {
            hint.classList.remove("show");
            return;
        }

        var usable = capacity;
        if (passwordBox && passwordBox.value.trim()) {
            usable = Math.max(0, usable - ENCRYPTION_OVERHEAD);
        }

        var used = messageBox.value.length;
        var over = used > usable;

        hint.classList.add("show");
        hint.classList.toggle("over", over);
        hint.innerHTML =
            '<i class="fas fa-' + (over ? "triangle-exclamation" : "circle-info") + '"></i>' +
            (over
                ? "Message too long \u2014 this image holds " + usable.toLocaleString() + " characters"
                : "This image can hold about " + usable.toLocaleString() + " characters");
    }

    fileInput.addEventListener("change", function () {
        var file = fileInput.files && fileInput.files[0];
        if (!file) {
            capacity = 0;
            refresh();
            return;
        }

        var img = new Image();
        img.onload = function () {
            // 3 colour channels per pixel, 1 bit each, 8 bits per character
            capacity = Math.floor((img.width * img.height * 3 - DELIMITER_BITS) / 8);
            refresh();
            URL.revokeObjectURL(img.src);
        };
        img.onerror = function () {
            capacity = 0;
            refresh();
        };
        img.src = URL.createObjectURL(file);
    });

    messageBox.addEventListener("input", refresh);
    if (passwordBox) passwordBox.addEventListener("input", refresh);
})();
