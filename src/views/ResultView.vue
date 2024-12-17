<template>
  <div class="min-h-screen bg-[#1e1b29] text-white p-8" v-if="result">
    <header class="text-center mb-8">
      <h1 class="text-2xl font-bold text-[#d3bafc]">{{ result.name }}</h1>
      <p class="text-[#a8a6b3]">Emotion Analysis Result</p>
    </header>

    <!-- Text Content Section -->
    <div class="bg-[#2b223c] rounded-lg p-5 mb-5 max-h-[300px] overflow-y-auto overflow-x-hidden whitespace-pre-wrap break-words">
      <h3 class="mb-2 text-[#d3bafc]">Text Content</h3>
      <p class="text-base text-[#c3bdd7] m-0">{{ result.content }}</p>
    </div>

    <!-- Emotion Scores and Pie Chart -->
    <h2 class="text-xl font-bold">Analysis Result</h2>
    <div class="bg-[#2b223c] rounded-lg flex flex-wrap gap-8 mt-5 mb-8 py-5">
      <!-- Emotion Scores -->
      <div class="flex-1 text-center">
        <h3 class="text-lg font-bold text-[#d3bafc]">Emotion Scores</h3>
        <div class="pl-8 pt-8 grid grid-cols-[repeat(auto-fit,minmax(160px,1fr))] gap-6">
          <div
            v-for="(score, emotion) in emotions"
            :key="emotion"
            class="w-44 h-24 p-4 rounded-lg text-center text-white font-bold"
            :class="getEmotionClass(emotion)"
          >
            <p class="text-base font-semibold">{{ capitalize(emotion) }}</p>
            <p class="text-base">{{ (score * 100).toFixed(1) }}%</p>
          </div>
        </div>
      </div>

      <!-- Pie Chart -->
      <div class="flex-[0.8] text-center">
        <h3 class="text-lg font-bold text-[#d3bafc]">Emotion Distribution</h3>
        <canvas id="emotionPieChart" class="max-w-full max-h-[500px] pt-8"></canvas>
      </div>
    </div>

    <!-- Export Button -->
    <button class="w-72 bg-[#6c5ce7] text-white mr-2 rounded-lg px-5 py-2.5 text-base font-bold cursor-pointer transition duration-300 hover:bg-[#4b39a2]" @click="openExportModal">
      Export
    </button>

    <button class="w-72 bg-[#ff2b2b] text-white rounded-lg px-5 py-2.5 text-base font-bold cursor-pointer transition duration-300 hover:bg-[#a23939]" @click="showDeleteConfirmation">
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

import {jsPDF} from 'jspdf';
import html2canvas from 'html2canvas';
import { nextTick, onMounted, ref } from 'vue';
import { useEmotionAPI } from '@/composables/api/emotion';
import type { EmotionResult } from '@/types/emotion';
Chart.register(...registerables);

const route = useRoute();
const router = useRouter();
const resultStore = useResultStore(); // Access Pinia store
const {get} = useEmotionAPI();

const result = ref<EmotionResult>();
const emotions = ref({});
const chart = ref<Chart>();
const showConfirmModal = ref(false); // State for modals
const showSuccessModal = ref(false); // State for modals
const showExportModal = ref(false); // State for modals

onMounted(async () => {
  const resultId = parseInt(route.params.resultId as string);
  // Fetching the emotion result from the API
  try {
    const res = await get(resultId);
    resultStore.setResult(res);
    result.value = res;
      emotions.value = {
        anger: res.anger_score,
        disgust: res.disgust_score,
        fear: res.fear_score,
        joy: res.joy_score,
        neutral: res.neutral_score,
        sadness: res.sadness_score,
        surprise: res.surprise_score,
      };

      nextTick(() => {
        renderChart();
      });
  } catch (error) {
    console.error(error);
  }
});

function capitalize(word: string) {
      return word.charAt(0).toUpperCase() + word.slice(1);
    };
    function getEmotionClass(emotion: string) {
      const classes: { [key: string]: string } = {
        anger: 'bg-[#ff4c4c]',
        surprise: 'bg-[#ffa502]',
        sadness: 'bg-[#3742fa]',
        joy: 'bg-[#2ed573]',
        neutral: 'bg-[#57606f]',
        disgust: 'bg-[#6c5ce7]',
        fear: 'bg-[#70a1ff]',
      };
      return classes[emotion] || 'bg-gray-500';
    };
    function renderChart() {
      if (result.value) {
        const ctx = document.getElementById('emotionPieChart') as HTMLCanvasElement;
        const data = Object.values(emotions);
        const labels = Object.keys(emotions).map((e) => capitalize(e));

        chart.value = new Chart(ctx, {
          type: 'pie',
          data: {
            labels,
            datasets: [
              {
                data,
                backgroundColor: [ '#ff4c4c','#ffa502','#3742fa','#2ed573','#57606f','#6c5ce7','#70a1ff',],
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
            },
          },
        }) as Chart; // Type assertion here
      }
    }

    function openExportModal() {
      showExportModal.value = true;
    }

    function closeExportModal() {
      showExportModal.value = false;
    }

    function exportAsCSV() {
      if (result.value) {
        const csvData = [];

        csvData.push(['File Content', ...Object.keys(emotions).map((e) => capitalize(e))]); //Header

        csvData.push([
          result.value.content,
          ...Object.values(emotions).map((score) => (score as number).toFixed(2)),  //Data
        ]);

          // Convert array to CSV string
        const csvContent = csvData.map((row) => row.join(",")).join("\n");

          // Create a Blob and download the file
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `Emotion_Analysis_Result_${result.value.id}.csv`;
        link.click();
      }
    }


    async function exportAsPDF() {
      if (result.value) {

        const doc = new jsPDF();

          // Add title and basic information
        doc.setFontSize(18);
        doc.text('Emotion Analysis Result', 10, 10);

        doc.setFontSize(14);
        doc.text(`Result Name: ${result.value.name}`, 10, 20);

          // Add file content
        doc.setFontSize(12);
        doc.text('File Content:', 10, 30);
        doc.setFontSize(10);
        doc.text(result.value.content, 10, 40, { maxWidth: 180 });

          // Add emotion scores
        const emotionsStartY = 50 + Math.ceil(result.value.content.length / 100) * 10;
        doc.setFontSize(12);
        doc.text('Emotion Scores:', 10, emotionsStartY);
        let yPosition = emotionsStartY + 10;
        Object.entries(emotions).forEach(([emotion, score]) => {
          doc.text(`${capitalize(emotion)}: ${(score as number).toFixed(2)}`, 10, yPosition);
          yPosition += 10;
        });


          // Add Pie Chart
        const chartElement = document.getElementById('emotionPieChart');
        if (chartElement) {
          const chartCanvas = await html2canvas(chartElement, { backgroundColor: null });
          const chartImage = chartCanvas.toDataURL('image/png');
          doc.addImage(chartImage, 'PNG', 10, yPosition, 180, 90);
        }

          // Save the PDF
        doc.save(`Emotion_Analysis_Result_${result.value.id}.pdf`);
      }
    }

    function showDeleteConfirmation() {
      showConfirmModal.value = true;
    };
    function closeModal() {
      showConfirmModal.value = false;
      showSuccessModal.value = false;
    };

    async function deleteResult(resultId: number) {
      try {
        await ResultsService.delete(resultId);
        showConfirmModal.value = false;
        showSuccessModal.value = true; // Show success modal
      } catch (error) {
        console.error('Error deleting result:', error);
        alert('Failed to delete result.');
      }
    };

    function navigateToHistory() {
      router.push('/history'); // Navigate to history page
    };
</script>

<style>
/*styles for modal */
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

/* Modal Box */
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
