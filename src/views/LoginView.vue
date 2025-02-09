<template>
  <div class="flex justify-center items-center min-h-screen bg-[#111827] text-white p-4">
    <div class="flex flex-col md:flex-row max-w-4xl w-full bg-[rgba(30,21,39,0.95)] rounded-lg overflow-hidden shadow-xl">
      <!-- Left Section: Sign-In Form -->
      <div class="p-8 w-full max-w-md border-r border-white/10">
        <h1 class="text-2xl font-bold mb-2 text-[#b399ff] shadow-md">Sign In</h1>
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div class="relative mb-4">
            <input
              type="text"
              class="w-full p-3 bg-[#2a004d] text-white text-base border border-[#27005a] rounded-lg placeholder-[#a08bbf] shadow-inner"
              placeholder="Email or Phone"
              v-model="email"
              required
            />
          </div>
          <div class="relative mb-4">
            <input
              :type="showPassword ? 'text' : 'password'"
              class="w-full p-3 bg-[#2a004d] text-white text-base border border-[#27005a] rounded-lg placeholder-[#a08bbf] shadow-inner"
              placeholder="Password"
              v-model="password"
              required
            />
            <button
              type="button"
              class="absolute top-1/2 right-3 text-[#9a6eff] -translate-y-1/2"
              @click="togglePasswordVisibility"
            >
              {{ showPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
          <a href="#" class="text-sm text-[#9a6eff] hover:text-[#d4aaff] transition">Forgot Password?</a>
          <button
            @click="handleLogin"
            type="submit"
            class="w-full p-3 bg-gradient-to-r from-[#6e00ff] to-[#9a6eff] text-white text-base font-medium rounded-lg shadow-md hover:scale-105 hover:shadow-lg transition"
          >
            Sign In
          </button>
        </form>
      </div>

      <!-- Right Section: Welcome Message -->
      <div class="p-8 w-full max-w-md flex flex-col justify-center text-center">
        <h2 class="text-xl mb-4">
          Welcome to <span class="text-[#cba3ff]">Deep Purple</span>
        </h2>
        <p class="text-base leading-relaxed bg-gradient-to-br from-[#2e005a]/80 to-[#240046]/80 p-4 rounded-lg shadow-inner">
          Discover the power of our advanced sentiment analysis tool. Our AI-driven platform helps you uncover hidden emotions within the text with ease and precision.
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { useStore } from '@/stores/store'; // Import Pinia store
import AuthenticationService from '@/services/AuthenticationService.js';

export default {
  data() {
    return {
      email: '',
      password: '',
      showPassword: false,
      error: null as string | null,
    };
  },
  setup() {
    const store = useStore(); // Access the Pinia store
    return { store }; // Return it so it's accessible in the template and methods
  },
  methods: {
    togglePasswordVisibility() {
      this.showPassword = !this.showPassword;
    },
    async handleLogin() {
      try {
        const response = await AuthenticationService.login({
          email: this.email,
          password: this.password,
          profile: "customerAgent",
        });
        // Use Pinia store actions
        this.store.setToken(response.token);
        this.store.setUser(response.user);
      } catch (error) {
        console.log(error);
        this.error = 'Failed to login. Please try again.'; // Display an error if needed
      }
    },
  },
};
</script>
