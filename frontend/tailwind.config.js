/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                slate: {
                    850: '#0f1b2e',
                }
            },
            animation: {
                fadeInUp: 'fadeInUp 0.5s ease-out forwards',
                fadeInUpSm: 'fadeInUp 0.5s ease-out 0.1s forwards',
                fadeInUpMd: 'fadeInUp 0.5s ease-out 0.2s forwards',
                fadeInUpLg: 'fadeInUp 0.5s ease-out 0.3s forwards',
                fadeInScale: 'fadeInScale 0.5s ease-out forwards',
                slideInLeft: 'slideInLeft 0.5s ease-out forwards',
                scaleIn: 'scaleIn 0.4s ease-out forwards',
                pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                fadeInUp: {
                    '0%': { 
                        opacity: '0',
                        transform: 'translateY(20px)'
                    },
                    '100%': {
                        opacity: '1',
                        transform: 'translateY(0)'
                    },
                },
                fadeInScale: {
                    '0%': {
                        opacity: '0',
                        transform: 'scale(0.95)'
                    },
                    '100%': {
                        opacity: '1',
                        transform: 'scale(1)'
                    },
                },
                slideInLeft: {
                    '0%': {
                        opacity: '0',
                        transform: 'translateX(-30px)'
                    },
                    '100%': {
                        opacity: '1',
                        transform: 'translateX(0)'
                    },
                },
                scaleIn: {
                    '0%': {
                        opacity: '0',
                        transform: 'scale(0.95)'
                    },
                    '100%': {
                        opacity: '1',
                        transform: 'scale(1)'
                    },
                },
                pulse: {
                    '0%, 100%': { opacity: '1' },
                    '50%': { opacity: '0.5' }
                }
            },
        },
    },
    plugins: [],
}

