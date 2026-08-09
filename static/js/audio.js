/*==========================================
        STEGAVAULT 3.0 - AUDIO PAGE
==========================================*/

document.addEventListener("DOMContentLoaded", function () {

    /*==================================
            FILE NAME PREVIEW
    ==================================*/

    function bindFileInput(inputId) {
        var input = document.getElementById(inputId);
        if (!input) return;

        var label = document.querySelector('label[for="' + inputId + '"]');
        if (!label) return;

        var text = label.querySelector("span");
        if (!text) return;

        var defaultText = text.textContent;

        input.addEventListener("change", function () {
            if (input.files && input.files.length > 0) {
                text.textContent = input.files[0].name;
            } else {
                text.textContent = defaultText;
            }
        });
    }

    bindFileInput("encodeAudio");
    bindFileInput("decodeAudio");


    /*==================================
            CHARACTER COUNTER
    ==================================*/

    var messageBox = document.getElementById("messageBox");
    var charCount = document.getElementById("charCount");

    if (messageBox && charCount) {
        function updateCount() {
            charCount.textContent = messageBox.value.length;
        }
        messageBox.addEventListener("input", updateCount);
        updateCount();
    }


    /*==================================
            COPY DECODED MESSAGE
    ==================================*/

    var decodedMessage = document.getElementById("decodedMessage");
    var copyBtn = document.getElementById("copyBtn");

    if (copyBtn && decodedMessage) {
        copyBtn.addEventListener("click", function () {
            if (!decodedMessage.value.trim()) return;

            decodedMessage.select();
            decodedMessage.setSelectionRange(0, 99999);

            var original = copyBtn.innerHTML;

            function done() {
                copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied';
                setTimeout(function () {
                    copyBtn.innerHTML = original;
                }, 1500);
            }

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(decodedMessage.value).then(done);
            } else {
                document.execCommand("copy");
                done();
            }
        });
    }


    /*==================================
            PROGRESS BAR
    ==================================*/

    if (window.StegaProgress) {
        StegaProgress.attach({
            form: document.getElementById("encodeForm"),
            title: "Encoding Audio",
            fallbackName: "encoded.wav"
        });

        StegaProgress.attach({
            form: document.getElementById("decodeForm"),
            title: "Decoding Audio",
            onMessage: function (message) {
                if (decodedMessage) {
                    decodedMessage.value = message;
                }
            }
        });
    }


    /*==================================
            SHOW / HIDE MESSAGE
    ==================================*/

    var toggleBtn = document.getElementById("toggleBtn");

    if (toggleBtn && decodedMessage) {
        var hidden = false;
        var realText = decodedMessage.value;

        toggleBtn.addEventListener("click", function () {
            hidden = !hidden;

            if (hidden) {
                realText = decodedMessage.value;
                decodedMessage.value = "•".repeat(realText.length);
                toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i> Show / Hide';
            } else {
                decodedMessage.value = realText;
                toggleBtn.innerHTML = '<i class="fas fa-eye"></i> Show / Hide';
            }
        });
    }

});
