<script setup lang="ts">
import { ref } from "vue";
import axios from "axios";

const selectedFile = ref<File | null>(null); // Store the uploaded file
const emotionResult = ref(""); // Store the emotion analysis result
const isLoading = ref(false); // Loading state

// Handle file selection
function handleFileChange(event: Event) {
  const files = (event.target as HTMLInputElement).files;
  if (files && files.length > 0) {
    selectedFile.value = files[0];
  } else {
    alert("No file selected.");
    selectedFile.value = null;
  }
}

// Handle drag-and-drop
function handleDragOver(event: DragEvent) {
  event.preventDefault();
  event.dataTransfer!.dropEffect = "copy";
}

function handleDrop(event: DragEvent) {
  event.preventDefault();
  const files = event.dataTransfer?.files;
  if (files && files.length > 0) {
    selectedFile.value = files[0];
  }
}

// Analyze the file
async function analyzeFile() {
  if (!selectedFile.value) {
    alert("Please select or drag a file.");
    return;
  }

  isLoading.value = true;
  try {
    const formData = new FormData();
    formData.append("file", selectedFile.value);

    const API_URL = "http://localhost:8000/analyze"; 
    const response = await axios.post(API_URL, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    emotionResult.value = response.data.result || "No result found.";
  } catch (error) {
    console.error("Error analyzing file:", error);
    emotionResult.value = "Failed to analyze the file. Please try again.";
  } finally {
    isLoading.value = false;
  }
}

// Save the result
function saveResult() {
  if (!emotionResult.value) {
    alert("No emotion result to save.");
    return;
  }

  const blob = new Blob([emotionResult.value], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "emotion_analysis_result.txt";
  link.click();
  URL.revokeObjectURL(url);
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 text-gray-200">
    <div class="w-full max-w-4xl bg-gray-800 rounded-lg shadow-md p-6 space-y-6">
      <!-- Header -->
      <h1 class="text-2xl font-bold text-center text-white">File Analysis</h1>

      <!-- File Upload Section -->
      <div class="flex flex-col md:flex-row gap-6">
        <!-- Drag and Drop Area -->
        <div
          class="flex-1 border-2 border-dashed border-gray-500 bg-gray-700 rounded-md flex flex-col items-center justify-center h-48 cursor-pointer"
          @dragover="handleDragOver"
          @drop="handleDrop"
        >
          <div class="text-center space-y-2">
            <div class="text-4xl">+</div>
            <div class="text-sm">Drag and Drop File Here</div>
          </div>
          <button
            class="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-500 transition"
            @click="$refs.fileInput.click()"
          >
            Browse
          </button>
          <input
            type="file"
            id="fileInput"
            ref="fileInput"
            class="hidden"
            @change="handleFileChange"
          />
        </div>

        <!-- Analyze Button -->
        <div class="flex-1 flex flex-col justify-between">
          <button
            class="w-full bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-500 transition"
            @click="analyzeFile"
            :disabled="isLoading"
          >
            <span v-if="!isLoading">Analyze</span>
            <span v-else>Analyzing...</span>
          </button>
        </div>
      </div>

      <!-- Emotion Result -->
      <div>
        <h2 class="text-lg font-bold text-gray-300">Emotion Result</h2>
        <textarea
          class="w-full mt-2 p-4 bg-gray-700 rounded-md text-gray-200 resize-none h-40"
          readonly
          v-model="emotionResult"
        ></textarea>
      </div>

      <!-- Save Button -->
      <div class="flex justify-end">
        <button
          class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-500 transition"
          @click="saveResult"
        >
          Save
        </button>
      </div>
    </div>
  </div>
</template>