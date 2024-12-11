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

ChartJS.register(Title, Tooltip, Legend, ArcElement);

const selectedFile = ref<File | null>(null);
const fileContent = ref<string>("");
const emotionResult = ref<{ label: string; score: number }[]>([]);
const isLoading = ref(false);
const fileName = ref("");
const isSaveDisabled = ref(true);

function handleFileChange(event: Event) {
  const files = (event.target as HTMLInputElement).files;
  if (files && files.length > 0) {
    selectedFile.value = files[0];
    fileName.value = files[0].name;
    readFileContent();
  } else {
    alert("No file selected.");
    selectedFile.value = null;
    fileName.value = "";
  }
}

function handleDragOver(event: DragEvent) {
  event.preventDefault();
  event.dataTransfer!.dropEffect = "copy";
}

function handleDrop(event: DragEvent) {
  event.preventDefault();
  const files = event.dataTransfer?.files;
  if (files && files.length > 0) {
    selectedFile.value = files[0];
    fileName.value = files[0].name;
    readFileContent();
  }
}

async function readFileContent() {
  if (!selectedFile.value) return;

  const reader = new FileReader();

  fileContent.value = await new Promise<string>((resolve, reject) => {
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(reader.error);

    if (selectedFile.value?.type === "text/plain") {
      reader.readAsText(selectedFile.value);
    } else if (selectedFile.value?.type === "application/pdf") {
      extractTextFromPDF(selectedFile.value).then(resolve).catch(reject);
    }
  });
}

async function analyzeFile() {
  if (!selectedFile.value) {
    alert("Please select or drag a file.");
    return;
  }

  const allowedTypes = ["text/plain", "application/pdf"];
  if (!allowedTypes.includes(selectedFile.value.type)) {
    alert("Only .txt and .pdf files are allowed.");
    return;
  }
  if (selectedFile.value.size > 5 * 1024 * 1024) {
    alert("File size exceeds the 5MB limit.");
    return;
  }

  isLoading.value = true;

  try {
    const ANALYZE_API_URL = "http://localhost:8000/analyze";
    const response = await axios.post(ANALYZE_API_URL, { text: fileContent.value }, {
      headers: { "Content-Type": "application/json" },
    });

    emotionResult.value = response.data.predictions[0];
    isSaveDisabled.value = false;
  } catch (error) {
    console.error("Error analyzing file:", error);
    alert("Failed to analyze the file. Please try again.");
  } finally {
    isLoading.value = false;
  }
}

async function extractTextFromPDF(file: File): Promise<string> {
  const pdfjsLib = await import("pdfjs-dist");
  const pdf = await pdfjsLib.getDocument(URL.createObjectURL(file)).promise;
  let text = "";
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();

    text += content.items
      .map((item) => ('str' in item ? item.str : ""))
      .join(" ");
  }
  return text;
}

async function saveResultToDB() {
  if (isSaveDisabled.value) {
    alert("Please analyze a file before saving the results.");
    return;
  }

  const SAVE_API_URL = "http://localhost:8001/save";
  try {
    await axios.post(SAVE_API_URL, {
      file_name: fileName.value,
      emotion_result: emotionResult.value,
    });
    alert("Results saved successfully.");
    isSaveDisabled.value = true;
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

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 text-gray-200">
    <div class="w-full max-w-6xl bg-gray-800 rounded-lg shadow-md p-6 space-y-6">
      <h1 class="text-2xl font-bold text-center text-white">File Analysis</h1>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Drag and Drop Section -->
        <div
          class="border-2 border-dashed border-gray-500 bg-gray-700 rounded-md flex flex-col items-center justify-center h-60"
          @dragover="handleDragOver"
          @drop="handleDrop"
        >
          <div class="text-center space-y-2">
            <div class="text-4xl">+</div>
            <div class="text-sm">Drag and Drop File Here</div>
          </div>
          <input
            type="file"
            id="fileInput"
            ref="fileInput"
            class="hidden"
            @change="handleFileChange"
          />
          <button
            class="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 transition"
            @click="$refs.fileInput.click()"
          >
            Browse
          </button>
        </div>

        <!-- File Content Section -->
        <div class="h-60">
          <h2 class="text-lg font-bold text-gray-300">File Content</h2>
          <textarea
            class="w-full mt-2 p-4 bg-gray-700 rounded-md text-gray-200 resize-none h-40"
            readonly
            v-model="fileContent"
          ></textarea>
        </div>
      </div>

      <div class="flex flex-col items-center mt-4">
        <div class="text-sm text-gray-300">File Name: {{ fileName }}</div>
        <button
          class="mt-4 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-500 transition"
          @click="analyzeFile"
          :disabled="isLoading"
        >
          <span v-if="!isLoading">Analyze</span>
          <span v-else>Analyzing...</span>
        </button>
      </div>

      <div class="bg-gray-700 p-4 rounded-md mt-6">
        <h2 class="text-lg font-bold text-gray-300">Emotion Results</h2>

        <!-- Emotion Results Section -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
          <!-- Pie Chart Section -->
          <div class="bg-gray-800 p-4 rounded-md flex justify-center">
            <Pie :data="pieData" :options="{ responsive: true, maintainAspectRatio: false }" style="height: 400px; width: 400px;" />
          </div>

          <!-- Top Emotions Section -->
          <div class="bg-gray-800 p-6 rounded-md">
            <h3 class="text-xl font-bold text-gray-300 mb-4">Top Emotions</h3>
            <ul class="list-disc pl-5 text-gray-200 text-lg">
              <li v-for="emotion in topThreeEmotions" :key="emotion.label">
                {{ emotion.label }}: {{ (emotion.score * 100).toFixed(2) }}%
              </li>
            </ul>
          </div>
        </div>
      </div>

      <button
        class="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-500 transition"
        @click="saveResultToDB"
        :disabled="isSaveDisabled"
      >
        Save Results
      </button>
    </div>
  </div>
</template>
