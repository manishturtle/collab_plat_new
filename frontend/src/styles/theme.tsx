'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { 
  createTheme, 
  ThemeProvider as MuiThemeProvider, 
  alpha, 
  Theme, 
  responsiveFontSizes 
} from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { Components } from '@mui/material/styles/components';
// Import for DataGrid component types
import { gridClasses } from '@mui/x-data-grid';

type ThemeMode = 'light' | 'dark';
type ThemeColor = 'blue' | 'purple' | 'green' | 'teal' | 'indigo' | 'amber' | 'red' | 'pink' | 'orange' | 'cyan' | 'deepPurple' | 'lime';
type FontFamily = 'inter' | 'roboto' | 'poppins' | 'montserrat' | 'opensans' | 'underdog';

interface ThemeContextType {
  mode: ThemeMode;
  color: ThemeColor;
  fontFamily: FontFamily;
  toggleTheme: () => void;
  changeThemeColor: (color: ThemeColor) => void;
  changeFontFamily: (font: FontFamily) => void;
}

const themeColors = {
  blue: {
    light: { 
      primary: '#1976d2', 
      secondary: '#f50057',
      background: '#f5f7fa',
      paper: '#ffffff',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      info: '#2196f3',
      accent1: '#bbdefb',
      accent2: '#64b5f6',
      accent3: '#1976d2'
    },
    dark: { 
      primary: '#90caf9', 
      secondary: '#f48fb1',
      background: '#121212',
      paper: '#1e1e1e',
      success: '#81c784',
      warning: '#ffb74d',
      error: '#e57373',
      info: '#64b5f6',
      accent1: '#0d47a1',
      accent2: '#1565c0',
      accent3: '#1976d2'
    },
  },
  purple: {
    light: { 
      primary: '#7b1fa2', 
      secondary: '#00bcd4',
      background: '#f8f6fc',
      paper: '#ffffff',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      info: '#2196f3',
      accent1: '#e1bee7',
      accent2: '#ba68c8',
      accent3: '#8e24aa'
    },
    dark: { 
      primary: '#ba68c8', 
      secondary: '#80deea',
      background: '#121212',
      paper: '#1e1e1e',
      success: '#81c784',
      warning: '#ffb74d',
      error: '#e57373',
      info: '#64b5f6',
      accent1: '#4a148c',
      accent2: '#6a1b9a',
      accent3: '#7b1fa2'
    },
  },
  green: {
    light: { 
      primary: '#2e7d32', 
      secondary: '#ff5722',
      background: '#f1f8e9',
      paper: '#ffffff',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      info: '#2196f3',
      accent1: '#c8e6c9',
      accent2: '#81c784',
      accent3: '#43a047'
    },
    dark: { 
      primary: '#81c784', 
      secondary: '#ff8a65',
      background: '#121212',
      paper: '#1e1e1e',
      success: '#81c784',
      warning: '#ffb74d',
      error: '#e57373',
      info: '#64b5f6',
      accent1: '#1b5e20',
      accent2: '#2e7d32',
      accent3: '#388e3c'
    },
  },
  teal: {
    light: { 
      primary: '#00796b', 
      secondary: '#ec407a',
      background: '#e0f2f1',
      paper: '#ffffff',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      info: '#2196f3',
      accent1: '#b2dfdb',
      accent2: '#4db6ac',
      accent3: '#00897b'
    },
    dark: { 
      primary: '#4db6ac', 
      secondary: '#f48fb1',
      background: '#121212',
      paper: '#1e1e1e',
      success: '#81c784',
      warning: '#ffb74d',
      error: '#e57373',
      info: '#64b5f6',
      accent1: '#004d40',
      accent2: '#00695c',
      accent3: '#00796b'
    },
  },
  indigo: {
    light: { 
      primary: '#3f51b5', 
      secondary: '#ff4081',
      background: '#e8eaf6',
      paper: '#ffffff',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      info: '#2196f3',
      accent1: '#c5cae9',
      accent2: '#7986cb',
      accent3: '#3949ab'
    },
    dark: { 
      primary: '#7986cb', 
      secondary: '#ff80ab',
      background: '#121212',
      paper: '#1e1e1e',
      success: '#81c784',
      warning: '#ffb74d',
      error: '#e57373',
      info: '#64b5f6',
      accent1: '#1a237e',
      accent2: '#283593',
      accent3: '#303f9f'
    },
  },
  amber: {
    light: { 
      primary: '#ff8f00', 
      secondary: '#448aff',
      background: '#fff8e1',
      paper: '#ffffff',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      info: '#2196f3',
      accent1: '#ffecb3',
      accent2: '#ffd54f',
      accent3: '#ffc107'
    },
    dark: { 
      primary: '#ffd54f', 
      secondary: '#82b1ff',
      background: '#121212',
      paper: '#1e1e1e',
      success: '#81c784',
      warning: '#ffb74d',
      error: '#e57373',
      info: '#64b5f6',
      accent1: '#ff6f00',
      accent2: '#ff8f00',
      accent3: '#ffa000'
    },
  },
  red: {
    light: { 
      primary: '#d32f2f', 
      secondary: '#2196f3',
      background: '#ffebee',
      paper: '#ffffff',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      info: '#2196f3',
      accent1: '#ffcdd2',
      accent2: '#e57373',
      accent3: '#f44336'
    },
    dark: { 
      primary: '#ef5350', 
      secondary: '#64b5f6',
      background: '#121212',
      paper: '#1e1e1e',
      success: '#81c784',
      warning: '#ffb74d',
      error: '#e57373',
      info: '#64b5f6',
      accent1: '#b71c1c',
      accent2: '#c62828',
      accent3: '#d32f2f'
    },
  },
  pink: {
    light: { 
      primary: '#c2185b', 
      secondary: '#00bcd4',
      background: '#fce4ec',
      paper: '#ffffff',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      info: '#2196f3',
      accent1: '#f8bbd0',
      accent2: '#f48fb1',
      accent3: '#ec407a'
    },
    dark: { 
      primary: '#f48fb1', 
      secondary: '#80deea',
      background: '#121212',
      paper: '#1e1e1e',
      success: '#81c784',
      warning: '#ffb74d',
      error: '#e57373',
      info: '#64b5f6',
      accent1: '#880e4f',
      accent2: '#ad1457',
      accent3: '#c2185b'
    },
  },
  orange: {
    light: { 
      primary: '#ef6c00', 
      secondary: '#03a9f4',
      background: '#fff3e0',
      paper: '#ffffff',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      info: '#2196f3',
      accent1: '#ffe0b2',
      accent2: '#ffb74d',
      accent3: '#ff9800'
    },
    dark: { 
      primary: '#ffb74d', 
      secondary: '#4fc3f7',
      background: '#121212',
      paper: '#1e1e1e',
      success: '#81c784',
      warning: '#ffb74d',
      error: '#e57373',
      info: '#64b5f6',
      accent1: '#e65100',
      accent2: '#ef6c00',
      accent3: '#f57c00'
    },
  },
  cyan: {
    light: { 
      primary: '#0097a7', 
      secondary: '#f50057',
      background: '#e0f7fa',
      paper: '#ffffff',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      info: '#2196f3',
      accent1: '#b2ebf2',
      accent2: '#4dd0e1',
      accent3: '#00bcd4'
    },
    dark: { 
      primary: '#4dd0e1', 
      secondary: '#f48fb1',
      background: '#121212',
      paper: '#1e1e1e',
      success: '#81c784',
      warning: '#ffb74d',
      error: '#e57373',
      info: '#64b5f6',
      accent1: '#006064',
      accent2: '#00838f',
      accent3: '#0097a7'
    },
  },
  deepPurple: {
    light: { 
      primary: '#512da8', 
      secondary: '#ff4081',
      background: '#ede7f6',
      paper: '#ffffff',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      info: '#2196f3',
      accent1: '#d1c4e9',
      accent2: '#9575cd',
      accent3: '#673ab7'
    },
    dark: { 
      primary: '#9575cd', 
      secondary: '#ff80ab',
      background: '#121212',
      paper: '#1e1e1e',
      success: '#81c784',
      warning: '#ffb74d',
      error: '#e57373',
      info: '#64b5f6',
      accent1: '#311b92',
      accent2: '#4527a0',
      accent3: '#512da8'
    },
  },
  lime: {
    light: { 
      primary: '#afb42b', 
      secondary: '#7e57c2',
      background: '#f9fbe7',
      paper: '#ffffff',
      success: '#4caf50',
      warning: '#ff9800',
      error: '#f44336',
      info: '#2196f3',
      accent1: '#f0f4c3',
      accent2: '#dce775',
      accent3: '#cddc39'
    },
    dark: { 
      primary: '#dce775', 
      secondary: '#b39ddb',
      background: '#121212',
      paper: '#1e1e1e',
      success: '#81c784',
      warning: '#ffb74d',
      error: '#e57373',
      info: '#64b5f6',
      accent1: '#827717',
      accent2: '#9e9d24',
      accent3: '#afb42b'
    },
  },
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Component to load Underdog font from Google Fonts
function UnderdogFontLoader() {
  useEffect(() => {
    // Add preconnect links
    const preconnectGoogle = document.createElement('link');
    preconnectGoogle.rel = 'preconnect';
    preconnectGoogle.href = 'https://fonts.googleapis.com';
    document.head.appendChild(preconnectGoogle);

    const preconnectGstatic = document.createElement('link');
    preconnectGstatic.rel = 'preconnect';
    preconnectGstatic.href = 'https://fonts.gstatic.com';
    preconnectGstatic.crossOrigin = 'anonymous';
    document.head.appendChild(preconnectGstatic);

    // Add font stylesheet
    const fontLink = document.createElement('link');
    fontLink.rel = 'stylesheet';
    fontLink.href = 'https://fonts.googleapis.com/css2?family=Underdog&display=swap';
    document.head.appendChild(fontLink);

    // Cleanup function
    return () => {
      document.head.removeChild(preconnectGoogle);
      document.head.removeChild(preconnectGstatic);
      document.head.removeChild(fontLink);
    };
  }, []);

  return null;
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>('light');
  const [color, setColor] = useState<ThemeColor>('blue');
  const [fontFamily, setFontFamily] = useState<FontFamily>('inter');

  useEffect(() => {
    try {
      const savedMode = localStorage.getItem('themeMode') as ThemeMode;
      const savedColor = localStorage.getItem('themeColor') as ThemeColor;
      const savedFont = localStorage.getItem('fontFamily') as FontFamily;
      
      if (savedMode && (savedMode === 'light' || savedMode === 'dark')) {
        setMode(savedMode);
      }
      
      if (savedColor && themeColors[savedColor] && Object.keys(themeColors).includes(savedColor)) {
        setColor(savedColor);
      }
      
      if (savedFont && ['inter', 'roboto', 'poppins', 'montserrat', 'opensans'].includes(savedFont)) {
        setFontFamily(savedFont);
      }
    } catch (error) {
      console.error('Error loading theme from localStorage:', error);
      // Reset to defaults if there's an error
      setMode('light');
      setColor('blue');
      setFontFamily('inter');
    }
  }, []);

  // Ensure we have valid values before creating the theme
  const safeMode = mode === 'light' || mode === 'dark' ? mode : 'light';
  const safeColor = themeColors[color] ? color : 'blue';
  const safeFontFamily = ['inter', 'roboto', 'poppins', 'montserrat', 'opensans', 'underdog'].includes(fontFamily) ? fontFamily : 'inter';
  
  // Font family mapping
  const fontFamilyMap = {
    inter: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    roboto: '"Roboto", "Helvetica", "Arial", sans-serif',
    poppins: '"Poppins", "Roboto", "Helvetica", "Arial", sans-serif',
    montserrat: '"Montserrat", "Roboto", "Helvetica", "Arial", sans-serif',
    opensans: '"Open Sans", "Roboto", "Helvetica", "Arial", sans-serif',
    underdog: '"Underdog", cursive'
  };

  const theme = createTheme({
    // Define breakpoints
    breakpoints: {
      values: {
        xs: 0,
        sm: 600,
        md: 960,
        lg: 1280,
        xl: 1920,
      },
    },
    // Define spacing unit (in px)
    spacing: 8,
    // Configure transitions
    transitions: {
      easing: {
        easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
        easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
        easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
        sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
      },
      duration: {
        shortest: 150,
        shorter: 200,
        short: 250,
        standard: 300,
        complex: 375,
        enteringScreen: 225,
        leavingScreen: 195,
      },
    },
    // Define zIndex values
    zIndex: {
      mobileStepper: 1000,
      speedDial: 1050,
      appBar: 1100,
      drawer: 1200,
      modal: 1300,
      snackbar: 1400,
      tooltip: 1500,
    },
    // Configure shadows
    shadows: [
      'none',
      '0 2px 4px rgba(0,0,0,0.05)',
      '0 4px 8px rgba(0,0,0,0.08)',
      '0 6px 12px rgba(0,0,0,0.1)',
      '0 8px 16px rgba(0,0,0,0.12)',
      '0 10px 20px rgba(0,0,0,0.14)',
      '0 12px 24px rgba(0,0,0,0.16)',
      '0 14px 28px rgba(0,0,0,0.18)',
      '0 16px 32px rgba(0,0,0,0.2)',
      '0 18px 36px rgba(0,0,0,0.22)',
      '0 20px 40px rgba(0,0,0,0.24)',
      '0 22px 44px rgba(0,0,0,0.26)',
      '0 24px 48px rgba(0,0,0,0.28)',
      '0 26px 52px rgba(0,0,0,0.3)',
      '0 28px 56px rgba(0,0,0,0.32)',
      '0 30px 60px rgba(0,0,0,0.34)',
      '0 32px 64px rgba(0,0,0,0.36)',
      '0 34px 68px rgba(0,0,0,0.38)',
      '0 36px 72px rgba(0,0,0,0.4)',
      '0 38px 76px rgba(0,0,0,0.42)',
      '0 40px 80px rgba(0,0,0,0.44)',
      '0 42px 84px rgba(0,0,0,0.46)',
      '0 44px 88px rgba(0,0,0,0.48)',
      '0 46px 92px rgba(0,0,0,0.5)',
      '0 48px 96px rgba(0,0,0,0.52)'
    ],
    palette: {
      mode: safeMode,
      primary: {
        main: themeColors[safeColor][safeMode].primary,
        light: themeColors[safeColor][safeMode].accent2,
        dark: themeColors[safeColor][safeMode].accent3,
      },
      secondary: {
        main: themeColors[safeColor][safeMode].secondary,
      },
      background: {
        default: themeColors[safeColor][safeMode].background,
        paper: themeColors[safeColor][safeMode].paper,
      },
      success: {
        main: themeColors[safeColor][safeMode].success,
      },
      warning: {
        main: themeColors[safeColor][safeMode].warning,
      },
      error: {
        main: themeColors[safeColor][safeMode].error,
      },
      info: {
        main: themeColors[safeColor][safeMode].info,
      },
      // Map custom accent colors to standard MUI palette keys
      grey: {
        50: safeMode === 'light' ? alpha(themeColors[safeColor][safeMode].accent1, 0.05) : alpha(themeColors[safeColor][safeMode].accent1, 0.15),
        100: safeMode === 'light' ? alpha(themeColors[safeColor][safeMode].accent1, 0.1) : alpha(themeColors[safeColor][safeMode].accent1, 0.2),
        200: safeMode === 'light' ? alpha(themeColors[safeColor][safeMode].accent1, 0.2) : alpha(themeColors[safeColor][safeMode].accent1, 0.3),
        300: safeMode === 'light' ? alpha(themeColors[safeColor][safeMode].accent1, 0.3) : alpha(themeColors[safeColor][safeMode].accent1, 0.4),
        400: safeMode === 'light' ? alpha(themeColors[safeColor][safeMode].accent1, 0.4) : alpha(themeColors[safeColor][safeMode].accent1, 0.5),
        500: safeMode === 'light' ? alpha(themeColors[safeColor][safeMode].accent1, 0.5) : alpha(themeColors[safeColor][safeMode].accent1, 0.6),
        600: safeMode === 'light' ? alpha(themeColors[safeColor][safeMode].accent1, 0.6) : alpha(themeColors[safeColor][safeMode].accent1, 0.7),
        700: safeMode === 'light' ? alpha(themeColors[safeColor][safeMode].accent1, 0.7) : alpha(themeColors[safeColor][safeMode].accent1, 0.8),
        800: safeMode === 'light' ? alpha(themeColors[safeColor][safeMode].accent1, 0.8) : alpha(themeColors[safeColor][safeMode].accent1, 0.9),
        900: safeMode === 'light' ? alpha(themeColors[safeColor][safeMode].accent1, 0.9) : alpha(themeColors[safeColor][safeMode].accent1, 1.0),
      },
      action: {
        hover: alpha(themeColors[safeColor][safeMode].accent2, 0.08),
        selected: alpha(themeColors[safeColor][safeMode].accent2, 0.16),
        disabled: alpha(themeColors[safeColor][safeMode].accent2, 0.3),
        disabledBackground: alpha(themeColors[safeColor][safeMode].accent2, 0.12),
        focus: alpha(themeColors[safeColor][safeMode].accent2, 0.12),
      },
      divider: safeMode === 'light' 
        ? alpha(themeColors[safeColor][safeMode].accent1, 0.12) 
        : alpha(themeColors[safeColor][safeMode].accent1, 0.2),
    } as any,
    components: {
      MuiAppBar: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            boxShadow: theme.palette.mode === 'light' 
              ? '0 2px 4px rgba(0,0,0,0.08)' 
              : '0 2px 4px rgba(0,0,0,0.15)',
            zIndex: theme.zIndex.appBar,
          }),
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: ({ theme }: { theme: Theme }) => ({
            backgroundImage: theme.palette.mode === 'light' 
              ? 'linear-gradient(rgba(255,255,255,0.05), rgba(255,255,255,0.05))' 
              : 'linear-gradient(rgba(0,0,0,0.15), rgba(0,0,0,0.15))',
            borderRadius: 0,
            boxShadow: theme.palette.mode === 'light'
              ? '0 0 10px rgba(0,0,0,0.05)'
              : '0 0 10px rgba(0,0,0,0.2)',
            transition: 'box-shadow 0.3s ease-in-out, width 0.3s ease-in-out',
          }),
        },
      },
      MuiCard: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            boxShadow: theme.palette.mode === 'light' 
              ? '0 2px 8px rgba(0,0,0,0.06)' 
              : '0 2px 8px rgba(0,0,0,0.2)',
            transition: 'box-shadow 0.3s ease-in-out',
            borderRadius: theme.shape.borderRadius,
            overflow: 'hidden',
            '&:hover': {
              boxShadow: theme.palette.mode === 'light' 
                ? '0 4px 12px rgba(0,0,0,0.1)' 
                : '0 4px 12px rgba(0,0,0,0.3)',
            },
          }),
        },
      },
      MuiButton: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            textTransform: 'none',
            borderRadius: theme.shape.borderRadius,
            transition: 'all 0.2s ease-in-out',
          }),
          contained: ({ theme }: { theme: Theme }) => ({
            boxShadow: 'none',
            '&:hover': {
              boxShadow: theme.shadows[2],
              transform: 'translateY(-1px)',
            },
          }),
          outlined: ({ theme }: { theme: Theme }) => ({
            '&:hover': {
              backgroundColor: alpha(theme.palette.primary.main, 0.04),
            },
          }),
        },
      },
      // Enhanced MuiDataGrid component overrides
      [`${gridClasses.root}`]: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            border: 'none',
            borderRadius: theme.shape.borderRadius,
            '&:focus': {
              outline: 'none',
            },
            '& .MuiDataGrid-main': {
              // Remove outline on focus
              '&:focus-within': {
                outline: 'none',
              },
            },
            // Customize scrollbars for better visibility
            '& ::-webkit-scrollbar': {
              width: '8px',
              height: '8px',
            },
            '& ::-webkit-scrollbar-track': {
              backgroundColor: theme.palette.mode === 'light' 
                ? alpha(theme.palette.grey[200], 0.5)
                : alpha(theme.palette.grey[900], 0.5),
              borderRadius: '4px',
            },
            '& ::-webkit-scrollbar-thumb': {
              backgroundColor: theme.palette.mode === 'light'
                ? theme.palette.grey[400]
                : theme.palette.grey[700],
              borderRadius: '4px',
              '&:hover': {
                backgroundColor: theme.palette.mode === 'light'
                  ? theme.palette.grey[600]
                  : theme.palette.grey[500],
              },
            },
          }),
          columnHeader: ({ theme }: { theme: Theme }) => ({
            backgroundColor: theme.palette.mode === 'light' 
              ? theme.palette.grey[50] 
              : theme.palette.grey[900],
            fontWeight: theme.typography.fontWeightMedium,
            fontSize: theme.typography.caption.fontSize,
            letterSpacing: '0.05em',
            padding: `${theme.spacing(1)} ${theme.spacing(2)}`,
            textTransform: 'uppercase',
            color: theme.palette.mode === 'light'
              ? theme.palette.grey[800]
              : theme.palette.grey[100],
            borderBottom: `1px solid ${
              theme.palette.mode === 'light'
                ? theme.palette.grey[300]
                : theme.palette.grey[700]
            }`,
            '&:focus': {
              outline: 'none',
            },
            '&:focus-within': {
              outline: 'none',
            },
            '& .MuiDataGrid-columnHeaderTitle': {
              fontWeight: theme.typography.fontWeightMedium,
            },
            '& .MuiDataGrid-columnSeparator': {
              color: theme.palette.mode === 'light'
                ? theme.palette.grey[200]
                : theme.palette.grey[700],
            },
            '& .MuiDataGrid-columnHeaderTitleContainer': {
              padding: `0 ${theme.spacing(1)}`,
            },
          }),
          cell: ({ theme }: { theme: Theme }) => ({
            padding: `${theme.spacing(0.5)} ${theme.spacing(1.25)}`,
            borderBottom: `1px solid ${
              theme.palette.mode === 'light'
                ? theme.palette.grey[200]
                : theme.palette.grey[800]
            }`,
            fontSize: theme.typography.body2.fontSize,
            '&:focus': {
              outline: 'none',
            },
            '&:focus-within': {
              outline: 'none',
            },
          }),
          row: ({ theme }: { theme: Theme }) => ({
            '&:hover': {
              backgroundColor: theme.palette.action.hover,
            },
            '&.Mui-selected': {
              backgroundColor: alpha(theme.palette.primary.main, 0.08),
              '&:hover': {
                backgroundColor: alpha(theme.palette.primary.main, 0.12),
              },
            },
          }),
          virtualScroller: ({ theme }: { theme: Theme }) => ({
            backgroundColor: theme.palette.background.paper,
          }),
          toolbarContainer: ({ theme }: { theme: Theme }) => ({
            padding: theme.spacing(2),
            backgroundColor: theme.palette.mode === 'light'
              ? alpha(theme.palette.primary.light, 0.05)
              : alpha(theme.palette.primary.dark, 0.1),
            borderTopLeftRadius: theme.shape.borderRadius,
            borderTopRightRadius: theme.shape.borderRadius,
            borderBottom: `1px solid ${
              theme.palette.mode === 'light'
                ? theme.palette.grey[200]
                : theme.palette.grey[800]
            }`,
          }),
          footerContainer: ({ theme }: { theme: Theme }) => ({
            borderTop: `1px solid ${
              theme.palette.mode === 'light'
                ? theme.palette.grey[200]
                : theme.palette.grey[800]
            }`,
            backgroundColor: theme.palette.mode === 'light'
              ? theme.palette.grey[50]
              : theme.palette.grey[900],
            borderBottomLeftRadius: theme.shape.borderRadius,
            borderBottomRightRadius: theme.shape.borderRadius,
            '& .MuiTablePagination-root': {
              color: theme.palette.text.secondary,
            },
            '& .MuiTablePagination-selectIcon': {
              color: theme.palette.text.secondary,
            },
          }),
          // Customize column menu
          panel: ({ theme }: { theme: Theme }) => ({
            backgroundColor: theme.palette.background.paper,
            borderRadius: theme.shape.borderRadius,
            boxShadow: theme.shadows[3],
          }),
          // Customize no rows overlay
          overlay: ({ theme }: { theme: Theme }) => ({
            backgroundColor: alpha(theme.palette.background.paper, 0.75),
            '& .MuiDataGrid-overlayContent': {
              color: theme.palette.text.secondary,
            },
          }),
          // Customize column headers
          columnHeaderCheckbox: ({ theme }: { theme: Theme }) => ({
            '& .MuiCheckbox-root': {
              padding: theme.spacing(0.5),
            },
          }),
          // Customize cell checkboxes
          cellCheckbox: ({ theme }: { theme: Theme }) => ({
            '& .MuiCheckbox-root': {
              padding: theme.spacing(0.5),
            },
          }),
        },
      },
      // Add MuiChip component overrides
      MuiChip: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            height: theme.spacing(4),
            borderRadius: theme.shape.borderRadiusLarge,
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              boxShadow: theme.palette.mode === 'light'
                ? '0 2px 4px rgba(0,0,0,0.1)'
                : '0 2px 4px rgba(0,0,0,0.2)',
            },
          }),
          label: ({ theme }: { theme: Theme }) => ({
            padding: `${theme.spacing(0.5)} ${theme.spacing(1.5)}`,
            fontSize: theme.typography.caption.fontSize,
          }),
          colorPrimary: ({ theme }: { theme: Theme }) => ({
            backgroundColor: alpha(theme.palette.primary.main, 0.1),
            color: theme.palette.primary.main,
          }),
          colorSecondary: ({ theme }: { theme: Theme }) => ({
            backgroundColor: alpha(theme.palette.secondary.main, 0.1),
            color: theme.palette.secondary.main,
          }),
          deleteIcon: ({ theme }: { theme: Theme }) => ({
            color: 'inherit',
            opacity: 0.7,
            '&:hover': {
              opacity: 1,
            },
          }),
        },
      },
      // Add MuiIconButton component overrides
      MuiIconButton: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            borderRadius: theme.shape.borderRadius,
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              backgroundColor: theme.palette.mode === 'light'
                ? alpha(theme.palette.primary.main, 0.04)
                : alpha(theme.palette.primary.main, 0.08),
            },
          }),
          colorPrimary: ({ theme }: { theme: Theme }) => ({
            '&:hover': {
              backgroundColor: alpha(theme.palette.primary.main, 0.1),
            },
          }),
        },
      },
      // Add MuiPopover component overrides
      MuiPopover: {
        styleOverrides: {
          paper: ({ theme }: { theme: Theme }) => ({
            boxShadow: theme.palette.mode === 'light'
              ? '0 2px 10px rgba(0,0,0,0.1)'
              : '0 2px 10px rgba(0,0,0,0.25)',
            borderRadius: theme.shape.borderRadius,
            overflow: 'hidden',
          }),
        },
      },
      // Add MuiTextField component overrides
      MuiTextField: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            marginBottom: theme.spacing(2),
            '& .MuiInputLabel-root': {
              fontSize: theme.typography.body2.fontSize,
              color: theme.palette.mode === 'dark'
                ? alpha(theme.palette.common.white, 0.7)
                : alpha(theme.palette.common.black, 0.7),
            },
            '& .MuiInputBase-input': {
              fontSize: theme.typography.body2.fontSize,
            },
            '& .MuiOutlinedInput-root': {
              // Empty state
              '& fieldset': {
                borderColor: theme.palette.mode === 'dark' 
                  ? alpha(theme.palette.common.white, 0.3) 
                  : alpha(theme.palette.common.black, 0.38), // Darker border in light mode
                borderWidth: 1,
              },
              // Hover state
              '&:hover fieldset': {
                borderColor: theme.palette.mode === 'dark' 
                  ? alpha(theme.palette.common.white, 0.5) 
                  : alpha(theme.palette.common.black, 0.55), // Darker hover border in light mode
              },
              // Focused state
              '&.Mui-focused fieldset': {
                borderColor: theme.palette.primary.main,
                borderWidth: 2,
              },
              // Filled state (when the field has a value)
              '&.Mui-filled fieldset': {
                borderColor: theme.palette.mode === 'dark'
                  ? alpha(theme.palette.common.white, 0.4)
                  : alpha(theme.palette.common.black, 0.45),
              },
              // Error state
              '&.Mui-error fieldset': {
                borderColor: theme.palette.error.main,
              },
              // Add box shadow on focus for better visual feedback
              // '&.Mui-focused': {
              //   boxShadow: `0 0 0 2px ${alpha(theme.palette.primary.main, 0.2)}`,
              // },
            },
          }),
        },
      },
      // Add MuiOutlinedInput component overrides
      MuiOutlinedInput: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            borderRadius: theme.shape.borderRadius,
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              borderColor: theme.palette.primary.main,
            },
            '&.Mui-focused': {
              boxShadow: `0 0 0 2px ${alpha(theme.palette.primary.main, 0.2)}`,
            },
            // Empty state
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: theme.palette.mode === 'dark'
                ? alpha(theme.palette.common.white, 0.3)
                : alpha(theme.palette.common.black, 0.38), // Darker in light mode
              borderWidth: 1,
            },
            // Hover state
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: theme.palette.mode === 'dark'
                ? alpha(theme.palette.common.white, 0.5)
                : alpha(theme.palette.common.black, 0.55), // Darker hover in light mode
            },
            // Focused state
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: theme.palette.primary.main,
              borderWidth: 2,
            },
            // Disabled state
            '&.Mui-disabled .MuiOutlinedInput-notchedOutline': {
              borderColor: theme.palette.mode === 'dark'
                ? alpha(theme.palette.common.white, 0.15)
                : alpha(theme.palette.common.black, 0.2),
            },
            // Error state
            '&.Mui-error .MuiOutlinedInput-notchedOutline': {
              borderColor: theme.palette.error.main,
            },
          }),
          notchedOutline: ({ theme }: { theme: Theme }) => ({
            transition: 'border-color 0.2s ease-in-out',
          }),
        },
      },
      // Add MuiSelect component overrides
      MuiSelect: {
        styleOverrides: {
          select: ({ theme }: { theme: Theme }) => ({
            fontSize: theme.typography.body2.fontSize,
            padding: `${theme.spacing(1.5)} ${theme.spacing(1.5)}`,
          }),
        },
      },
      // Add MuiMenuItem component overrides
      MuiMenuItem: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            fontSize: theme.typography.body2.fontSize,
            padding: `${theme.spacing(1)} ${theme.spacing(2)}`,
            '&:hover': {
              backgroundColor: theme.palette.action.hover,
            },
            '&.Mui-selected': {
              backgroundColor: alpha(theme.palette.primary.main, 0.08),
              '&:hover': {
                backgroundColor: alpha(theme.palette.primary.main, 0.12),
              },
            },
          }),
        },
      },
      // Add MuiDialog component overrides
      MuiDialog: {
        styleOverrides: {
          paper: ({ theme }: { theme: Theme }) => ({
            borderRadius: theme.shape.borderRadius,
            boxShadow: theme.shadows[4],
            '&.MuiDialog-paperFullScreen': {
              borderRadius: 0,
            },
          }),
        },
      },
      // Add MuiDialogTitle component overrides
      MuiDialogTitle: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            padding: theme.spacing(3),
            fontSize: theme.typography.h5.fontSize,
            fontWeight: theme.typography.h5.fontWeight,
          }),
        },
      },
      // Add MuiDialogContent component overrides
      MuiDialogContent: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            padding: theme.spacing(3),
          }),
        },
      },
      // Add MuiDialogActions component overrides
      MuiDialogActions: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            padding: theme.spacing(2, 3),
          }),
        },
      },
      // Add MuiAlert component overrides
      MuiAlert: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            borderRadius: theme.shape.borderRadius,
            padding: theme.spacing(1, 2),
          }),
          standardSuccess: ({ theme }: { theme: Theme }) => ({
            backgroundColor: alpha(theme.palette.success.main, 0.1),
            color: theme.palette.success.dark,
          }),
          standardInfo: ({ theme }: { theme: Theme }) => ({
            backgroundColor: alpha(theme.palette.info.main, 0.1),
            color: theme.palette.info.dark,
          }),
          standardWarning: ({ theme }: { theme: Theme }) => ({
            backgroundColor: alpha(theme.palette.warning.main, 0.1),
            color: theme.palette.warning.dark,
          }),
          standardError: ({ theme }: { theme: Theme }) => ({
            backgroundColor: alpha(theme.palette.error.main, 0.1),
            color: theme.palette.error.dark,
          }),
          message: ({ theme }: { theme: Theme }) => ({
            fontSize: theme.typography.body2.fontSize,
            padding: theme.spacing(0.5, 0),
          }),
          icon: ({ theme }: { theme: Theme }) => ({
            padding: theme.spacing(0.5, 0),
          }),
        },
      },
      // Add MuiSnackbar component overrides
      MuiSnackbar: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            zIndex: theme.zIndex.snackbar,
          }),
        },
      },
      // Add MuiTooltip component overrides
      MuiTooltip: {
        styleOverrides: {
          tooltip: ({ theme }: { theme: Theme }) => ({
            backgroundColor: theme.palette.mode === 'light'
              ? alpha(theme.palette.grey[800], 0.9)
              : alpha(theme.palette.grey[700], 0.9),
            borderRadius: theme.shape.borderRadius,
            fontSize: theme.typography.caption.fontSize,
            padding: theme.spacing(0.75, 1.5),
            maxWidth: 300,
          }),
          arrow: ({ theme }: { theme: Theme }) => ({
            color: theme.palette.mode === 'light'
              ? alpha(theme.palette.grey[800], 0.9)
              : alpha(theme.palette.grey[700], 0.9),
          }),
        },
      },
      // Add MuiDivider component overrides
      MuiDivider: {
        styleOverrides: {
          root: ({ theme }: { theme: Theme }) => ({
            borderColor: theme.palette.divider,
            margin: theme.spacing(2, 0),
          }),
        },
      },
    },
    shape: {
      borderRadius: 3, // Default border radius
      // Extended border radius values
      borderRadiusSmall: 2,
      borderRadiusMedium: 4,
      borderRadiusLarge: 8,
      borderRadiusExtraLarge: 12,
    } as any, // Type assertion needed for custom properties
    typography: {
      fontFamily: fontFamilyMap[safeFontFamily],
      // Comprehensive typography scale
      h1: {
        fontWeight: 700,
        fontSize: '2.5rem',  // 40px
        lineHeight: 1.2,
        letterSpacing: '-0.01562em',
        marginBottom: '0.5em',
      },
      h2: {
        fontWeight: 700,
        fontSize: '2rem',    // 32px
        lineHeight: 1.2,
        letterSpacing: '-0.00833em',
        marginBottom: '0.5em',
      },
      h3: {
        fontWeight: 600,
        fontSize: '1.75rem', // 28px
        lineHeight: 1.3,
        letterSpacing: '0em',
        marginBottom: '0.5em',
      },
      h4: {
        fontWeight: 600,
        fontSize: '1.5rem',  // 24px
        lineHeight: 1.35,
        letterSpacing: '0.00735em',
        marginBottom: '0.5em',
      },
      h5: {
        fontWeight: 600,
        fontSize: '1.25rem', // 20px
        lineHeight: 1.4,
        letterSpacing: '0em',
        marginBottom: '0.5em',
      },
      h6: {
        fontWeight: 600,
        fontSize: '1.125rem', // 18px
        lineHeight: 1.4,
        letterSpacing: '0.0075em',
        marginBottom: '0.5em',
      },
      subtitle1: {
        fontWeight: 500,
        fontSize: '1rem',    // 16px
        lineHeight: 1.5,
        letterSpacing: '0.00938em',
      },
      subtitle2: {
        fontWeight: 500,
        fontSize: '0.875rem', // 14px
        lineHeight: 1.5,
        letterSpacing: '0.00714em',
      },
      body1: {
        fontWeight: 400,
        fontSize: '1rem',    // 16px
        lineHeight: 1.5,
        letterSpacing: '0.00938em',
      },
      body2: {
        fontWeight: 400,
        fontSize: '0.875rem', // 14px
        lineHeight: 1.5,
        letterSpacing: '0.01071em',
      },
      button: {
        fontWeight: 500,
        fontSize: '0.875rem', // 14px
        lineHeight: 1.75,
        letterSpacing: '0.02857em',
        textTransform: 'none',
      },
      caption: {
        fontWeight: 400,
        fontSize: '0.75rem',  // 12px
        lineHeight: 1.5,
        letterSpacing: '0.03333em',
      },
      overline: {
        fontWeight: 500,
        fontSize: '0.75rem',  // 12px
        lineHeight: 1.5,
        letterSpacing: '0.08333em',
        textTransform: 'uppercase',
      },
    },
  });

  const toggleTheme = () => {
    const newMode = safeMode === 'light' ? 'dark' : 'light';
    setMode(newMode);
    localStorage.setItem('themeMode', newMode);
  };

  const changeThemeColor = (newColor: ThemeColor) => {
    setColor(newColor);
    localStorage.setItem('themeColor', newColor);
  };
  
  const changeFontFamily = (newFont: FontFamily) => {
    setFontFamily(newFont);
    localStorage.setItem('fontFamily', newFont);
  };

  // Apply responsive font sizes
  const responsiveTheme = responsiveFontSizes(theme, {
    breakpoints: ['xs', 'sm', 'md', 'lg', 'xl'],
    factor: 2, // Slightly more aggressive scaling
  });

  return (
    <ThemeContext.Provider value={{ mode: safeMode, color: safeColor, fontFamily: safeFontFamily, toggleTheme, changeThemeColor, changeFontFamily }}>
      <UnderdogFontLoader />
      <MuiThemeProvider theme={responsiveTheme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
}

export const useThemeContext = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useThemeContext must be used within a ThemeProvider');
  }
  return context;
};