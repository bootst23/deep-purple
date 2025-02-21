<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 text-gray-200">
    <div class="w-full max-w-6xl bg-gray-800 rounded-lg shadow-2xl p-6 mt-14 space-y-8">
          <!-- Title and Description -->
          <div class="text-center mb-8">
            <!-- Smaller Title -->
            <h1 class="text-4xl font-bold text-white mb-2">
              Batch
              <span class="text-purple-300 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-300">
                Emotion Analysis
              </span>
            </h1>

            <!-- Description (closer to the title) -->
            <p class="text-md text-gray-300 max-w-2xl mx-auto">
              Upload multiple files at once to analyze emotions across your content.
            </p>
          </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- Drag and Drop Section -->
        <div
          class="border-2 border-dashed border-[#a692cc] bg-[#2b223c] rounded-lg flex flex-col items-center justify-center h-64 transition-all duration-300 hover:border-purple-400 hover:bg-[#3a2f4d]"
          @dragover="handleDragOver"
          @drop="handleDrop"
        >
          <div class="text-center space-y-2">
            <div class="text-5xl text-purple-400">+</div>
            <div class="text-sm text-gray-300">Drag and Drop File Here</div>
          </div>
          <input
            type="file"
            id="fileInput"
            ref="fileInput"
            class="hidden"
            @change="handleFileChange"
            multiple
          />
          <button
            class="mt-4 bg-[#8a4fff] text-white px-6 py-2 rounded-lg hover:bg-[#6f3bbd] transition-all duration-300 transform hover:scale-105"
            @click="$refs.fileInput.click()"
          >
            Browse
          </button>
        </div>

        <!-- File Content Section -->
        <div class="h-64">
          <h2 class="text-xl font-bold text-[#a8a6b3]">File Content</h2>
          <textarea
            class="w-full mt-2 p-4 bg-[#2b223c] rounded-lg text-[#c3bdd7] resize-none h-52 focus:outline-none focus:ring-2 focus:ring-purple-400"
            readonly
            v-model="aggregatedFileContent"
          ></textarea>
        </div>
      </div>

      <div class="flex flex-col mt-4">
        <div class="text-sm text-[#a8a6b3]">File Name: {{ fileNames.join(', ') }}</div>
        <button
          class="mt-4 bg-[#8a4fff] text-white px-6 py-2 rounded-lg hover:bg-[#6f3bbd] transition-all duration-300 transform hover:scale-105 w-full md:w-6/12 mx-auto"
          @click="analyzeFiles"
          :disabled="isLoading"
        >
          <span v-if="!isLoading">Analyze</span>
          <span v-else>Analyzing...</span>
        </button>
      </div>

      <!-- Emotion Results Section -->
      <div class="bg-[#2b223c] p-6 rounded-lg mt-8">
        <h2 class="text-xl font-bold text-[#a8a6b3]">Emotion Results</h2>

        <!-- Top Emotions and Pie Chart Section -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-6">
          <!-- Top Emotions Section -->
          <div class="space-y-6">
            <!-- Dominant Emotion Card -->
            <div
              v-if="dominantEmotion"
              class="bg-[#1e1b29] p-6 rounded-lg shadow-lg"
              :style="{ backgroundColor: emotionConfig[dominantEmotion as keyof typeof emotionConfig]?.color + '20' }"
            >
              <div class="flex items-center justify-center">
                <span class="text-5xl mr-4">
                  {{ emotionConfig[dominantEmotion as keyof typeof emotionConfig]?.emoji }}
                </span>
                <div>
                  <h3 class="text-3xl font-bold text-white">{{ dominantEmotion }}</h3>
                  <p class="text-xl text-gray-400">
                    {{ ((sortedEmotions[0]?.score ?? 0) * 100).toFixed(2) }}%
                  </p>
                </div>
              </div>
            </div>

            <!-- Related Emotions -->
            <div
              v-for="(emotion, index) in topThreeEmotions.slice(1)"
              :key="index"
              class="bg-[#1e1b29] p-4 rounded-lg shadow-md"
              :style="{ backgroundColor: emotionConfig[emotion.label as keyof typeof emotionConfig]?.color + '20' }"
            >
              <div class="flex items-center">
                <span class="text-3xl mr-2">
                  {{ emotionConfig[emotion.label as keyof typeof emotionConfig]?.emoji }}
                </span>
                <div>
                  <h3 class="text-xl font-bold text-white">{{ emotion.label }}</h3>
                  <p class="text-lg text-gray-400">{{ (emotion.score * 100).toFixed(2) }}%</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Pie Chart Section -->
          <div class="bg-[#1e1b29] p-6 rounded-lg shadow-lg flex flex-col items-center justify-center">
            <h4 class="text-xl font-bold text-[#a8a6b3] mb-6">Emotion Distribution</h4>
            <div><Pie :data="pieData" :options="{ responsive: true, maintainAspectRatio: false }" style="height: 300px; width: 300px;" /></div>
          </div>
        </div>

        <!-- Summary, Insights, and Suggested Response Section -->
        <div class="mt-8">
          <h3 class="text-xl font-bold text-[#a8a6b3] mb-6">Summary</h3>
          <div class="bg-[#1e1b29] p-6 rounded-lg shadow-md">
            <p class="text-[#c3bdd7]">
              <strong class="text-purple-300">Dominant Emotion:</strong> {{ dominantEmotion }}<br />
              {{ summary }}
            </p>
          </div>
        </div>

        <div class="mt-8">
          <h3 class="text-xl font-bold text-[#a8a6b3] mb-6">Actionable Insights</h3>
          <div class="bg-[#1e1b29] p-6 rounded-lg shadow-md">
            <ul class="list-disc pl-5 text-[#c3bdd7]">
              <li v-for="(insight, index) in insights" :key="index">{{ insight }}</li>
            </ul>
          </div>
        </div>

        <div class="mt-8">
          <h3 class="text-xl font-bold text-[#a8a6b3] mb-6">Suggested Response</h3>
          <div class="bg-[#1e1b29] p-6 rounded-lg shadow-md">
            <p class="text-[#c3bdd7]">{{ suggestedResponse }}</p>
          </div>
        </div>
      </div>

      <!-- Save Results Button -->
      <button
        class="w-full bg-[#2ed573] text-white px-6 py-3 rounded-lg hover:bg-[#27c56e] transition-all duration-300 transform hover:scale-105 mt-8"
        @click="showModal = true"
        :disabled="isSaveDisabled"
      >
        Save Results
      </button>

      <!-- Save Results Modal -->
      <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-[#1e1b29] p-8 rounded-lg shadow-2xl w-96">
          <h2 class="text-xl font-bold text-white mb-6">Name this Communication</h2>
          <input
            type="text"
            v-model="communicationName"
            placeholder="Enter a name..."
            class="w-full p-3 mb-6 border border-[#a692cc] rounded-lg bg-[#2b223c] text-[#c3bdd7] focus:outline-none focus:ring-2 focus:ring-purple-400"
          />
          <div class="flex justify-end space-x-4">
            <button
              class="bg-[#ff4c4c] text-white px-6 py-2 rounded-lg hover:bg-[#ff2a2a] transition-all duration-300 transform hover:scale-105"
              @click="showModal = false"
            >
              Cancel
            </button>
            <button
              class="bg-[#2ed573] text-white px-6 py-2 rounded-lg hover:bg-[#27c56e] transition-all duration-300 transform hover:scale-105"
              @click="saveResultToDB"
            >
              Save
            </button>
          </div>
        </div>
      </div>

      <!-- Custom Notification -->
      <div v-if="showNotification" class="fixed bottom-8 right-8 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-4">
        <span>Data saved successfully!</span>
        <button @click="showNotification = false" class="text-white hover:text-gray-200">×</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
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

// Imports for Extracting Text From PDF File
import * as pdfjsLib from "pdfjs-dist";
import { GlobalWorkerOptions } from "pdfjs-dist";
GlobalWorkerOptions.workerSrc = "/pdf.worker.min.mjs";

const emotionConfig = {
  Anger: { emoji: "😡", color: "#FF6384" },
  Disgust: { emoji: "🤢", color: "#8DD3C7" },
  Fear: { emoji: "😨", color: "#9966FF" },
  Joy: { emoji: "😊", color: "#FFCE56" },
  Neutral: { emoji: "😐", color: "#d3d3d3" },
  Sadness: { emoji: "😢", color: "#36A2EB" },
  Surprise: { emoji: "😲", color: "#ffa500" },
};

const sortedEmotions = computed(() => {
  return emotionResult.value
    .slice()
    .sort((a, b) => b.score - a.score);
});

const selectedFiles = ref<File[]>([]);
const aggregatedFileContent = ref<string>("");
const emotionResult = ref<{ label: string; score: number }[]>([]);
const dominantEmotion = ref<string>("");
const summary = ref("");
const insights = ref<string[]>([]);
const suggestedResponse = ref("");
const isLoading = ref(false);
const fileNames = ref<string[]>([]);
const isSaveDisabled = ref(true);
const communicationName = ref("");
const showModal = ref(false);
const showNotification = ref(false);

function handleFileChange(event: Event) {
  const files = Array.from((event.target as HTMLInputElement).files || []);
  if (files.length > 0) {
    selectedFiles.value = files;
    fileNames.value = files.map((file) => file.name);
    readFilesContent();
  } else {
    alert("No files selected.");
    selectedFiles.value = [];
    fileNames.value = [];
  }
}

function handleDragOver(event: DragEvent) {
  event.preventDefault();
  event.dataTransfer!.dropEffect = "copy";
}

function handleDrop(event: DragEvent) {
  event.preventDefault();
  const files = Array.from(event.dataTransfer?.files || []);
  if (files.length > 0) {
    selectedFiles.value = files;
    fileNames.value = files.map((file) => file.name);
    readFilesContent();
  }
}

async function readFilesContent() {
  aggregatedFileContent.value = "";

  for (const file of selectedFiles.value) {
    const content = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = () => reject(reader.error);

      if (file.type === "text/plain") {
        reader.readAsText(file);
      } else if (file.type === "application/pdf") {
        extractTextFromPDF(file).then(resolve).catch(reject);
      }
    });

    aggregatedFileContent.value += content + "\n \n";
  }
}

async function analyzeFiles() {
  if (selectedFiles.value.length === 0) {
    alert("Please select or drag files.");
    return;
  }

  const allowedTypes = ["text/plain", "application/pdf"];
  if (selectedFiles.value.some((file) => !allowedTypes.includes(file.type))) {
    alert("Only .txt and .pdf files are allowed.");
    return;
  }
  if (selectedFiles.value.some((file) => file.size > 5 * 1024 * 1024)) {
    alert("One or more files exceed the 5MB limit.");
    return;
  }

  isLoading.value = true;

  try {
    const endpoint = selectedFiles.value.length === 1 ? "/analyze" : "/analyze-batch";
    const ANALYZE_API_URL = `https://deep-purple-modelapi.onrender.com${endpoint}`;
    const payload = selectedFiles.value.length === 1 ? { text: aggregatedFileContent.value } : { texts: [aggregatedFileContent.value] };

    const response = await axios.post(ANALYZE_API_URL, payload, {
      headers: { "Content-Type": "application/json" },
    });

    emotionResult.value = response.data.predictions;
    dominantEmotion.value = response.data.predicted_emotion;
    summary.value = response.data.summary;
    insights.value = response.data.insights.split("\n");
    suggestedResponse.value = response.data.suggested_response;
    isSaveDisabled.value = false;
  } catch (error) {
    console.error("Error analyzing files:", error);
    alert("Failed to analyze the files. Please try again.");
  } finally {
    isLoading.value = false;
  }
}

async function saveResultToDB() {
  if (isSaveDisabled.value) {
    alert("Please analyze a file before saving the results.");
    return;
  }

  if (!communicationName.value) {
    alert("Please provide a name for this communication.");
    return;
  }
  const SAVE_API_URL = "https://deep-purple-databaseservice.onrender.com/save";
  try {
    await axios.post(SAVE_API_URL, {
      name: communicationName.value,
      file_name: fileNames.value.join(", "),
      content: aggregatedFileContent.value,
      input_type: "file",
      emotion_result: emotionResult.value,
      dominant_emotion: dominantEmotion.value,
      summary: summary.value,
      actionable_insights: insights.value.join("\n"),
      suggested_response: suggestedResponse.value,
    });
    console.log(emotionResult.value);
    showNotification.value = true;
    setTimeout(() => {
      showNotification.value = false;
    }, 3000);
    isSaveDisabled.value = true;
    showModal.value = false;
  } catch (error) {
    console.error("Error saving results:", error);
    alert("Failed to save results. Please try again.");
  }
}

async function extractTextFromPDF(file: File): Promise<string> {
  // Load the PDF document
  const pdf = await pdfjsLib.getDocument(URL.createObjectURL(file)).promise;

  let text = "";

  // Loop through each page and extract text
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();

    // Concatenate all text content from the page
    text += content.items
      .map((item) => ('str' in item ? item.str : ""))
      .join(" ");
  }

  return text;
}

const pieData = computed(() => {
  const labels = emotionResult.value.map((item) => item.label);
  const data = emotionResult.value.map((item) => Number((item.score * 100).toFixed(2)));
  const backgroundColor = [
    emotionConfig.Anger.color,
    emotionConfig.Disgust.color,
    emotionConfig.Fear.color,
    emotionConfig.Joy.color,
    emotionConfig.Neutral.color,
    emotionConfig.Sadness.color,
    emotionConfig.Surprise.color,
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
/* Add any custom styles here */
</style>