<template>
  <div class="min-h-screen flex items-center justify-center bg-[#1e1b29] text-white">
      <!-- Navigation Buttons -->
      <button
          class="absolute top-4 right-60 bg-[#8a4fff] text-white px-4 py-2 rounded-full hover:bg-[#6f3bbd] transition"
          @click="navigateToFileInput"
      >
          File Input Analyze
      </button>
      <button
          class="absolute top-4 right-10 bg-[#8a4fff] text-white px-4 py-2 rounded-full hover:bg-[#6f3bbd] transition"
          @click="navigateToDirectInput"
      >
          Direct Input Analyze
      </button>

    <div class="w-full max-w-6xl bg-[#1e1b29] rounded-lg shadow-md p-4 mt-14 space-y-6">
      <!-- Main Content -->
      <h1 class="text-4xl font-bold text-white mb-10 text-center">
        Text
        <span
          class="text-purple-300 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-300"
        >
          Emotion Analysis
        </span>
      </h1>

      <!-- Text Input Section -->
      <div>
        <h2 class="text-[1.125rem] font-bold text-[#a8a6b3] mb-4">Enter Text</h2>
        <textarea
          v-model="userText"
          class="w-full p-4 bg-[#2b223c] rounded-md text-[#c3bdd7] resize-none h-52"
          placeholder="Enter your text here..."
        ></textarea>
      </div>

      <div class="flex justify-end mt-4">
        <button
          class="bg-[#8a4fff] text-white px-4 py-2 rounded-md hover:bg-[#6f3bbd] transition"
          @click="analyzeText"
          :disabled="isLoading || !userText.trim()"
        >
          <span v-if="!isLoading">Analyze</span>
          <span v-else>Analyzing...</span>
        </button>
      </div>
      

      <div class="bg-[#2b223c] p-4 rounded-md mt-6">
          <h2 class="text-[1.125rem] font-bold text-[#a8a6b3]">Emotion Results</h2>

          <!-- Emotion Results Section -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
          <!-- Pie Chart Section -->
          <div class="bg-[#1e1b29] p-4 rounded-md flex justify-center">
              <Pie :data="pieData" :options="{ responsive: true, maintainAspectRatio: false }" style="height: 400px; width: 400px;" />
          </div>

          <!-- Top Emotions Section -->
          <div class="bg-[#1e1b29] p-6 rounded-md">
              <h3 class="text-[1.25rem] font-bold text-[#a8a6b3] mb-4">Top Emotions</h3>
              <ul class="list-disc pl-5 text-[#c3bdd7] text-[1.125rem]">
              <li v-for="emotion in topThreeEmotions" :key="emotion.label">
                  {{ emotion.label }}: {{ (emotion.score * 100).toFixed(2) }}%
              </li>
              </ul>
          </div>
          </div>
      </div>



      <!-- Save Results Button -->
      <button
        class="w-full bg-[#2ed573] text-white px-4 py-2 rounded-md hover:bg-[#27c56e] transition"
        @click="showModal = true"
        :disabled="isSaveDisabled"
      >
        Save Results
      </button>

      <!-- Save Results Modal -->
      <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-[#1e1b29] p-6 rounded-md shadow-md w-96">
          <h2 class="text-[1.125rem] font-bold text-white mb-4">Name this Communication</h2>
          <input
            type="text"
            v-model="communicationName"
            placeholder="Enter a name..."
            class="w-full p-2 mb-4 border border-[#a692cc] rounded-md bg-[#2b223c] text-[#c3bdd7]"
          />
          <div class="flex justify-end space-x-4">
            <button
              class="bg-[#ff4c4c] text-white px-4 py-2 rounded-md hover:bg-[#ff2a2a]"
              @click="showModal = false"
            >
              Cancel
            </button>
            <button
              class="bg-[#2ed573] text-white px-4 py-2 rounded-md hover:bg-[#27c56e]"
              @click="saveResultToDB"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { ref, computed } from "vue";
import axios from "axios";
import { Pie } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";

// Register chart components
ChartJS.register(Title, Tooltip, Legend, ArcElement);

const userText = ref<string>("");
const emotionResult = ref<{ label: string; score: number }[]>([]);
const isLoading = ref(false);
const isSaveDisabled = ref(true);
const communicationName = ref("");
const showModal = ref(false);
const router = useRouter();

function navigateToFileInput() {
router.push("/fileUpload");
}

function navigateToDirectInput() {
router.push("/directInput");
}

async function analyzeText() {
  if (!userText.value.trim()) {
    alert("Please enter some text to analyze.");
    return;
  }

  isLoading.value = true;

  try {
    const ANALYZE_API_URL = "https://deep-purple-modelapi.onrender.com/analyze";
    const response = await axios.post(ANALYZE_API_URL, { text: userText.value }, {
      headers: { "Content-Type": "application/json" },
    });

    emotionResult.value = response.data.predictions[0];
    isSaveDisabled.value = false;
  } catch (error) {
    console.error("Error analyzing text:", error);
    alert("Failed to analyze the text. Please try again.");
  } finally {
    isLoading.value = false;
  }
}

async function saveResultToDB() {
  if (!communicationName.value.trim()) {
    alert("Please provide a name for this communication.");
    return;
  }

  const SAVE_API_URL = "https://deep-purple-databaseservice.onrender.com/save";
  try {
    await axios.post(SAVE_API_URL, {
      name: communicationName.value,
      file_name: "NA",
      content: userText.value,
      input_type: "text",
      emotion_result: emotionResult.value,
    });
    alert("Results saved successfully.");
    isSaveDisabled.value = true;
    showModal.value = false;
  } catch (error) {
    console.error("Error saving results:", error);
    alert("Failed to save results. Please try again.");
  }
}

const pieData = computed(() => {
  const labels = emotionResult.value.map((item) => item.label);
  const data = emotionResult.value.map((item) => Number((item.score * 100).toFixed(2)));
  const backgroundColor = [
    "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40", "#8DD3C7",
  ];

  return {
    labels,
    datasets: [
      {
        data,
        backgroundColor,
      },
    ],
  };
});

const topThreeEmotions = computed(() => {
  return emotionResult.value
    .slice()
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);
});
</script>

<style scoped>
/* Add only unique styles here that Tailwind cannot handle */
</style>
