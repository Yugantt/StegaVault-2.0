/*==========================================
    STEGAVAULT 3.0 - PROGRESS OVERLAY

    Submits an encode/decode form over fetch() and polls
    /progress/<job_id> to drive a real percentage bar.
==========================================*/

(function (window) {

    var POLL_INTERVAL = 300;

    function newJobId() {
        return 'job-' + Date.now() + '-' + Math.random().toString(36).slice(2, 10);
    }

    /*==================================
            OVERLAY
    ==================================*/

    function buildOverlay() {
        var existing = document.getElementById('stegaProgressOverlay');
        if (existing) return existing;

        var overlay = document.createElement('div');
        overlay.id = 'stegaProgressOverlay';
        overlay.className = 'stega-progress-overlay';
        overlay.innerHTML =
            '<div class="stega-progress-box">' +
            '  <div class="stega-progress-title">Processing</div>' +
            '  <div class="stega-progress-stage">Starting...</div>' +
            '  <div class="stega-progress-track">' +
            '    <div class="stega-progress-fill"></div>' +
            '  </div>' +
            '  <div class="stega-progress-percent">0%</div>' +
            '</div>';

        document.body.appendChild(overlay);
        return overlay;
    }

    function showOverlay(title) {
        var overlay = buildOverlay();
        overlay.querySelector('.stega-progress-title').textContent = title;
        overlay.querySelector('.stega-progress-stage').textContent = 'Starting...';
        setPercent(overlay, 0);
        overlay.classList.add('show');
        return overlay;
    }

    function hideOverlay(overlay) {
        if (overlay) overlay.classList.remove('show');
    }

    function setPercent(overlay, percent) {
        overlay.querySelector('.stega-progress-fill').style.width = percent + '%';
        overlay.querySelector('.stega-progress-percent').textContent = percent + '%';
    }

    /*==================================
            POLLING
    ==================================*/

    function poll(jobId, overlay) {
        var stopped = false;

        function tick() {
            if (stopped) return;

            fetch('/progress/' + jobId, { headers: { 'X-Requested-With': 'fetch' } })
                .then(function (res) { return res.json(); })
                .then(function (data) {
                    if (stopped) return;

                    setPercent(overlay, data.percent);
                    if (data.stage) {
                        overlay.querySelector('.stega-progress-stage').textContent = data.stage;
                    }
                    if (!data.done) {
                        setTimeout(tick, POLL_INTERVAL);
                    }
                })
                .catch(function () {
                    if (!stopped) setTimeout(tick, POLL_INTERVAL);
                });
        }

        tick();

        return function stop() { stopped = true; };
    }

    /*==================================
            DOWNLOAD A BLOB RESPONSE
    ==================================*/

    function downloadBlob(blob, filename) {
        var url = URL.createObjectURL(blob);
        var link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    function filenameFromResponse(res, fallback) {
        var disposition = res.headers.get('Content-Disposition') || '';
        var match = disposition.match(/filename="?([^";]+)"?/);
        return match ? match[1] : fallback;
    }

    /*==================================
            PUBLIC API
    ==================================*/

    /**
     * options:
     *   form           - the <form> element
     *   title          - overlay heading, e.g. "Encoding Audio"
     *   mode           - "download" (encode) or "json" (decode)
     *   fallbackName   - download filename if the server sends none
     *   onMessage      - for mode "json": function(message)
     */
    function attach(options) {
        var form = options.form;
        if (!form) return;

        form.addEventListener('submit', function (e) {
            e.preventDefault();

            var jobId = newJobId();
            var data = new FormData(form);
            data.append('job_id', jobId);

            var overlay = showOverlay(options.title || 'Processing');
            var stopPolling = poll(jobId, overlay);

            var headers = { 'X-Requested-With': 'fetch' };

            var token = form.querySelector('input[name="csrf_token"]');
            if (token) headers['X-CSRFToken'] = token.value;

            fetch(form.action, {
                method: 'POST',
                body: data,
                headers: headers
            })
                .then(function (res) {
                    var type = res.headers.get('Content-Type') || '';

                    if (!res.ok || type.indexOf('application/json') !== -1) {
                        return res.json().then(function (payload) {
                            if (payload.success === false) {
                                throw new Error(payload.error || 'Request failed');
                            }
                            return { json: payload };
                        });
                    }

                    return res.blob().then(function (blob) {
                        return {
                            blob: blob,
                            filename: filenameFromResponse(res, options.fallbackName || 'output')
                        };
                    });
                })
                .then(function (result) {
                    setPercent(overlay, 100);
                    overlay.querySelector('.stega-progress-stage').textContent = 'Done';

                    setTimeout(function () {
                        stopPolling();
                        hideOverlay(overlay);

                        if (result.blob) {
                            downloadBlob(result.blob, result.filename);
                        } else if (options.onMessage) {
                            options.onMessage(result.json.message);
                        }
                    }, 400);
                })
                .catch(function (err) {
                    stopPolling();
                    hideOverlay(overlay);
                    alert(err.message || 'Something went wrong.');
                });
        });
    }

    window.StegaProgress = { attach: attach };

})(window);
