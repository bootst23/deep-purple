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

    <!-- Export Button -->
    <button class="export-btn" @click="exportData">Export</button>
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
        }) as Chart; // Type assertion here
      }
    },
    exportData() {
      //Export
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
</style>
