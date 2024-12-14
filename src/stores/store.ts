import { defineStore } from 'pinia';

// Declare types for your state
export interface User {
  id: string;
  name: string;
  email: string;
}

export const useStore = defineStore('main', {
  state: () => ({
    token: null as string | null,
    user: null as User | null,
  }),
  actions: {
    setToken(token: string) {
      this.token = token;
    },
    setUser(user: User) {
      this.user = user;
    },
  },
  persist: true,  // For persistence, if you want to use this
});
