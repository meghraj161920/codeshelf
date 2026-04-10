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

    // Initiate WOW
    new WOW().init();

   
    // ================= BACK TO TOP =================
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').css({ opacity: 1, visibility: 'visible' });
        } else {
            $('.back-to-top').css({ opacity: 0, visibility: 'hidden' });
        }
    });

    $('.back-to-top').click(function () {
        $('html, body').animate({ scrollTop: 0 }, 1500, 'easeInOutExpo');
        return false;
    });

    // ================= LIVE SEARCH SUGGESTIONS =================
    const searchInput = document.querySelector('.search-input');
    const searchWrap = document.querySelector('.search-wrap');

    if (searchInput && searchWrap) {
        const dropdown = document.createElement('div');
        dropdown.id = 'search-dropdown';
        dropdown.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--bg-dropdown, #fff);
            border: 1px solid var(--border, #eee);
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
            z-index: 9999;
            margin-top: 6px;
            overflow: hidden;
            display: none;
        `;

        searchWrap.style.position = 'relative';
        searchWrap.appendChild(dropdown);

        let timer;

        searchInput.addEventListener('input', function () {
            const q = this.value.trim();
            clearTimeout(timer);

            if (q.length < 2) {
                dropdown.style.display = 'none';
                return;
            }

            timer = setTimeout(() => {
                fetch(`/projects/search-suggestions/?q=${encodeURIComponent(q)}`)
                    .then(res => res.json())
                    .then(data => {
                        dropdown.innerHTML = '';

                        if (data.results.length === 0) {
                            dropdown.style.display = 'none';
                            return;
                        }

                        data.results.forEach(project => {
                            const item = document.createElement('a');
                            item.href = `/projects/${project.slug}/`;
                            item.style.cssText = `
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                padding: 10px 14px;
                                text-decoration: none;
                                color: var(--text, #1a1f36);
                                font-size: 13px;
                                border-bottom: 1px solid var(--border, #f0f0f0);
                                transition: background 0.15s;
                            `;
                            item.innerHTML = `
                                <div>
                                    <i class="fa-solid fa-magnifying-glass" style="color:#06BBCC;margin-right:8px;font-size:11px;"></i>
                                    <strong>${project.title}</strong>
                                    <span style="color:var(--text-muted);font-size:11px;margin-left:6px;">
                                        ${project.technology}
                                    </span>
                                </div>
                                <span style="color:#06BBCC;font-weight:700;">₹${project.price}</span>
                            `;
                            item.addEventListener('mouseenter', () => item.style.background = 'var(--bg-hover)');
                            item.addEventListener('mouseleave', () => item.style.background = 'transparent');
                            dropdown.appendChild(item);
                        });

                        const viewAll = document.createElement('a');
                        viewAll.href = `/projects/?q=${encodeURIComponent(q)}`;
                        viewAll.style.cssText = `
                            display: block;
                            padding: 10px 14px;
                            text-align: center;
                            color: #06BBCC;
                            font-size: 12px;
                            font-weight: 600;
                            text-decoration: none;
                        `;
                        viewAll.textContent = `View all results for "${q}"`;
                        dropdown.appendChild(viewAll);
                        dropdown.style.display = 'block';
                    });
            }, 300);
        });

        document.addEventListener('click', function (e) {
            if (!searchWrap.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });

        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') dropdown.style.display = 'none';
        });
    }

    // ================= CAROUSELS =================
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

    // ================= DARK MODE =================
    const html = document.documentElement;
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');

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
        themeIcon.className = theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    }

})(jQuery);