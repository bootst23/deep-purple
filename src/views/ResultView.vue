<template>
  <div class="min-h-screen bg-[#1e1b29] text-white p-8" v-if="result">
    <header class="text-center mb-8">
      <h1 class="text-2xl font-bold text-[#d3bafc]">{{ result.name }}</h1>
      <p class="text-[#a8a6b3]">Emotion Analysis Result</p>
    </header>

    <!-- Text Content Section -->
    <div
      class="bg-[#2b223c] rounded-lg p-5 mb-5 max-h-[300px] overflow-y-auto overflow-x-hidden whitespace-pre-wrap break-words">
      <h3 class="mb-2 text-[#d3bafc]">Text Content</h3>
      <p class="text-base text-[#c3bdd7] m-0">{{ result.content }}</p>
    </div>

    <!-- Top Three Predicted Emotions Section -->
    <div class="bg-[#2b223c] rounded-lg p-5 mb-5">
      <h3 class="text-lg font-bold text-[#d3bafc] mb-4">Top Three Predicted Emotions</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="(emotion, index) in topThreeEmotions"
          :key="index"
          class="p-4 rounded-md"
          :style="{ backgroundColor: getEmotionClass(emotion.label).backgroundColor + '20' }"
        >
          <div class="flex items-center">
            <span class="text-2xl mr-2">
              {{ getEmotionClass(emotion.label).emoji }}
            </span>
            <div>
              <h3 class="text-lg font-bold text-white">{{ capitalize(emotion.label) }}</h3>
              <p class="text-md text-gray-400">{{ (emotion.score * 100).toFixed(1) }}%</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Analysis Result Section -->
    <h2 class="text-xl font-bold">Analysis Result</h2>
    <div class="bg-[#2b223c] rounded-lg flex flex-wrap gap-8 mt-5 mb-8 py-5">
      <div class="flex-1 text-center">
        <h3 class="text-lg font-bold text-[#d3bafc]">Emotion Scores</h3>
        <div class="pl-8 pt-8 grid grid-cols-[repeat(auto-fit,minmax(160px,1fr))] gap-6">
          <div
            v-for="(score, emotion) in emotions"
            :key="emotion"
            class="w-44 h-24 p-4 rounded-lg text-center text-white font-bold"
            :class="getEmotionColorClass(emotion)"
          >
            <p class="text-base font-semibold">{{ capitalize(emotion) }}</p>
            <p class="text-base">{{ (score * 100).toFixed(1) }}%</p>
          </div>
        </div>
      </div>

      <!-- Emotion Distribution Chart -->
      <div class="flex-[0.8] text-center">
        <h3 class="text-lg font-bold text-[#d3bafc]">Emotion Distribution</h3>
        <canvas id="emotionPieChart" class="max-w-full max-h-[500px] pt-8"></canvas>
      </div>
    </div>

    <!-- Summary Section -->
    <div class="bg-[#2b223c] rounded-lg p-5 mb-5">
      <h3 class="text-lg font-bold text-[#d3bafc]">Summary</h3>
      <p class="text-[#c3bdd7]">{{ result.summary }}</p>
    </div>

    <!-- Suggested Response Section -->
    <div class="bg-[#2b223c] rounded-lg p-5 mb-5">
      <h3 class="text-lg font-bold text-[#d3bafc]">Suggested Response</h3>
      <p class="text-[#c3bdd7]">{{ result.suggested_response || 'No suggestion available.' }}</p>
    </div>

    <!-- Actionable Insights Section -->
    <div class="bg-[#2b223c] rounded-lg p-5 mb-5">
      <h3 class="text-lg font-bold text-[#d3bafc]">Actionable Insights</h3>
      <p class="text-[#c3bdd7]">{{ result.actionable_insights }}</p>
    </div>

    <!-- Buttons Section -->
    <button
      class="w-72 bg-[#6c5ce7] text-white mr-2 rounded-lg px-5 py-2.5 text-base font-bold cursor-pointer transition duration-300 hover:bg-[#4b39a2]"
      @click="openExportModal"
    >
      Export
    </button>

    <button
      class="w-72 bg-[#ff2b2b] text-white rounded-lg px-5 py-2.5 text-base font-bold cursor-pointer transition duration-300 hover:bg-[#a23939]"
      @click="showDeleteConfirmation"
    >
      Delete
    </button>

    <!-- Delete Confirmation Modal -->
    <div v-if="showConfirmModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Are you sure you want to delete this result permanently?</h3>
        <div class="modal-actions">
          <button class="yes-btn" @click="deleteResult(result.id)">Yes</button>
          <button class="cancel-btn" @click="closeModal">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Result deleted successfully!</h3>
        <button class="ok-btn" @click="navigateToHistory">OK</button>
      </div>
    </div>

    <!-- Export Modal -->
    <div v-if="showExportModal" class="export-modal-overlay">
      <div class="export-modal">
        <h3>Choose Export Format</h3>
        <button @click="exportAsCSV">Export as CSV</button>
        <button @click="exportAsPDF">Export as PDF</button>
        <button @click="closeExportModal">Cancel</button>
      </div>
    </div>
  </div>
  <div v-else>
    <p>Loading...</p>
  </div>
</template>

<script setup lang="ts">
import { useResultStore } from '@/stores/result';
import { useRoute, useRouter } from 'vue-router';
import ResultsService from '@/services/ResultsService.js';
import { Chart, registerables } from 'chart.js';
import { jsPDF } from 'jspdf';
import { nextTick, onMounted, ref, computed } from 'vue';
import html2canvas from 'html2canvas';

Chart.register(...registerables);

const route = useRoute();
const router = useRouter();
const resultStore = useResultStore();

interface EmotionResult {
  id: number;
  name: string;
  content: string;
  sadness_score: number;
  joy_score: number;
  love_score: number;
  anger_score: number;
  fear_score: number;
  surprise_score: number;
  summary: string;
  suggested_response?: string;
  actionable_insights: string;
}

const result = ref<EmotionResult>();
const emotions = ref<Record<string, number>>({});
const chart = ref<Chart>();
const showConfirmModal = ref(false);
const showSuccessModal = ref(false);
const showExportModal = ref(false);

onMounted(async () => {
  const resultId = parseInt(route.params.resultId as string);
  try {
    const res = await ResultsService.show(resultId);
    resultStore.setResult(res.data);
    result.value = res.data;
    emotions.value = {
      sadness: res.data.sadness_score,
      joy: res.data.joy_score,
      love: res.data.love_score,
      anger: res.data.anger_score,
      fear: res.data.fear_score,
      surprise: res.data.surprise_score,
    };

    nextTick(() => {
      renderChart();
    });
  } catch (error) {
    console.error(error);
  }
});

// Calculate top three emotions
const topThreeEmotions = computed(() => {
  return Object.entries(emotions.value)
    .map(([label, score]) => ({ label, score }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);
});

function capitalize(word: string) {
  return word.charAt(0).toUpperCase() + word.slice(1);
}

function getEmotionClass(emotion: string) {
  const classes: { [key: string]: { backgroundColor: string; emoji: string } } = {
    anger: { backgroundColor: '#ff4c4c', emoji: '😡' },
    surprise: { backgroundColor: '#70a1ff', emoji: '😲' },
    sadness: { backgroundColor: '#3742fa', emoji: '😢' },
    joy: { backgroundColor: '#2ed573', emoji: '😊' },
    love: { backgroundColor: '#ffc0cb', emoji: '❤️' },
    fear: { backgroundColor: '#ffa502', emoji: '😨' },
  };
  return classes[emotion] || { backgroundColor: '#808080', emoji: '❓' };
}

// New function for Emotion Scores section
function getEmotionColorClass(emotion: string) {
  const classes: { [key: string]: string } = {
    anger: 'bg-[#ff4c4c]',
    surprise: 'bg-[#70a1ff]',
    sadness: 'bg-[#3742fa]',
    joy: 'bg-[#2ed573]',
    love: 'bg-[#ffc0cb]',
    fear: 'bg-[#ffa502]',
  };
  return classes[emotion] || 'bg-gray-500';
}

function renderChart() {
  if (result.value) {
    const ctx = document.getElementById('emotionPieChart') as HTMLCanvasElement;

    const emotionData = Object.entries(emotions.value).map(([emotion, score]) => {
      return { emotion, score };
    });

    const labels = emotionData.map((data) => capitalize(data.emotion));
    const data = emotionData.map((data) => data.score);

    chart.value = new Chart(ctx, {
      type: 'pie',
      data: {
        labels,
        datasets: [
          {
            data,
            backgroundColor: ['#3742fa', '#2ed573', '#ffc0cb', '#ff4c4c', '#ffa502', '#70a1ff'],
            borderColor: '#fff',
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: {
              color: '#ffffff',
            },
          },
          tooltip: {
            callbacks: {
              label: function (tooltipItem) {
                return `${tooltipItem.label}: ${(tooltipItem.raw as number * 100).toFixed(1)}%`;
              },
            },
          },
        },
      },
    }) as Chart;
  }
}

function openExportModal() {
  showExportModal.value = true;
}

function closeExportModal() {
  showExportModal.value = false;
}

function exportAsCSV() {
  if (!result.value) {
    alert("No data available to export.");
    return;
  }


  const csvHeaders = [
    "Emotion Analysis Result",
    "",
    `Communication Name: ${result.value.name}`,
    "",
    "Text Content",
    `"${result.value.content}"`,
    "",
    "Emotion Scores",
    "Emotion,Score (%)",
  ];


  const emotionScores = Object.entries(emotions.value).map(([emotion, score]) => {
    return `${capitalize(emotion)},${(score * 100).toFixed(1)}`;
  });


  const csvBody = [
    "",
    "Summary",
    `"${result.value.summary}"`,
    "",
    "Suggested Response",
    `"${result.value.suggested_response || "No suggestion available."}"`,
    "",
    "Actionable Insights",
    `"${result.value.actionable_insights}"`,
  ];


  const csvData = [...csvHeaders, ...emotionScores, ...csvBody].join("\n");

  const blob = new Blob([csvData], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", `emotion-analysis-${result.value.id}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}


function exportAsPDF() {
  const resultsElement = document.querySelector(".min-h-screen") as HTMLElement;
  const exportModal = document.querySelector(".export-modal-overlay") as HTMLElement;

  if (!resultsElement) {
    alert("Results section not found!");
    return;
  }


  if (exportModal) {
    exportModal.style.display = "none";
  }

  html2canvas(resultsElement, {
    scale: 2,
    useCORS: true,
  })
    .then((canvas) => {
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

      pdf.save(`emotion-analysis-${result.value?.id}.pdf`);
    })
    .catch((error) => {
      console.error("Error saving PDF:", error);
      alert("Failed to save the PDF. Please try again.");
    })
    .finally(() => {
      if (exportModal) {
        exportModal.style.display = "flex";
      }
    });
}



function showDeleteConfirmation() {
  showConfirmModal.value = true;
}

function closeModal() {
  showConfirmModal.value = false;
}

async function deleteResult(id: number) {
  try {
    await ResultsService.delete(id);
    showConfirmModal.value = false;
    showSuccessModal.value = true;
  } catch (error) {
    console.error(error);
  }
}

function navigateToHistory() {
  router.push('/history');
}

</script>


<style>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: #2b223c;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  color: #ffffff;
  max-width: 400px;
  width: 90%;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.yes-btn,
.cancel-btn,
.ok-btn {
  width: 100px;
  background-color: #6c5ce7;
  color: #ffffff;
  border: none;
  border-radius: 5px;
  padding: 10px 20px;
  cursor: pointer;
}

.yes-btn:hover,
.cancel-btn:hover,
.ok-btn:hover {
  background-color: #4b39a2;
}

.cancel-btn {
  background-color: #f51111;
}

.cancel-btn:hover {
  background-color: #b01818;
}

.export-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.export-modal {
  background-color: #fff;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  width: 300px;
}

.export-modal h3 {
  margin-bottom: 20px;
  color: #333;
}

.export-modal button {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  border: none;
  border-radius: 5px;
  background-color: #3498db;
  color: white;
  cursor: pointer;
  font-size: 16px;
}

.export-modal button:hover {
  background-color: #2980b9;
}

.export-modal button:last-child {
  background-color: #e74c3c;
}

.export-modal button:last-child:hover {
  background-color: #c0392b;
}
</style>
