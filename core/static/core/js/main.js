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

      toggle.addEventListener("click", () => {
        const expanded = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", expanded ? "false" : "true");
        target.classList.toggle("is-open", !expanded);
      });
    });
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

  document.addEventListener("DOMContentLoaded", () => {
    initThemeSwitch();
    initMobileMenus();
    setActiveNavLinks();
  });
})();
