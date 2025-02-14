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
const showInputDetails = ref(false);
const expandedFileIndex = ref<number | null>(null);
const fileContents = ref<string[]>([]);
const dominantEmotion = ref<string>("");
const summary = ref<string>("");
const insights = ref<string>("");
const suggestedResponse = ref<string>("");
const showDownloadDropdown = ref(false);


const toggleDownloadDropdown = () => {
  showDownloadDropdown.value = !showDownloadDropdown.value;
};


function downloadCSV() {
  if (!emotionResult.value.length) {
    alert("No data available to download.");
    return;
  }

  // Prepare CSV content
  let csvContent = "data:text/csv;charset=utf-8,";


  if (fileContents.value.length > 0) {
    csvContent += `File Content\n"${fileContents.value.join("\n\n")}"\n\n`;
  } else {
    csvContent += `User Input\n"${userInput.value}"\n\n`;
  }


  csvContent += "Emotion,Score (%)\n";
  emotionResult.value.forEach(({ label, score }) => {
    csvContent += `${label},${(score * 100).toFixed(2)}\n`;
  });


  csvContent += `\nDominant Emotion,${dominantEmotion.value}\n`;
  csvContent += `Summary,"${summary.value}"\n`;
  csvContent += `Actionable Insights,"${insights.value}"\n`;
  csvContent += `Suggested Response,"${suggestedResponse.value}"\n`;


  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "emotion_analysis_results.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}




const readFilesContent = async () => {
  aggregatedFileContent.value = "";
  fileContents.value = [];

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
    aggregatedFileContent.value += content + "\n\n";
  }
};


const toggleFileContent = (index: number) => {
  expandedFileIndex.value = expandedFileIndex.value === index ? null : index;
};

const handleFileChange = (event: Event) => {
  const files = Array.from((event.target as HTMLInputElement).files || []);
  if (files.length > 0) {
    selectedFiles.value = files;
    fileNames.value = files.map((file) => file.name);
    userInput.value = "";
    readFilesContent();
  }
};

const analyzeFiles = async () => {
  if (userInput.value.trim()) {
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

    emotionResult.value = response.data.predictions;
    dominantEmotion.value = response.data.predicted_emotion;
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


const saveResultsAsPDF = async () => {
  const resultsElement = document.querySelector(".results-container") as HTMLElement;
  if (!resultsElement) {
    alert("Results section not found!");
    return;
  }

  try {
    const canvas = await html2canvas(resultsElement, {
      scale: 3,
      useCORS: true,
      scrollY: 0, // Prevent viewport cutting
    });

    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p", "mm", "a4");


    const imgWidth = 210;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;


    const pageHeight = 297;
    let position = 0;

    while (position < imgHeight) {
      pdf.addImage(imgData, "PNG", 0, position * -1, imgWidth, imgHeight);
      position += pageHeight;
      if (position < imgHeight) pdf.addPage();
    }

    pdf.save("emotion-analysis-results.pdf");
  } catch (error) {
    console.error("Error saving PDF:", error);
    alert("Failed to save the PDF. Please try again.");
  }
};



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


  <div class="max-w-2xl mx-auto">
    <div v-if="emotionResult.length > 0" class="mt-6 mb-4 bg-gray-800 p-4 rounded-lg shadow-md pie-chart-container">
      <div class="results-container p-4 rounded-md shadow-md">
        <h2 class="text-lg font-bold text-white">Emotion Results</h2>

        <Pie :data="pieData" :options="{ responsive: true, maintainAspectRatio: true }" style="height: 100px;" />

        <div class="text-white text-md mt-4">
          <h3 class="font-bold mb-2">Top 3 Emotions:</h3>
          <ul class="list-disc ml-5">
            <li v-for="(emotion, index) in topThreeEmotions" :key="index">
              {{ emotion.label }}: {{ (emotion.score * 100).toFixed(2) }}%
            </li>
          </ul>
        </div>

        <div class="bg-[#1e1b29] p-4 rounded-md mt-4">
          <h3 class="text-[1.25rem] font-bold text-[#a8a6b3] mb-4">Summary</h3>
          <p class="text-[#c3bdd7] text-[1.125rem]">
            <strong>Dominant Emotion:</strong> {{ dominantEmotion }}<br />
            {{ summary }}
          </p>
        </div>

        <div class="bg-[#1e1b29] p-4 rounded-md mt-4">
          <h3 class="text-[1.25rem] font-bold text-[#a8a6b3] mb-4">Actionable Insights</h3>
          <p class="text-[#c3bdd7] text-[1.125rem]">{{ insights }}</p>
        </div>

        <div class="bg-[#1e1b29] p-4 rounded-md mt-4">
          <h3 class="text-[1.25rem] font-bold text-[#a8a6b3] mb-4">Suggested Response</h3>
          <p class="text-[#c3bdd7] text-[1.125rem]">{{ suggestedResponse }}</p>
        </div>
      </div>

      <div class="flex justify-center gap-8 mt-4" style="min-height: 50px;">
        <button class="flex-1 bg-[#2ed573] text-white px-2 py-2 rounded-md hover:bg-[#27c56e] transition text-center"
          @click="showModal = true" :disabled="isSaveDisabled">
          Save Results
        </button>


        <div class="relative flex-1">
          <button class="w-full bg-blue-500 text-white px-4 py-4 rounded-md hover:bg-blue-600 transition text-center"
            @click="toggleDownloadDropdown">
            Download Results
          </button>


          <div v-if="showDownloadDropdown"
            class="absolute bottom-full mb-2 w-full bg-[#2b223c] py-4 text-white rounded-md shadow-lg z-10">
            <button @click="downloadCSV" class="block w-full px-4 py-4 text-left hover:bg-[#3d2f4a] transition">
              Download as CSV
            </button>
            <button @click="saveResultsAsPDF" class="block w-full px-4 py-4 text-left hover:bg-[#3d2f4a] transition">
              Download as PDF
            </button>

          </div>
        </div>

        <button class="flex-1 bg-gray-600 text-white px-2 py-2 rounded-md hover:bg-gray-700 transition text-center"
          @click="showInputDetails = !showInputDetails">
          {{ showInputDetails ? "Hide Input Details" : "Input Details" }}
        </button>
      </div>


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


      <div v-if="showInputDetails" class="mt-4 p-3 bg-gray-900 rounded-md text-white">
        <h3 class="text-lg font-bold mb-2">Input Details:</h3>
        <div v-if="userInput.trim()">
          <p class="whitespace-pre-wrap">{{ userInput }}</p>
        </div>
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
  </div>

  <form class="w-full max-w-md space-y-4" @submit.prevent="analyzeFiles">
    <div v-if="fileNames.length > 0" class="text-sm text-gray-400">
      Selected Files: <span class="font-medium text-gray-200">{{ fileNames.join(", ") }}</span>
    </div>

    <div class="flex items-center gap-2">
      <div class="relative flex-grow">
        <Input type="text" placeholder="Type your text or upload files..." class="w-full pr-16" v-model="userInput" />
        <button type="button"
          class="absolute right-2 top-1/2 transform -translate-y-1/2 text-white px-2 py-1 rounded-md hover:bg-gray-200 transition"
          @click="$refs.fileInput.click()">
          📎
        </button>
        <input type="file" id="fileInput" ref="fileInput" class="hidden" @change="handleFileChange" multiple />
      </div>

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
