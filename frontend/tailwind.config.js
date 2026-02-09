/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0a',
        foreground: '#ffffff',
        card: '#171717',
        'card-foreground': '#ffffff',
        primary: '#fbbf24',
        'primary-foreground': '#000000',
        secondary: '#3b82f6',
        'secondary-foreground': '#ffffff',
        accent: '#22c55e',
        destructive: '#ef4444',
        border: '#262626',
        input: '#262626',
        ring: '#fbbf24',
      },
      fontFamily: {
        headings: ['Barlow Condensed', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};