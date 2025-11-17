/**
 * LocalStorage kezelő utility
 * JWT token és user adatok perzisztens tárolása
 */

const TOKEN_KEY = 'pos_auth_token';
const USER_KEY = 'pos_user';

export const storage = {
  // Token műveletek
  getToken: (): string | null => {
    return localStorage.getItem(TOKEN_KEY);
  },

  setToken: (token: string): void => {
    localStorage.setItem(TOKEN_KEY, token);
  },

  removeToken: (): void => {
    localStorage.removeItem(TOKEN_KEY);
  },

  // User műveletek
  getUser: (): any | null => {
    const userJson = localStorage.getItem(USER_KEY);
    return userJson ? JSON.parse(userJson) : null;
  },

  setUser: (user: any): void => {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  removeUser: (): void => {
    localStorage.removeItem(USER_KEY);
  },

  // Teljes kijelentkezés (mindkettő törlése)
  clear: (): void => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};
