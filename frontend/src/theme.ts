'use client'; // This can be a client component file if you need theme logic
import { createTheme } from '@mui/material/styles';
import { Roboto } from 'next/font/google';

const roboto = Roboto({
  weight: ['300', '400', '500', '700'],
  subsets: ['latin'],
  display: 'swap',
});

const theme = createTheme({
  typography: {
    fontFamily: roboto.style.fontFamily,
  },
  palette: {
    mode: 'light',
    // Add your custom palette colors here
    primary: {
      main: '#556cd6',
    },
    secondary: {
      main: '#19857b',
    },
    // ...
  },
});

export default theme;