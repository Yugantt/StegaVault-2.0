/*==========================================
        STEGAVAULT 3.0 DASHBOARD
        FINAL WORKING VERSION
==========================================*/

document.addEventListener("DOMContentLoaded", function() {

    console.log("✅ Dashboard JS Loaded");

    /*==================================
            ELEMENTS
    ==================================*/

    var sidebar = document.getElementById("sidebar");
    var menuBtn = document.getElementById("menuBtn");
    var overlay = document.getElementById("sidebarOverlay");

    var themeBtn = document.getElementById("themeToggle");

    var notificationBtn = document.getElementById("notificationBtn");
    var notificationDropdown = document.getElementById("notificationDropdown");

    var profileBtn = document.getElementById("profileBtn");
    var profileDropdown = document.getElementById("profileDropdown");


    /*==================================
            DARK MODE - FINAL FIX
    ==================================*/

    function setDarkMode(isDark) {
        console.log("Setting dark mode to:", isDark);
        
        if (isDark) {
            document.body.classList.add("dark-mode");
        } else {
            document.body.classList.remove("dark-mode");
        }
        localStorage.setItem("theme", isDark ? "dark" : "light");

        // Update icon
        if (themeBtn) {
            var icon = themeBtn.querySelector("i");
            if (icon) {
                if (isDark) {
                    icon.className = "fa-solid fa-sun";
                } else {
                    icon.className = "fa-solid fa-moon";
                }
            }
        }
        
        console.log("Dark mode class present:", document.body.classList.contains("dark-mode"));
    }

    // Load saved theme on page load
    var savedTheme = localStorage.getItem("theme");
    console.log("Saved theme:", savedTheme);
    
    if (savedTheme === "dark") {
        setDarkMode(true);
    } else {
        setDarkMode(false);
    }

    // Toggle theme on button click
    if (themeBtn) {
        console.log("✅ Theme button found");
        themeBtn.addEventListener("click", function(e) {
            e.preventDefault();
            e.stopPropagation();
            var isDark = !document.body.classList.contains("dark-mode");
            console.log("Toggle clicked, new state:", isDark);
            setDarkMode(isDark);
        });
    } else {
        console.log("❌ Theme button NOT found!");
    }


    /*==================================
            SIDEBAR TOGGLE
    ==================================*/

    if (menuBtn && sidebar) {
        menuBtn.addEventListener("click", function(e) {
            e.preventDefault();
            sidebar.classList.toggle("show");
            if (overlay) {
                overlay.classList.toggle("show");
            }
        });
    }

    if (overlay) {
        overlay.addEventListener("click", function() {
            sidebar.classList.remove("show");
            overlay.classList.remove("show");
        });
    }


    /*==================================
            NOTIFICATION DROPDOWN
    ==================================*/

    if (notificationBtn && notificationDropdown) {
        console.log("✅ Notification button found");
        notificationBtn.addEventListener("click", function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // ✅ Close profile dropdown if open
            if (profileDropdown) profileDropdown.classList.remove("show");
            
            notificationDropdown.classList.toggle("show");
            console.log("Notification toggled:", notificationDropdown.classList.contains("show"));
        });
    } else {
        console.log("❌ Notification button NOT found!");
    }


    /*==================================
            PROFILE DROPDOWN - ✅ ADDED
    ==================================*/

    if (profileBtn && profileDropdown) {
        console.log("✅ Profile button found");
        profileBtn.addEventListener("click", function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // ✅ Close notification dropdown if open
            if (notificationDropdown) notificationDropdown.classList.remove("show");
            
            profileDropdown.classList.toggle("show");
            console.log("Profile toggled:", profileDropdown.classList.contains("show"));
        });
    } else {
        console.log("❌ Profile button NOT found!");
    }


    /*==================================
            CLOSE DROPDOWN (Click Outside) - ✅ UPDATED
    ==================================*/

    document.addEventListener("click", function(e) {
        // Close notification dropdown
        if (notificationDropdown && notificationDropdown.classList.contains("show")) {
            if (notificationBtn && !notificationBtn.contains(e.target) && !notificationDropdown.contains(e.target)) {
                notificationDropdown.classList.remove("show");
            }
        }
        
        // ✅ Close profile dropdown
        if (profileDropdown && profileDropdown.classList.contains("show")) {
            if (profileBtn && !profileBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
                profileDropdown.classList.remove("show");
            }
        }
    });


    /*==================================
            CARD HOVER EFFECT
    ==================================*/

    document.querySelectorAll(".stat-card, .action-card, .module-card").forEach(function(card) {
        card.addEventListener("mouseenter", function() {
            this.style.transform = "translateY(-8px)";
        });
        card.addEventListener("mouseleave", function() {
            this.style.transform = "translateY(0px)";
        });
    });


    /*==================================
            BUTTON RIPPLE EFFECT
    ==================================*/

    document.querySelectorAll(".action-btn, .primary-btn, .secondary-btn").forEach(function(btn) {
        btn.addEventListener("click", function(e) {
            var ripple = document.createElement("span");
            ripple.className = "ripple";
            var rect = this.getBoundingClientRect();
            ripple.style.left = (e.clientX - rect.left) + "px";
            ripple.style.top = (e.clientY - rect.top) + "px";
            this.appendChild(ripple);
            setTimeout(function() {
                ripple.remove();
            }, 600);
        });
    });


    /*==================================
            PAGE FADE
    ==================================*/

    document.body.classList.add("page-loaded");
    console.log("✅ StegaVault Dashboard Loaded Successfully");

});