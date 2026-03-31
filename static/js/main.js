(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();

    // Initiate the wowjs
    new WOW().init();

    // Sticky Navbar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.sticky-top').css('top', '0px');
        } else {
            $('.sticky-top').css('top', '-100px');
        }
    });

    // ❌ DROPDOWN HOVER CODE HATAYA — CSS se fix ho chuka hai

    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });

    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });

    // Header carousel
    $(".header-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        items: 1,
        dots: false,
        loop: true,
        nav: true,
        navText: [
            '<i class="bi bi-chevron-left"></i>',
            '<i class="bi bi-chevron-right"></i>'
        ]
    });

    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        center: true,
        margin: 24,
        dots: true,
        loop: true,
        nav: false,
        responsive: {
            0: { items: 1 },
            768: { items: 2 },
            992: { items: 3 }
        }
    });


    // ================= DARK / LIGHT MODE =================
    const html = document.documentElement;
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');

    // Load saved theme
    const savedTheme = localStorage.getItem('csTheme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    updateIcon(savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const current = html.getAttribute('data-theme');
            const next = current === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', next);
            localStorage.setItem('csTheme', next);
            updateIcon(next);
        });
    }

    function updateIcon(theme) {
        if (!themeIcon) return;
        if (theme === 'dark') {
            themeIcon.className = 'fa fa-sun';
        } else {
            themeIcon.className = 'fa fa-moon';
        }
    }


    // ✅ Yeh function pehle define karna zaroori hai
    function getCSRFToken() {
        let cookieValue = null;
        document.cookie.split(';').forEach(function (cookie) {
            cookie = cookie.trim();
            if (cookie.startsWith('csrftoken=')) {
                cookieValue = cookie.substring('csrftoken='.length);
            }
        });
        // Fallback: Django ke meta tag se bhi le sako
        if (!cookieValue) {
            const meta = document.querySelector('meta[name="csrf-token"]');
            if (meta) cookieValue = meta.getAttribute('content');
        }
        return cookieValue;
    }


    // ================= WISHLIST LIVE UPDATE =================
    $(document).on("click", ".wishlist-btn", function (e) {
        e.preventDefault();

        const btn = $(this);
        const projectId = btn.data("id");
        const icon = btn.find("i");

        $.ajax({
            url: "/wishlist/toggle/",
            method: "POST",
            data: {
                project_id: projectId,
                csrfmiddlewaretoken: getCSRFToken()
            },
            success: function (data) {

                // ✅ Navbar wishlist badge update
                const countEl = $("#wishlist-count");
                if (data.wishlist_count > 0) {
                    countEl.text(data.wishlist_count).show();
                } else {
                    countEl.hide();
                }

                // ✅ Button icon toggle
                if (data.status === "added") {
                    icon.removeClass("fa-heart-o").addClass("fa-heart");
                    icon.css("color", "red");
                } else {
                    icon.removeClass("fa-heart").addClass("fa-heart-o");
                    icon.css("color", "");
                }
            },
            error: function (xhr) {
                if (xhr.status === 403) {
                    window.location.href = "/accounts/login/";
                }
            }
        });
    });


})(jQuery);