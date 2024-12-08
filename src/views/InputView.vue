<script setup lang="ts">
import { ref } from "vue";
import axios from "axios";
import IconDeepPurple from "../components/icons/IconDeepPurple.vue";
import IconInput from "../components/icons/IconInput.vue";
import IconSettings from "../components/icons/IconSettings.vue";
import IconLogout from "../components/icons/IconLogout.vue";
import IconChevron from "../components/icons/IconChevron.vue";

const isSidebarCollapsed = ref(false); //pc sidebar toggle
const isMobileSidebarOpen = ref(false); //mobile fullscreen nav toggle
const inputText = ref("");

//init vals for emotions
const emotions = ref({
  joy: 0,
  sadness: 0,
  anger: 0,
  fear: 0,
  surprise: 0,
});
const isLoading = ref(false); //for when the api is loading

function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
}

function toggleMobileSidebar() {
  isMobileSidebarOpen.value = !isMobileSidebarOpen.value;
}

//main functionality here -- text analysis -- TO DO: should probably put this in a separate js file for better reusability among components
async function analyzeText() {

  //if nothing is in the textarea
  if (!inputText.value.trim()) {
    alert("Please enter some text to analyze.");
    return;
  }

  //starts tracking the loading
  isLoading.value = true;

  try {

    //obviously, replace the url after deployment
    const API_URL = "http://localhost:8000/analyze";
    const response = await axios.post(API_URL, {
      text: inputText.value,
    });

    //map the API response to the emotions object
    const result = response.data.predictions[0];
    emotions.value = result.reduce((acc: any, emotion: any) => {
      acc[emotion.label.toLowerCase()] = emotion.score * 100; // Convert to percentage
      return acc;
    }, {});
  } catch (error) {
    console.error("Error analyzing text:", error);
    alert("Failed to analyze text. Please try again later.");
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="flex min-h-screen bg-gray-900 text-gray-300">

    <!-- hamburger menu for mobile -->
    <button
      @click="toggleMobileSidebar"
      class="fixed top-4 left-4 z-50 bg-gray-800 text-gray-400 p-2 rounded-md hover:text-purple-400 md:hidden"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 6h16M4 12h16m-7 6h7"
        />
      </svg>
    </button>

    <!-- fullscreen mobile nav -->
    <div
      v-if="isMobileSidebarOpen"
      class="fixed inset-0 bg-gray-800 text-gray-300 z-50"
    >
      <div class="flex flex-col h-full">

        <!-- close button -->
        <button
          @click="toggleMobileSidebar"
          class="p-4 text-gray-400 hover:text-purple-400 self-end"
        >
          <IconChevron class="h-6 w-6"/>
        </button>

        <!-- links -->
        <nav class="flex-grow p-6 space-y-4">
          <a
            href="#"
            class="block p-4 bg-gray-700 rounded-md hover:bg-purple-600 hover:text-gray-100 transition"
          >
            <IconInput class="h-6 w-6 inline-block mr-2" />
            Direct Input
          </a>
          <a
            href="#"
            class="block p-4 bg-gray-700 rounded-md hover:bg-purple-600 hover:text-gray-100 transition"
          >
            <IconSettings class="h-6 w-6 inline-block mr-2" />
            Settings
          </a>
          <a
            href="#"
            class="block p-4 bg-gray-700 rounded-md hover:bg-purple-600 hover:text-gray-100 transition"
          >
            <IconLogout class="h-6 w-6 inline-block mr-2" />
            Logout
          </a>
        </nav>
      </div>
    </div>

    <!-- non-mobile nav -->
    <aside
      class="hidden md:block transition-all duration-300 ease-in-out bg-gray-800 text-gray-400"
      :class="isSidebarCollapsed ? 'w-16' : 'w-64'"
    >
      <div class="p-4 flex items-center justify-between">
        <IconDeepPurple v-if="!isSidebarCollapsed" class="h-8 w-8" />
        <button
          @click="toggleSidebar"
          class="text-gray-400 hover:text-purple-400"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="transition-transform h-6 w-6"
            :class="{ 'rotate-180': isSidebarCollapsed }"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
      </div>

      <nav class="flex-grow">
        <ul class="space-y-2">
          <li>
            <a
              href="#"
              class="flex items-center p-4 hover:bg-purple-600 hover:text-gray-100 transition whitespace-nowrap"
            >
              <IconInput class="h-6 w-6" />
              <span v-if="!isSidebarCollapsed" class="ml-4">Direct Input</span>
            </a>
          </li>
          <li>
            <a
              href="#"
              class="flex items-center p-4 hover:bg-purple-600 hover:text-gray-100 transition whitespace-nowrap"
            >
              <IconSettings class="h-6 w-6" />
              <span v-if="!isSidebarCollapsed" class="ml-4">Settings</span>
            </a>
          </li>
          <li>
            <a
              href="#"
              class="flex items-center p-4 hover:bg-purple-600 hover:text-gray-100 transition whitespace-nowrap"
            >
              <IconLogout class="h-6 w-6" />
              <span v-if="!isSidebarCollapsed" class="ml-4">Logout</span>
            </a>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- content here -->
    <main class="flex-1 p-6">
      <header class="flex justify-between items-center mb-6">
        <h2 class="text-3xl font-bold text-purple-300 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-300">
          Emotion Analyzer
        </h2>
      </header>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <!-- text input -->
        <div class="bg-gray-800 p-6 rounded-lg shadow-md">
          <textarea
            v-model="inputText"
            placeholder="Type your text here..."
            class="w-full h-48 p-4 bg-gray-700 text-gray-300 rounded-md resize-none"
          ></textarea>
          <button
            @click="analyzeText"
            :disabled="isLoading"
            class="mt-8 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-gray-100 shadow-md transition w-full"
          >
            <span v-if="!isLoading">Analyze Text</span>
            <span v-else>Loading...</span>
          </button>
        </div>

        <!-- analysis results ui -->
        <div class="bg-gray-800 p-6 rounded-lg shadow-md">
          <h3 class="text-xl font-semibold text-gray-200">Emotion Analysis</h3>
          <ul class="mt-4 space-y-4">
            <li v-for="(value, emotion) in emotions" :key="emotion" class="space-y-2">
              <div class="flex justify-between">
                <span class="capitalize">{{ emotion }}</span>
                <span>{{ value.toFixed(2) }}%</span>
              </div>
              <div class="h-3 w-full bg-gray-700 rounded-full">
                <div
                  :class="{
                    'bg-red-500': emotion === 'anger',
                    'bg-blue-500': emotion === 'sadness',
                    'bg-yellow-500': emotion === 'joy',
                    'bg-green-500': emotion === 'fear',
                    'bg-purple-500': emotion === 'surprise',
                  }"
                  class="h-full rounded-full transition-all duration-500 ease-out"
                  :style="{ width: value + '%' }"
                ></div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </main>
  </div>
</template>
