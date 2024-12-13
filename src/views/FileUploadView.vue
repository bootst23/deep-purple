<template>
  
  <div class="min-h-screen flex items-center justify-center bg-gray-900 text-gray-200">
    <div class="w-full max-w-6xl bg-gray-800 rounded-lg shadow-md p-4 mt-14 space-y-6">
      <h1 class="text-4xl  font-bold text-white mb-10 text-center">
      File
      <span
        class="text-purple-300 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-300"
      >
        Emotion Analysis
      </span>
     </h1>
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
            class="mt-4 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-500 transition"
            @click="$refs.fileInput.click()"
          >
            Browse
          </button>
        </div>

        <!-- File Content Section -->
        <div class="h-60">
          <h2 class="text-lg font-bold text-gray-300">File Content</h2>
          <textarea
            class="w-full mt-2 p-4 bg-gray-700 rounded-md text-gray-200 resize-none h-52"
            readonly
            v-model="fileContent"
          ></textarea>
        </div>
      </div>

      <div class="flex flex-col mt-2">
        <div class="text-sm text-gray-300">File Name: {{ fileName }}</div>
        <button
          class="mt-4 bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-500 transition w-6/12"
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

      <!-- Save Results Button -->
      <button
        class="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-500 transition"
        @click="showModal = true"
        :disabled="isSaveDisabled"
      >
        Save Results
      </button>

       <!-- Save Results Modal -->
       <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-gray-800 p-6 rounded-md shadow-md w-96">
          <h2 class="text-lg font-bold text-white mb-4">Name this Communication</h2>
          <input
            type="text"
            v-model="communicationName"
            placeholder="Enter a name..."
            class="w-full p-2 mb-4 border border-gray-700 rounded-md bg-gray-700 text-gray-200"
          />
          <div class="flex justify-end space-x-4">
            <button
              class="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-500"
              @click="showModal = false"
            >
              Cancel
            </button>
            <button
              class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-500"
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

//Imports for Extractiong Text From PDF File
import * as pdfjsLib from "pdfjs-dist";
import { GlobalWorkerOptions } from "pdfjs-dist";
GlobalWorkerOptions.workerSrc = "/node_modules/pdfjs-dist/build/pdf.worker.min.mjs";



const selectedFile = ref<File | null>(null);
const fileContent = ref<string>("");
const emotionResult = ref<{ label: string; score: number }[]>([]);
const isLoading = ref(false);
const fileName = ref("");
const isSaveDisabled = ref(true);
const communicationName = ref(""); 
const showModal = ref(false);

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

async function saveResultToDB() {
  if (isSaveDisabled.value) {
    alert("Please analyze a file before saving the results.");
    return;
  }

  if (!communicationName.value) {
    alert("Please provide a name for this communication.");
    return;
  }

  const SAVE_API_URL = "http://localhost:8001/save";
  try {
    await axios.post(SAVE_API_URL, {
      name: communicationName.value,
      file_name: fileName.value,
      content: fileContent.value,
      input_type: "file",
      emotion_result: emotionResult.value,
    });
    alert("Results saved successfully.");
    isSaveDisabled.value = true;
    showModal.value = false; // Close the modal after successful save
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
.min-h-screen {
  background-color: #1e1b29; 
  color: #ffffff; 
}

.bg-gray-700 {
  background-color: #2b223c; 
}

.bg-gray-800 {
  background-color: #1e1b29; 
}

.bg-gray-900 {
  background-color: #1e1b29; 
}

.text-gray-200 {
  color: #c3bdd7; 
}

.text-gray-300 {
  color: #a8a6b3; 
}

.bg-purple-600 {
  background-color: #8a4fff; 
}

.bg-purple-500 {
  background-color: #6f3bbd; 
}

.bg-green-600 {
  background-color: #2ed573; 
}

.bg-green-500 {
  background-color: #27c56e; 
}

.bg-red-600 {
  background-color: #ff4c4c; 
}

.bg-red-500 {
  background-color: #ff2a2a; 
}

.border-gray-500 {
  border-color: #a692cc; 
}

.text-gray-100 {
  color: #ffffff;
}

.text-lg {
  font-size: 1.125rem;
}

.text-xl {
  font-size: 1.25rem;
}

.text-2xl {
  font-size: 1.5rem;
}
</style>
