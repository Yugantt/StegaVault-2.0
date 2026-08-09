/*==========================================
        STEGAVAULT 3.0 - VIDEO PAGE
==========================================*/

// ===============================
// FILE UPLOAD HANDLER
// ===============================
function setupFileUpload(type) {
    const input = document.getElementById(type + 'Video');
    const fileInfo = document.getElementById(type + 'FileInfo');

    if (!input || !fileInfo) return;

    const fileName = fileInfo.querySelector('.file-name');
    const uploadLabel = input.closest('.upload-box').querySelector('.upload-label');

    input.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            fileName.textContent = this.files[0].name;
            fileInfo.style.display = 'flex';
            uploadLabel.style.display = 'none';
        } else {
            fileInfo.style.display = 'none';
            uploadLabel.style.display = 'flex';
        }
    });
}

// ===============================
// REMOVE FILE
// ===============================
function removeFile(type) {
    const input = document.getElementById(type + 'Video');
    const fileInfo = document.getElementById(type + 'FileInfo');

    if (!input) return;

    const uploadLabel = input.closest('.upload-box').querySelector('.upload-label');

    input.value = '';
    if (fileInfo) fileInfo.style.display = 'none';
    if (uploadLabel) uploadLabel.style.display = 'flex';
}


document.addEventListener('DOMContentLoaded', function () {

    // ===============================
    // FILE INPUTS
    // ===============================
    setupFileUpload('encode');
    setupFileUpload('decode');

    // ===============================
    // DRAG AND DROP
    // ===============================
    document.querySelectorAll('.upload-box').forEach(function (box) {
        const input = box.querySelector('input[type="file"]');
        const label = box.querySelector('.upload-label');

        if (!input || !label) return;

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function (eventName) {
            box.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(function (eventName) {
            box.addEventListener(eventName, function () {
                box.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(function (eventName) {
            box.addEventListener(eventName, function () {
                box.classList.remove('dragover');
            });
        });

        box.addEventListener('drop', function (e) {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                input.dispatchEvent(new Event('change'));
            }
        });
    });

    // ===============================
    // CHARACTER COUNTER
    // ===============================
    const messageBox = document.getElementById('messageBox');
    const charCount = document.getElementById('charCount');

    if (messageBox && charCount) {
        function updateCount() {
            const count = messageBox.value.length;
            charCount.textContent = count;

            if (count > 450) {
                charCount.style.color = '#ef4444';
            } else if (count > 400) {
                charCount.style.color = '#f59e0b';
            } else {
                charCount.style.color = '#3b82f6';
            }
        }

        messageBox.addEventListener('input', updateCount);
        updateCount();
    }

    // ===============================
    // COPY BUTTON
    // ===============================
    const decodedMessage = document.getElementById('decodedMessage');
    const copyBtn = document.getElementById('copyBtn');

    if (copyBtn && decodedMessage) {
        copyBtn.addEventListener('click', function () {
            const message = decodedMessage.value;

            if (!message || message.includes('No secret message')) {
                alert('Nothing to copy!');
                return;
            }

            const originalText = copyBtn.innerHTML;

            function done() {
                copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(function () {
                    copyBtn.innerHTML = originalText;
                }, 2000);
            }

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(message).then(done).catch(function () {
                    alert('Failed to copy!');
                });
            } else {
                decodedMessage.select();
                document.execCommand('copy');
                done();
            }
        });
    }

    // ===============================
    // PROGRESS BAR
    // ===============================
    if (window.StegaProgress) {
        StegaProgress.attach({
            form: document.getElementById('encodeForm'),
            title: 'Encoding Video',
            fallbackName: 'encoded.mp4'
        });

        StegaProgress.attach({
            form: document.getElementById('decodeForm'),
            title: 'Decoding Video',
            onMessage: function (message) {
                if (decodedMessage) decodedMessage.value = message;
            }
        });
    }

    // ===============================
    // SHOW / HIDE BUTTON
    // ===============================
    const toggleBtn = document.getElementById('toggleBtn');

    if (toggleBtn && decodedMessage) {
        let hidden = false;
        let realText = decodedMessage.value;

        toggleBtn.addEventListener('click', function () {
            hidden = !hidden;

            if (hidden) {
                realText = decodedMessage.value;
                decodedMessage.value = '•'.repeat(realText.length);
                toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i> Show';
            } else {
                decodedMessage.value = realText;
                toggleBtn.innerHTML = '<i class="fas fa-eye"></i> Hide';
            }
        });
    }

});
