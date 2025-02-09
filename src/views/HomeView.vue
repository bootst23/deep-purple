<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ref, computed } from "vue";
import axios from "axios";
import { Pie } from "vue-chartjs";
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from "chart.js";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

ChartJS.register(Title, Tooltip, Legend, ArcElement);

const userInput = ref("");
const selectedFiles = ref<File[]>([]);
const fileNames = ref<string[]>([]);
const aggregatedFileContent = ref("");
const emotionResult = ref<{ label: string; score: number }[]>([]);
const isLoading = ref(false);
const showModal = ref(false);
const communicationName = ref("");
const isSaveDisabled = ref(true);
const showInputDetails = ref(false); // Toggle input details section
const expandedFileIndex = ref<number | null>(null); // Track expanded file
const fileContents = ref<string[]>([]); // Store file contents
const dominantEmotion = ref<string>(""); // Holds the dominant emotion
const summary = ref<string>(""); // Holds the summary
const insights = ref<string>(""); // Holds actionable insights
const suggestedResponse = ref<string>(""); // Holds the suggested response

// Modify readFilesContent to store file contents for display
const readFilesContent = async () => {
  aggregatedFileContent.value = ""; // Reset content
  fileContents.value = []; // Reset file contents

  for (const file of selectedFiles.value) {
    const content = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = () => reject(reader.error);

      if (file.type === "text/plain") {
        reader.readAsText(file);
      } else {
        reject("Unsupported file type");
      }
    });

    fileContents.value.push(content);
    aggregatedFileContent.value += content + "\n\n"; // Append content
  }
};

// Toggle file content visibility
const toggleFileContent = (index: number) => {
  expandedFileIndex.value = expandedFileIndex.value === index ? null : index;
};

// Handle file change
const handleFileChange = (event: Event) => {
  const files = Array.from((event.target as HTMLInputElement).files || []);
  if (files.length > 0) {
    selectedFiles.value = files;
    fileNames.value = files.map((file) => file.name);
    userInput.value = ""; // Clear text input when a file is uploaded
    readFilesContent();
  }
};

// Analyze files or text input
const analyzeFiles = async () => {
  if (userInput.value.trim()) {
    // If the user inputs text, clear file-related data
    selectedFiles.value = [];
    fileNames.value = [];
    fileContents.value = [];
    aggregatedFileContent.value = "";

  }

  const textToAnalyze = userInput.value.trim() || aggregatedFileContent.value.trim();

  if (!textToAnalyze) {
    alert("Please provide input text or upload a file.");
    return;
  }

  isLoading.value = true;

  try {
    const response = await axios.post(
      "http://localhost:8000/analyze",
      { text: textToAnalyze },
      { headers: { "Content-Type": "application/json" } }
    );
    // Update results from the API response
    emotionResult.value = response.data.predictions;
    dominantEmotion.value = response.data.dominant_emotion;
    summary.value = response.data.summary;
    insights.value = response.data.insights;
    suggestedResponse.value = response.data.suggested_response;
    isSaveDisabled.value = false;
  } catch (error) {
    console.error("Error analyzing text:", error);
    alert("Failed to analyze the content. Please try again.");
  } finally {
    isLoading.value = false;
  }
};


// Save pie chart as PDF
const saveChartAsPDF = async () => {
  const chartElement = document.querySelector(".pie-chart-container") as HTMLElement; // Type assertion
  if (!chartElement) {
    alert("Pie chart not found!");
    return;
  }

  try {
    const canvas = await html2canvas(chartElement);
    const imgData = canvas.toDataURL("image/png");

    const pdf = new jsPDF();

    // Get canvas dimensions
    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;

    // Calculate aspect ratio for the PDF page
    const pdfWidth = 190; // Adjust based on PDF width
    const pdfHeight = (canvasHeight * pdfWidth) / canvasWidth; // Maintain aspect ratio

    pdf.text("Emotion Analysis Results", 10, 10);
    pdf.addImage(imgData, "PNG", 10, 20, pdfWidth, pdfHeight); // Use dynamic dimensions
    pdf.save("emotion-analysis-results.pdf");
  } catch (error) {
    console.error("Error saving PDF:", error);
    alert("Failed to save the PDF. Please try again.");
  }
};


// Pie chart data
const pieData = computed(() => ({
  labels: emotionResult.value.map((item) => item.label),
  datasets: [
    {
      data: emotionResult.value.map((item) => item.score * 100),
      backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"],
    },
  ],
}));

const topThreeEmotions = computed(() =>
  emotionResult.value
    .slice()
    .sort((a, b) => b.score - a.score)
    .slice(0, 3)
);

async function saveResultToDB() {
  if (!communicationName.value.trim()) {
    alert("Please provide a name for this communication.");
    return;
  }

  const SAVE_API_URL = "http://localhost:8080/save";
  try {
    await axios.post(SAVE_API_URL, {
      name: communicationName.value,
      file_name: "NA",
      content: userInput.value,
      input_type: "text",
      emotion_result: emotionResult.value,
      dominant_emotion: dominantEmotion.value,
      summary: summary.value,
      actionable_insights: insights.value,
      suggested_response: suggestedResponse.value,
    });
    alert("Results saved successfully.");
    isSaveDisabled.value = true;
    showModal.value = false;
  } catch (error) {
    console.error("Error saving results:", error);
    alert("Failed to save results. Please try again.");
  }
}


</script>

<template>
  <h1 class="text-4xl md:text-6xl font-bold text-white mb-2 text-center">
    Welcome to
    <span class="text-purple-300 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-300">
      DeepPurple
    </span>
  </h1>
  <p class="text-xl text-purple-200 mb-8 text-center max-w-2xl">
    Your Emotional Detection AI
  </p>

  <!-- Results Section -->
  <div v-if="emotionResult.length > 0" class="mt-6 mb-4 bg-gray-800 p-4 rounded-lg shadow-md pie-chart-container">
    <h2 class="text-lg font-bold text-white">Emotion Results</h2>

    <!-- Pie Chart -->
    <Pie :data="pieData" :options="{ responsive: true, maintainAspectRatio: true }" style="height: 300px;" />

    <!-- Summary Section -->
    <div class="text-white text-md mt-4">
      <h3 class="font-bold mb-2">Top 3 Emotions:</h3>
      <ul class="list-disc ml-5">
        <li v-for="(emotion, index) in topThreeEmotions" :key="index">
          {{ emotion.label }}: {{ (emotion.score * 100).toFixed(2) }}%
        </li>
      </ul>
    </div>

    <!-- Summary Section -->
    <div class="bg-[#1e1b29] p-6 rounded-md mt-6">
      <h3 class="text-[1.25rem] font-bold text-[#a8a6b3] mb-4">Summary</h3>
      <p class="text-[#c3bdd7] text-[1.125rem]">
        <strong>Dominant Emotion:</strong> {{ dominantEmotion }}<br />
        {{ summary }}
      </p>
    </div>

    <!-- Insights Section -->
    <div class="bg-[#1e1b29] p-6 rounded-md mt-6">
      <h3 class="text-[1.25rem] font-bold text-[#a8a6b3] mb-4">Actionable Insights</h3>
      <p class="text-[#c3bdd7] text-[1.125rem]">{{ insights }}</p>
    </div>

    <!-- Suggested Response Section -->
    <div class="bg-[#1e1b29] p-6 rounded-md mt-6">
      <h3 class="text-[1.25rem] font-bold text-[#a8a6b3] mb-4">Suggested Response</h3>
      <p class="text-[#c3bdd7] text-[1.125rem]">{{ suggestedResponse }}</p>
    </div>

    <div class="flex justify-center gap-8 mt-4 m-4" style="min-height: 50px;">
      <!-- Save Results Button -->
      <button class="flex-1 bg-[#2ed573] text-white px-2 py-2 rounded-md hover:bg-[#27c56e] transition text-center"
        @click="showModal = true" :disabled="isSaveDisabled">
        Save Results
      </button>

      <!-- Save Chart as PDF Button -->
      <button class="flex-1 bg-blue-500 text-white px-2 py-2 rounded-md hover:bg-blue-600 text-center"
        @click="saveChartAsPDF">
        Save as PDF
      </button>

      <!-- Input Details Button -->
      <button class="flex-1 bg-gray-600 text-white px-2 py-2 rounded-md hover:bg-gray-700 transition text-center"
        @click="showInputDetails = !showInputDetails">
        {{ showInputDetails ? "Hide Input Details" : "Input Details" }}
      </button>
    </div>



    <!-- Save Results Modal -->
    <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-[#1e1b29] p-6 rounded-md shadow-md w-96">
        <h2 class="text-[1.125rem] font-bold text-white mb-4">Name this Communication</h2>
        <input type="text" v-model="communicationName" placeholder="Enter a name..."
          class="w-full p-2 mb-4 border border-[#a692cc] rounded-md bg-[#2b223c] text-[#c3bdd7]" />
        <div class="flex justify-end space-x-4">
          <button class="bg-[#ff4c4c] text-white px-4 py-2 rounded-md hover:bg-[#ff2a2a]" @click="showModal = false">
            Cancel
          </button>
          <button class="bg-[#2ed573] text-white px-4 py-2 rounded-md hover:bg-[#27c56e]" @click="saveResultToDB">
            Save
          </button>
        </div>
      </div>
    </div>

    <!-- Text Input or File List -->
    <div v-if="showInputDetails" class="mt-4 p-3 bg-gray-900 rounded-md text-white">
      <h3 class="text-lg font-bold mb-2">Input Details:</h3>

      <!-- Show Text Input if Manually Entered -->
      <div v-if="userInput.trim()">
        <p class="whitespace-pre-wrap">{{ userInput }}</p>
      </div>

      <!-- Show File List if Files Were Uploaded -->
      <div v-else-if="fileNames.length > 0">
        <ul>
          <li v-for="(file, index) in fileNames" :key="index">
            <button @click="toggleFileContent(index)" class="text-blue-400 hover:underline">
              {{ file }}
            </button>
            <p v-if="expandedFileIndex === index" class="mt-2 p-2 bg-gray-700 rounded-md">
              {{ fileContents[index] }}
            </p>
          </li>
        </ul>
      </div>
    </div>
  </div>



  <form class="w-full max-w-md space-y-4" @submit.prevent="analyzeFiles">
    <!-- File Names Display -->
    <div v-if="fileNames.length > 0" class="text-sm text-gray-400">
      Selected Files: <span class="font-medium text-gray-200">{{ fileNames.join(", ") }}</span>
    </div>

    <div class="flex items-center gap-2">
      <!-- Input Text -->
      <div class="relative flex-grow">
        <Input type="text" placeholder="Type your text or upload files..." class="w-full pr-16" v-model="userInput" />
        <!-- File Button -->
        <button type="button"
          class="absolute right-2 top-1/2 transform -translate-y-1/2 text-white px-2 py-1 rounded-md hover:bg-gray-200 transition"
          @click="$refs.fileInput.click()">
          📎
        </button>
        <!-- Hidden File Input -->
        <input type="file" id="fileInput" ref="fileInput" class="hidden" @change="handleFileChange" multiple />
      </div>

      <!-- Analyze Button -->
      <Button type="submit" variant="secondary"
        class="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-md flex items-center justify-center"
        :disabled="isLoading">
        <span v-if="!isLoading">Analyze</span>
        <span v-else>
          <svg class="animate-spin h-5 w-5 text-white ml-2 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none"
            viewBox="0 0 24 24">
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
          </svg>
        </span>
      </Button>

    </div>
  </form>
</template>
