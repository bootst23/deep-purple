<template>
    <div class="login-container">
      <div class="login-wrapper">
        <!-- Left Section: Sign-In Form -->
        <div class="login-form">
          <h1 class="title">Sign In</h1>
          <p class="subtitle">Keep it all together and you'll be fine</p>
          <form @submit.prevent="handleLogin">
            <div class="input-group">
              <input 
                type="text" 
                placeholder="Email or Phone" 
                v-model="email" 
                required
              />
            </div>
            <div class="input-group">
              <input 
                :type="showPassword ? 'text' : 'password'" 
                placeholder="Password" 
                v-model="password" 
                required
              />
              <button type="button" class="show-password" @click="togglePasswordVisibility">
                {{ showPassword ? 'Hide' : 'Show' }}
              </button>
            </div>
            <a href="#" class="forgot-password">Forgot Password?</a>
            <button @click="handleLogin" type="submit" class="submit-button">Sign In</button>
          </form>
        </div>
  
        <!-- Right Section: Welcome Message -->
        <div class="message-section">
          <h2 class="welcome-title">Welcome to <span class="highlight">Deep Purple</span></h2>
          <p class="welcome-message">
            Discover the power of our advanced sentiment analysis tool. 
            Our AI-driven platform helps you uncover hidden emotions 
            within the text with ease and precision.
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

  
  <style scoped>
  /* Container Styling */
  .login-container {
    font-family: 'Arial', sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background:#111827;
    color: #fff;
    padding: 1rem;
  }
  
  /* Wrapper Layout */
  .login-wrapper {
    display: flex;
    max-width: 900px;
    width: 100%;
    background: rgba(30, 21, 39, 0.95);
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.5);
  }
  
  @media (max-width: 768px) {
    .login-wrapper {
      flex-direction: column;
    }
  }
  
  /* Left Section: Login Form */
  .login-form {
    padding: 2rem;
    width: 100%;
    max-width: 400px;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .title {
    font-size: 2rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: #b399ff;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.6);
  }
  
  .subtitle {
    font-size: 1rem;
    color: #d4c8e3;
    margin-bottom: 1.5rem;
  }
  
  /* Input Styling */
  .input-group {
    position: relative;
    margin-bottom: 1.5rem;
  }
  
  input {
    width: 100%;
    padding: 0.8rem;
    border: 1px solid #27005a;
    border-radius: 8px;
    background: #2a004d;
    color: #fff;
    font-size: 1rem;
    box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.4);
  }
  
  input::placeholder {
    color: #a08bbf;
  }
  
  .show-password {
    position: absolute;
    top: 50%;
    right: 10px;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: #9a6eff;
    cursor: pointer;
  }
  
  .forgot-password {
    display: block;
    margin: 0.5rem 0;
    color: #9a6eff;
    text-decoration: none;
    font-size: 0.9rem;
    transition: color 0.3s ease;
  }
  
  .forgot-password:hover {
    color: #d4aaff;
  }
  
  /* Button Styling */
  .submit-button {
    width: 100%;
    padding: 0.8rem;
    background: linear-gradient(90deg, #6e00ff, #9a6eff);
    border: none;
    border-radius: 8px;
    color: #fff;
    font-size: 1rem;
    cursor: pointer;
    margin-top: 1rem;
    transition: transform 0.2s ease, box-shadow 0.3s ease;
  }
  
  .submit-button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 15px rgba(155, 110, 255, 0.5);
  }
  
  /* Right Section: Welcome Message */
  .message-section {
    padding: 2rem;
    width: 100%;
    max-width: 400px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
  }
  
  .welcome-title {
    font-size: 1.8rem;
    margin-bottom: 1rem;
  }
  
  .highlight {
    color: #cba3ff;
  }
  
  .welcome-message {
    font-size: 1rem;
    color: #d7c1e8;
    line-height: 1.6;
    background: linear-gradient(145deg, rgba(46, 0, 90, 0.8), rgba(36, 0, 70, 0.8));
    padding: 1rem;
    border-radius: 10px;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.5);
  }
  </style>
  