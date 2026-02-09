/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#0f0f23',
        foreground: '#ffffff',
        card: '#1a1a2e',
        'card-foreground': '#ffffff',
        primary: '#00d9ff',
        'primary-foreground': '#000000',
        secondary: '#ff006e',
        'secondary-foreground': '#ffffff',
        accent: '#ffbe0b',
        'accent-secondary': '#fb5607',
        destructive: '#ef4444',
        border: '#2d2d44',
        input: '#2d2d44',
        ring: '#00d9ff',
        'neon-blue': '#00d9ff',
        'neon-pink': '#ff006e',
        'neon-orange': '#fb5607',
        'neon-yellow': '#ffbe0b',
        'electric-purple': '#8338ec',
      },
      fontFamily: {
        headings: ['Barlow Condensed', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'neon-blue': '0 0 20px rgba(0, 217, 255, 0.5)',
        'neon-pink': '0 0 20px rgba(255, 0, 110, 0.5)',
        'neon-yellow': '0 0 20px rgba(255, 190, 11, 0.5)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};