import { createTheme } from '@mui/material/styles';

export const tokens = {
  bg: '#EEF3F2',
  surface: '#FFFFFF',
  surfaceAlt: '#F6F9F8',
  ink: '#12313A',
  muted: '#4F6B70',
  line: '#D3DFDD',
  lineStrong: '#768E91',
  primary: '#0F6E7A',
  primaryHover: '#0B5964',
  primarySoft: '#DDEEEF',
  have: '#24692A',
  haveSoft: '#E2F1E3',
  miss: '#8F4700',
  missSoft: '#FCEBD9',
  error: '#B3261E',
  errorSoft: '#FBE9E7',
};

export const categoryColors = {
  produce: { main: '#24622A', soft: '#DDF2D1' },
  dairy: { main: '#1D4F86', soft: '#DCEBFA' },
  protein: { main: '#9B2226', soft: '#FBDCDC' },
  grains: { main: '#7A5200', soft: '#F8E9C6' },
  canned: { main: '#5B3A8C', soft: '#E9E1F5' },
  condiments: { main: '#9A3C00', soft: '#FFE2CC' },
  baking: { main: '#5C4636', soft: '#EDE6DF' },
};

const sans = '"Figtree", system-ui, -apple-system, "Segoe UI", sans-serif';
const display = '"Bricolage Grotesque", "Figtree", system-ui, sans-serif';
const raised = '0 1px 2px rgba(18, 49, 58, 0.06), 0 6px 16px rgba(18, 49, 58, 0.08)';
const overlay = '0 12px 32px rgba(18, 49, 58, 0.16)';

const heading = (fontSize, lineHeight, letterSpacing) => ({
  fontFamily: display, fontWeight: 700, fontSize, lineHeight, letterSpacing, textWrap: 'balance',
});

const shadows = Array(25).fill(overlay);
shadows[0] = 'none';
shadows[1] = raised;
shadows[2] = raised;

const theme = createTheme({
  cssVariables: true,
  palette: {
    mode: 'light',
    primary: { main: tokens.primary, dark: tokens.primaryHover, light: tokens.primarySoft, contrastText: '#FFFFFF' },
    secondary: { main: tokens.ink, contrastText: '#FFFFFF' },
    success: { main: tokens.have, light: tokens.haveSoft, contrastText: '#FFFFFF' },
    warning: { main: tokens.miss, light: tokens.missSoft, contrastText: '#FFFFFF' },
    error: { main: tokens.error, light: tokens.errorSoft, contrastText: '#FFFFFF' },
    info: { main: tokens.primary, light: tokens.primarySoft, contrastText: '#FFFFFF' },
    text: { primary: tokens.ink, secondary: tokens.muted, disabled: '#8FA3A6' },
    background: { default: tokens.bg, paper: tokens.surface },
    divider: tokens.line,
    // css vars: --mui-palette-app-* and --mui-palette-cat-*-main|soft -Arun
    app: tokens,
    cat: categoryColors,
  },
  shape: { borderRadius: 12 },
  shadows,
  typography: {
    fontFamily: sans,
    htmlFontSize: 16,
    fontSize: 16,
    display: heading('clamp(2.25rem, 4.6vw, 3.75rem)', 1.05, '-0.025em'),
    h1: heading('2rem', 1.15, '-0.015em'),
    h2: heading('1.375rem', 1.25, '-0.01em'),
    h3: heading('1.125rem', 1.3, '-0.005em'),
    h4: { fontFamily: sans, fontWeight: 700, fontSize: '1rem', lineHeight: 1.4 },
    h5: { fontFamily: sans, fontWeight: 700, fontSize: '1rem', lineHeight: 1.4 },
    h6: { fontFamily: sans, fontWeight: 700, fontSize: '1rem', lineHeight: 1.4 },
    body1: { fontSize: '1rem', lineHeight: 1.6 },
    body2: { fontSize: '1rem', lineHeight: 1.6 },
    meta: { fontFamily: sans, fontSize: '0.875rem', fontWeight: 500, lineHeight: 1.4, color: tokens.muted, fontVariantNumeric: 'tabular-nums' },
    caption: { fontFamily: sans, fontSize: '0.8125rem', lineHeight: 1.4 },
    overline: { fontFamily: sans, fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.06em', lineHeight: 1.4 },
    button: { fontFamily: sans, fontWeight: 600, fontSize: '0.9375rem', letterSpacing: 0, textTransform: 'none' },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { backgroundColor: tokens.bg, color: tokens.ink, caretColor: tokens.primary },
        '::selection': { backgroundColor: tokens.primarySoft, color: tokens.ink },
        ':focus-visible': { outline: `2px solid ${tokens.primary}`, outlineOffset: 2 },
        '@media (prefers-reduced-motion: reduce)': {
          '*, *::before, *::after': { animationDuration: '0.01ms !important', transitionDuration: '0.01ms !important', scrollBehavior: 'auto !important' },
        },
      },
    },
    MuiTypography: {
      defaultProps: { variantMapping: { display: 'h1', meta: 'span' } },
    },
    MuiButtonBase: { defaultProps: { disableRipple: true } },
    MuiButton: {
      defaultProps: { disableElevation: true, variant: 'contained' },
      styleOverrides: {
        root: {
          minHeight: 44, borderRadius: 999, paddingInline: 22,
          transition: 'background-color 150ms ease-out, box-shadow 150ms ease-out, border-color 150ms ease-out',
        },
        sizeLarge: { minHeight: 52, fontSize: '1rem', paddingInline: 28 },
        contained: { '&:hover': { boxShadow: raised } },
        outlined: {
          borderColor: tokens.lineStrong, color: tokens.ink, backgroundColor: tokens.surface,
          '&:hover': { borderColor: tokens.primary, backgroundColor: tokens.surface },
        },
        text: { color: tokens.primary, '&:hover': { backgroundColor: tokens.primarySoft } },
      },
    },
    MuiIconButton: {
      styleOverrides: { root: { minWidth: 44, minHeight: 44, color: tokens.ink, '&:hover': { backgroundColor: tokens.primarySoft } } },
    },
    MuiCard: {
      defaultProps: { elevation: 1 },
      styleOverrides: { root: { borderRadius: 16, border: 'none' } },
    },
    MuiPaper: { styleOverrides: { rounded: { borderRadius: 16 } } },
    MuiMenu: { styleOverrides: { paper: { borderRadius: 12, border: `1px solid ${tokens.line}` } } },
    MuiDrawer: {
      styleOverrides: {
        paperAnchorBottom: { borderRadius: '20px 20px 0 0', paddingBottom: 'env(safe-area-inset-bottom, 0px)' },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 8, fontWeight: 600, height: 36 },
        outlined: { borderColor: tokens.lineStrong, color: tokens.ink },
        clickable: {
          position: 'relative',
          '&::after': { content: '""', position: 'absolute', inset: '-4px 0' },
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 12, backgroundColor: tokens.surface,
          '& .MuiOutlinedInput-notchedOutline': { borderColor: tokens.lineStrong },
          '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: tokens.ink },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: tokens.primary, borderWidth: 2 },
          '&.Mui-error .MuiOutlinedInput-notchedOutline': { borderColor: tokens.error },
        },
        input: { fontSize: '1rem' },
      },
    },
    MuiInputLabel: {
      styleOverrides: { root: { color: tokens.muted, '&.Mui-focused': { color: tokens.primary } } },
    },
    MuiFormHelperText: { styleOverrides: { root: { fontSize: '0.875rem', marginInline: 0 } } },
    MuiAlert: {
      styleOverrides: {
        root: { borderRadius: 12, alignItems: 'center' },
        standardInfo: { backgroundColor: tokens.primarySoft, color: tokens.ink, '& .MuiAlert-icon': { color: tokens.primary } },
        standardSuccess: { backgroundColor: tokens.haveSoft, color: tokens.ink, '& .MuiAlert-icon': { color: tokens.have } },
        standardWarning: { backgroundColor: tokens.missSoft, color: tokens.ink, '& .MuiAlert-icon': { color: tokens.miss } },
        standardError: { backgroundColor: tokens.errorSoft, color: tokens.ink, '& .MuiAlert-icon': { color: tokens.error } },
      },
    },
    MuiTooltip: {
      styleOverrides: { tooltip: { backgroundColor: tokens.ink, color: '#FFFFFF', fontSize: '0.8125rem', borderRadius: 8 } },
    },
    MuiAppBar: {
      defaultProps: { elevation: 0, color: 'inherit', position: 'sticky' },
      styleOverrides: { root: { backgroundColor: tokens.surface, borderBottom: `1px solid ${tokens.line}` } },
    },
    MuiTabs: { styleOverrides: { indicator: { height: 3, borderRadius: 3, backgroundColor: tokens.primary } } },
    MuiTab: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 600, fontSize: '0.9375rem', minHeight: 48, color: tokens.muted, '&.Mui-selected': { color: tokens.primary } },
      },
    },
    MuiBottomNavigation: {
      styleOverrides: { root: { height: 64, borderTop: `1px solid ${tokens.line}`, paddingBottom: 'env(safe-area-inset-bottom, 0px)', boxSizing: 'content-box' } },
    },
    MuiBottomNavigationAction: {
      styleOverrides: {
        root: { color: tokens.muted, '&.Mui-selected': { color: tokens.primary } },
        label: { fontSize: '0.75rem', fontWeight: 600, '&.Mui-selected': { fontSize: '0.75rem' } },
      },
    },
    MuiLink: {
      defaultProps: { underline: 'hover' },
      styleOverrides: { root: { color: tokens.primary, fontWeight: 600 } },
    },
    MuiSkeleton: { styleOverrides: { root: { backgroundColor: tokens.line } } },
    MuiCheckbox: { styleOverrides: { root: { color: tokens.lineStrong, '&.Mui-checked': { color: tokens.primary } } } },
  },
});

export default theme;
