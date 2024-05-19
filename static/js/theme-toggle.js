document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("theme-toggle");
  const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");

  // Check localStorage for user preference
  const currentTheme =
    localStorage.getItem("theme") ||
    (prefersDarkScheme.matches ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", currentTheme);
  themeToggle.checked = currentTheme === "dark";

  // Listen for the toggle switch change
  themeToggle.addEventListener("change", () => {
    const theme = themeToggle.checked ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  });

  // Listen for system theme change
  prefersDarkScheme.addEventListener("change", (e) => {
    const theme = e.matches ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", theme);
    themeToggle.checked = theme === "dark";
    localStorage.setItem("theme", theme);
  });
});
