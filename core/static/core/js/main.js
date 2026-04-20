(() => {
  const STORAGE_KEY = "roomiehku.theme";
  const THEMES = ["light", "dark", "system"];

  function getStoredTheme() {
    try {
      const value = window.localStorage.getItem(STORAGE_KEY);
      if (value && THEMES.includes(value)) {
        return value;
      }
    } catch (error) {
      // Ignore localStorage unavailability and fall back to system mode.
    }
    return "system";
  }

  function applyTheme(theme) {
    if (theme === "system") {
      document.documentElement.removeAttribute("data-theme");
    } else {
      document.documentElement.setAttribute("data-theme", theme);
    }
    try {
      window.localStorage.setItem(STORAGE_KEY, theme);
    } catch (error) {
      // Ignore localStorage write failures in restricted browser modes.
    }
    document.querySelectorAll("[data-theme-option]").forEach((button) => {
      const isActive = button.dataset.themeOption === theme;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
  }

  function initThemeSwitch() {
    const initial = getStoredTheme();
    applyTheme(initial);

    document.querySelectorAll("[data-theme-option]").forEach((button) => {
      button.addEventListener("click", () => {
        applyTheme(button.dataset.themeOption || "system");
      });
    });

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const onMediaChange = () => {
      if (getStoredTheme() === "system") {
        applyTheme("system");
      }
    };

    if (typeof media.addEventListener === "function") {
      media.addEventListener("change", onMediaChange);
    } else if (typeof media.addListener === "function") {
      media.addListener(onMediaChange);
    }
  }

  function initMobileMenus() {
    const toggles = document.querySelectorAll("[data-mobile-toggle]");
    toggles.forEach((toggle) => {
      const targetId = toggle.getAttribute("data-mobile-toggle");
      const target = targetId ? document.getElementById(targetId) : null;
      if (!target) {
        return;
      }

      const closeMenu = () => {
        toggle.setAttribute("aria-expanded", "false");
        target.classList.remove("is-open");
      };

      toggle.addEventListener("click", () => {
        const expanded = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", expanded ? "false" : "true");
        target.classList.toggle("is-open", !expanded);
      });

      target.querySelectorAll("[data-mobile-close]").forEach((item) => {
        item.addEventListener("click", closeMenu);
      });

      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
          closeMenu();
        }
      });

      document.addEventListener("click", (event) => {
        if (
          target.classList.contains("is-open") &&
          !target.contains(event.target) &&
          !toggle.contains(event.target)
        ) {
          closeMenu();
        }
      });
    });
  }

  function normalizePath(path) {
    if (!path) {
      return "/";
    }
    return path.endsWith("/") ? path : `${path}/`;
  }

  function resolveAppTabGroup(pathname) {
    const path = normalizePath(pathname);

    if (path === "/" || path === "/app/" || path === "/app/listings/") {
      return "listings";
    }

    if (/^\/app\/listings\/new\/$/.test(path)) {
      return "new";
    }

    if (/^\/app\/listings\/\d+\/(?:edit|delete)\/$/.test(path)) {
      return "my-posts";
    }

    if (path === "/app/my-posts/") {
      return "my-posts";
    }

    if (path === "/app/saved/") {
      return "saved";
    }

    if (path === "/app/profile/edit/" || /^\/auth\/(?:login|signup)\/$/.test(path)) {
      return "profile";
    }

    if (/^\/app\/listings\/\d+\/$/.test(path)) {
      return "listings";
    }

    return null;
  }

  function setActiveNavLinks() {
    const currentPath = window.location.pathname;
    document.querySelectorAll("[data-nav-link]").forEach((link) => {
      const href = link.getAttribute("href");
      if (!href) {
        return;
      }

      const isActive =
        currentPath === href ||
        (href !== "/" && currentPath.startsWith(href));
      link.classList.toggle("active", isActive);
      link.setAttribute("aria-current", isActive ? "page" : "false");
    });
  }

  function setActiveMobileTabs() {
    const tabLinks = document.querySelectorAll("[data-mobile-tab]");
    if (!tabLinks.length) {
      return;
    }

    const currentPath = normalizePath(window.location.pathname);
    const activeGroup = resolveAppTabGroup(currentPath);

    tabLinks.forEach((link) => {
      const href = link.getAttribute("href") || "";
      const routeGroup = link.dataset.routeGroup || "";
      const hrefPath = href.startsWith("/") ? normalizePath(href) : "";
      const isActive = activeGroup
        ? routeGroup === activeGroup
        : hrefPath !== "/" && currentPath.startsWith(hrefPath);

      link.classList.toggle("is-active", isActive);
      link.setAttribute("aria-current", isActive ? "page" : "false");
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initThemeSwitch();
    initMobileMenus();
    setActiveNavLinks();
    setActiveMobileTabs();
  });
})();
