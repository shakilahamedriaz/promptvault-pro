import { useThemeStore } from '@/store/themeStore';

export function useTheme() {
  const { theme, setTheme, toggleTheme } = useThemeStore();

  return {
    theme,
    isDark: theme === 'dark',
    isLight: theme === 'light',
    setTheme,
    toggleTheme,
  };
}
