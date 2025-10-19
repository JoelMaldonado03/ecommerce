// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        primary: '#1E40AF',
        secondary: '#F59E0B',
        fondo: '#F3F4F6',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        title: ['"Playfair Display"', 'serif'],
      },
      spacing: {
        '128': '32rem',
      },
    },
  },
  darkMode: 'class', // si usas modo oscuro
  content: ['./index.html'], // asegúrate de incluir tus archivos
}
