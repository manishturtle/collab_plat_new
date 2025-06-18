// Jest setup file
import '@testing-library/jest-dom';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
    pathname: '/',
    query: {},
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
}));

// Mock useMediaQuery hook
jest.mock('@mui/material/useMediaQuery', () => jest.fn(() => false));

// Mock i18next
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => key,
    i18n: {
      changeLanguage: jest.fn(),
    },
  }),
  initReactI18next: {
    type: '3rdParty',
    init: jest.fn(),
  },
}));

// Mock for CSS modules
jest.mock('*.module.css', () => ({}));
jest.mock('*.module.scss', () => ({}));

// Global beforeEach
beforeEach(() => {
  // Clear all mocks before each test
  jest.clearAllMocks();
});
