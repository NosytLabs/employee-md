/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./web/templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        // Soft, paper-like accent inspired by worker.md / soul.md.
        brand: {
          DEFAULT: "#111111",
          dark: "#000000",
          light: "#3f3f46",
        },
        // "ink" is now a neutral light-paper scale (was dark slate).
        // We keep the same token names so existing templates pick up the
        // new palette automatically — bg-ink-900 etc. become near-white
        // with very subtle warm tint.
        ink: {
          900: "#ffffff", // page bg
          800: "#fafaf9", // raised surface (cards / nav strip)
          700: "#e7e5e4", // borders
          500: "#78716c", // muted body text
          300: "#44403c", // body text
          100: "#1c1917", // headings / strong text
        },
        accent: {
          DEFAULT: "#15803d", // green pill (worker.md style "evergreen" badge)
          soft: "#dcfce7",
          ring: "#86efac",
        },
      },
      fontFamily: {
        // Display serif for h1/h2 (soul.md / worker.md aesthetic).
        serif: ['"Source Serif 4"', '"Source Serif Pro"', "Georgia", "Cambria", "Times New Roman", "serif"],
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "Roboto", "sans-serif"],
        mono: ['"JetBrains Mono"', "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      typography: ({ theme }) => ({
        DEFAULT: {
          css: {
            "--tw-prose-body": theme("colors.ink.300"),
            "--tw-prose-headings": theme("colors.ink.100"),
            "--tw-prose-links": theme("colors.brand.DEFAULT"),
            "--tw-prose-bold": theme("colors.ink.100"),
            "--tw-prose-code": theme("colors.ink.100"),
            "--tw-prose-quotes": theme("colors.ink.300"),
            "--tw-prose-borders": theme("colors.ink.700"),
            maxWidth: "none",
          },
        },
      }),
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
