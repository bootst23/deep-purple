<template>
  <div class="result-page" v-if="result">
    <header class="result-header">
      <h1>{{ result.name }}</h1>
      <p>Emotion Analysis Result</p>
    </header>

    <!-- Text Content Section -->
    <div class="text-content">
      <h3>Text Content</h3>
      <p>{{ result.content }}</p>
    </div>

    <!-- Emotion Scores and Pie Chart -->
    <h2> Analysis Result </h2>
    <div class="analysis-container">
      <!-- Emotion Scores -->
      <div class="emotion-scores-section">
        <h3>Emotion Scores</h3>
        <div class="emotion-scores">
          <div
            v-for="(score, emotion) in emotions"
            :key="emotion"
            class="emotion-box"
            :class="getEmotionClass(emotion)"
          >
            <p class="emotion-name">{{ capitalize(emotion) }}</p>
            <p class="emotion-score">{{ (score * 100).toFixed(1) }}%</p>
          </div>
        </div>
      </div>

      <!-- Pie Chart -->
      <div class="chart-container">
        <h3>Emotion Distribution</h3>
        <canvas id="emotionPieChart"></canvas>
      </div>
    </div>

    <!-- Buttons -->
    <button class="export-btn" @click="openExportModal">Export</button>
    <button class="delete-btn" @click="showDeleteConfirmation">Delete</button>

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
    <p>Result not found.</p>
  </div>
</template>

<script lang="ts">
import { useResultStore } from '@/stores/result'; 
import type { Result } from '@/stores/result';
import { useRoute } from 'vue-router';
import ResultsService from '@/services/ResultsService.js';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default {
  data() {
    return {
      result: null as Result | null,
      emotions: {},
      chart: null as Chart | null,
      showConfirmModal: false, // State for modals
      showSuccessModal: false, 
      showExportModal: false,
    };
  },
  async mounted() {
    const route = useRoute();
    const resultId = parseInt(route.params.resultId as string);
    const resultStore = useResultStore(); // Access Pinia store

    try {
      const result = await ResultsService.show(resultId); // Fetch result from API
      console.log('API Response:', result); 
      console.log('First Result:', result.data);

      resultStore.setResult(result.data);
      this.result = result.data;
      
    } catch (err) {
      console.error('Error fetching result:', err);
    }

    // Ensure that 'result' is not null before assigning emotions
    if (this.result) {
      this.emotions = {
        anger: this.result.anger_score,
        disgust: this.result.disgust_score,
        fear: this.result.fear_score,
        joy: this.result.joy_score,
        neutral: this.result.neutral_score,
        sadness: this.result.sadness_score,
        surprise: this.result.surprise_score,
      };

      this.$nextTick(() => {
        this.renderChart();
      });
    }
  },
  methods: {
    capitalize(word: string) {
      return word.charAt(0).toUpperCase() + word.slice(1);
    },
    getEmotionClass(emotion: string) {
      const classes: { [key: string]: string } = {
        anger: 'emotion-anger',
        surprise: 'emotion-surprise',
        sadness: 'emotion-sadness',
        joy: 'emotion-joy',
        neutral: 'emotion-neutral',
        disgust: 'emotion-disgust',
        fear: 'emotion-fear',
      };
      return classes[emotion] || 'emotion-default';
    },
    renderChart() {
      if (this.result) {
        const ctx = document.getElementById('emotionPieChart') as HTMLCanvasElement;
        const data = Object.values(this.emotions);
        const labels = Object.keys(this.emotions).map((e) => this.capitalize(e));

        this.chart = new Chart(ctx, {
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
        }) as Chart; 
      }
    },

    openExportModal() {
      this.showExportModal = true;
    },
    closeExportModal() {
      this.showExportModal = false;
    },

    exportAsCSV() {
      if (this.result) {
        const csvData = [];

        csvData.push(['File Content', ...Object.keys(this.emotions).map((e) => this.capitalize(e))]); //Header

        csvData.push([
          this.result.content,
          ...Object.values(this.emotions).map((score) => (score as number).toFixed(2)),  //Data
        ]);

        // Convert array to CSV string
        const csvContent = csvData.map((row) => row.join(",")).join("\n");

        // Create a Blob and download the file
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `Emotion_Analysis_Result_${this.result.id}.csv`;
        link.click();
      }
    },

    
    async exportAsPDF() {
      if (this.result) {
        const { jsPDF } = await import('jspdf');
        const html2canvas = (await import('html2canvas')).default;

        const doc = new jsPDF();

        // Add title and basic information
        doc.setFontSize(18);
        doc.text('Emotion Analysis Result', 10, 10);

        doc.setFontSize(14);
        doc.text(`Result Name: ${this.result.name}`, 10, 20);

        // Add file content
        doc.setFontSize(12);
        doc.text('File Content:', 10, 30);
        doc.setFontSize(10);
        doc.text(this.result.content, 10, 40, { maxWidth: 180 });

        // Add emotion scores
        const emotionsStartY = 50 + Math.ceil(this.result.content.length / 100) * 10; 
        doc.setFontSize(12);
        doc.text('Emotion Scores:', 10, emotionsStartY);
        let yPosition = emotionsStartY + 10;
        Object.entries(this.emotions).forEach(([emotion, score]) => {
          doc.text(`${this.capitalize(emotion)}: ${(score as number).toFixed(2)}`, 10, yPosition);
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
        doc.save(`Emotion_Analysis_Result_${this.result.id}.pdf`);
      }
    },

    showDeleteConfirmation() {
      this.showConfirmModal = true;
    },
    closeModal() {
      this.showConfirmModal = false;
      this.showSuccessModal = false;
    },

    async deleteResult(resultId: number) {
      try {
        await ResultsService.delete(resultId);
        this.showConfirmModal = false;
        this.showSuccessModal = true; // Show success modal
      } catch (error) {
        console.error('Error deleting result:', error);
        alert('Failed to delete result.');
      }
    },

    navigateToHistory() {
      this.$router.push('/history'); // Navigate to history page
    },

  },
};
</script>

<style scoped>
/* General Styles */
.result-page {
  background-color: #1e1b29;
  color: #ffffff;
  padding: 30px;
  min-height: 100vh;
}

.result-header {
  text-align: center;
  margin-bottom: 30px;
}

.result-header h1 {
  color: #d3bafc;
  font-size: 2rem;
  font-weight: bold;
}

.result-header p {
  color: #a8a6b3;
}

/* Analysis Container */
.analysis-container {
  background-color: #2b223c;
  border-radius: 10px;
  display: flex;
  gap: 30px;
  margin-top: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
  padding-top: 20px;
  padding-bottom: 20px;
}

/* Emotion Scores Section */
.emotion-scores-section {
  flex: 0.5;
  text-align: center;
}

.emotion-scores {
  padding-left: 30px;
  padding-top: 30px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 25px;
}

.emotion-box {
  width: 180px;
  height: 90px;
  padding: 15px;
  border-radius: 10px;
  text-align: center;
  color: #ffffff;
  font-weight: bold;
  background-color: #2b223c;
}

/* Emotion Color Classes */
.emotion-anger {
  background-color: #ff4c4c;
}

.emotion-surprise {
  background-color: #ffa502;
}

.emotion-sadness {
  background-color: #3742fa;
}

.emotion-joy {
  background-color: #2ed573;
}

.emotion-neutral {
  background-color: #57606f;
}

.emotion-disgust {
  background-color: #6c5ce7;
}

.emotion-fear {
  background-color: #70a1ff;
}

/* Chart Container */
.chart-container {
  flex: 0.8;
  text-align: center;
}

.chart-container canvas {
  max-width: 100%;
  max-height: 500px;
  padding-top: 30px;
}

/* Text Content */
.text-content {
  background-color: #2b223c;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  max-height: 300px; 
  overflow-y: auto; 
  overflow-x: hidden; 
  white-space: pre-wrap; 
  word-wrap: break-word; 
}

.text-content h3 {
  margin-bottom: 10px;
  color: #d3bafc;
}

.text-content p {
  font-size: 1rem;
  color: #c3bdd7;
  margin: 0; 
}

/* Export Button */
.export-btn {
  margin-right: 30px;
  width: 300px;
  background-color: #6c5ce7;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 10px 20px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.export-btn:hover {
  background-color: #4b39a2;
}

.delete-btn {
  margin-right: 30px;
  width: 300px;
  background-color: #f51111;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 10px 20px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.export-btn:hover {
  background-color: #b01818;
}

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
