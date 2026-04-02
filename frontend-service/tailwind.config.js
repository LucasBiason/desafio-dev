/** @type {import('tailwindcss').Config} */

const nord = {
  0: '#2e3440',
  1: '#3b4252',
  2: '#434c5e',
  3: '#4c566a',
  4: '#d8dee9',
  5: '#e5e9f0',
  6: '#eceff4',
  7: '#8fbcbb',
  8: '#88c0d0',
  9: '#81a1c1',
  10: '#5e81ac',
  11: '#bf616a',
  12: '#d08770',
  13: '#ebcb8b',
  14: '#a3be8c',
  15: '#b48ead',
}

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        nord,
        primary: nord[10],
        'primary-light': nord[9],
        'primary-dark': nord[10],
        accent: nord[8],
        success: nord[14],
        warning: nord[13],
        danger: nord[11],
        info: nord[9],
        bg: {
          dark: nord[0],
          DEFAULT: nord[1],
          light: nord[2],
          lighter: nord[3],
        },
        text: {
          primary: nord[6],
          secondary: nord[4],
          muted: nord[3],
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
