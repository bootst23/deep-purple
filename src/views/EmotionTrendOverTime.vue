<template>
  <div class="p-8 bg-[#1b172b] min-h-screen text-[#e5e3f0]">
    <h2 class="text-2xl font-bold text-[#a78bfa] mb-6">Emotion Trends Over Time</h2>
    
    <!-- Date and Grouping Controls -->
    <div class="flex flex-col gap-6 mb-6">
      <!-- Date Range Inputs -->
      <div class="flex flex-wrap gap-4">
        <div class="flex flex-col">
          <label class="text-[#c3bdd7] mb-1">Start Date</label>
          <input
            type="date"
            v-model="startDate"
            class="p-3 border border-[#6b4fd8] rounded-md bg-[#2d223e] text-[#c3bdd7] focus:outline-none focus:border-[#8a4fff]"
            @change="handleStartDateChange"
          />
          <span v-if="dateError" class="text-red-400 text-sm mt-1">{{ dateError }}</span>
        </div>

        <div class="flex flex-col">
          <label class="text-[#c3bdd7] mb-1">End Date</label>
          <input
            type="date"
            v-model="endDate"
            :min="startDate"
            :disabled="!startDate"
            class="p-3 border border-[#6b4fd8] rounded-md bg-[#2d223e] text-[#c3bdd7] focus:outline-none focus:border-[#8a4fff] disabled:opacity-50"
            @change="handleEndDateChange"
          />
        </div>

        <div class="flex flex-col">
          <label class="text-[#c3bdd7] mb-1">Group By</label>
          <select
            v-model="groupBy"
            class="p-3 border border-[#6b4fd8] rounded-md bg-[#2d223e] text-[#c3bdd7] focus:outline-none focus:border-[#8a4fff]"
            @change="handleGroupByChange"
          >
            <option value="day">Daily</option>
            <option v-if="dateDifference >= 7" value="week">Weekly</option>
            <option v-if="dateDifference >= 30" value="month">Monthly</option>
          </select>
        </div>
      </div>

      <!-- Emotion Selection Checkboxes -->
      <div class="flex flex-col gap-2">
        <label class="text-[#c3bdd7]">Select Emotions:</label>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
          <label
            v-for="(emotion, key) in emotionColors"
            :key="key"
            class="flex items-center gap-2 p-2 border border-[#6b4fd8] rounded-md bg-[#2d223e] hover:bg-[#3b2f4d] transition cursor-pointer"
          >
            <input
              type="checkbox"
              v-model="selectedEmotions"
              :value="key"
              class="accent-[#8a4fff]"
            />
            <span class="text-[#c3bdd7]">{{ key.charAt(0).toUpperCase() + key.slice(1) }}</span>
          </label>
        </div>
      </div>

      <!-- Fetch Trends Button -->
      <button
        class="bg-[#8a4fff] text-white px-6 py-3 rounded-md hover:bg-[#6f3bbd] transition disabled:opacity-50 disabled:cursor-not-allowed w-full md:w-auto"
        @click="fetchEmotionTrends"
        :disabled="!startDate || !endDate || loading"
      >
        {{ loading ? 'Loading...' : 'Fetch Trends' }}
      </button>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="mb-6 p-4 bg-red-900/50 border border-red-500 rounded-md text-red-200">
      {{ error }}
    </div>

    <!-- Group By Warning -->
    <div v-if="groupByWarning" class="mb-6 p-4 bg-yellow-900/50 border border-yellow-500 rounded-md text-yellow-200">
      {{ groupByWarning }}
    </div>

    <!-- Emotion Trends Chart -->
    <div class="bg-[#252033] p-6 rounded-md shadow-md h-[600px]" v-if="chartData.datasets.length">
      <Line :data="chartData" :options="chartOptions" />
    </div>
    <div v-else class="bg-[#252033] p-6 rounded-md shadow-md text-center text-[#c3bdd7]">
      Select a date range and click "Fetch Trends" to view the emotion analysis
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import axios from "axios";
import { Line } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Filler,
  type TooltipItem,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Filler
);

// State variables
const startDate = ref("");
const endDate = ref("");
const groupBy = ref("day");
const selectedEmotions = ref<string[]>([]);
const error = ref("");
const dateError = ref("");
const groupByWarning = ref("");
const loading = ref(false);

// Emotion colors configuration
const emotionColors = {
  anger: { border: "#ff4500", background: "rgba(255, 69, 0, 0.1)" }, // Red
  disgust: { border: "#32cd32", background: "rgba(50, 205, 50, 0.1)" }, // Green
  fear: { border: "#800080", background: "rgba(128, 0, 128, 0.1)" }, // Purple
  joy: { border: "#ffd700", background: "rgba(255, 215, 0, 0.1)" }, // Yellow
  neutral: { border: "#d3d3d3", background: "rgba(211, 211, 211, 0.1)" }, // Light Gray
  sadness: { border: "#1e90ff", background: "rgba(30, 144, 255, 0.1)" }, // Blue
  surprise: { border: "#ffa500", background: "rgba(255, 165, 0, 0.1)" }, // Orange
};

// Computed date difference in days
const dateDifference = computed(() => {
  if (!startDate.value || !endDate.value) return 0;
  const start = new Date(startDate.value);
  const end = new Date(endDate.value);
  return Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
});

// Initialize chart data
const chartData = ref<{
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    fill: boolean;
    tension: number;
    pointRadius: number;
    pointHoverRadius: number;
    borderWidth: number;
  }[];
}>({
  labels: [],
  datasets: [],
});

// Chart options configuration
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: 'index' as const
  },
  plugins: {
    legend: {
      labels: {
        color: "#e5e3f0",
        font: { size: 14 },
        usePointStyle: true,
        pointStyle: 'circle',
      }
    },
    tooltip: {
      backgroundColor: "#1b172b",
      titleColor: "#e5e3f0",
      bodyColor: "#c3bdd7",
      borderColor: "#6b4fd8",
      borderWidth: 1,
      padding: 10,
      callbacks: {
        label: (tooltipItem: TooltipItem<"line">) => {
          const value = tooltipItem.raw as number;
          return `${tooltipItem.dataset.label}: ${value.toFixed(2)}`;
        },
      },
    },
  },
  scales: {
    x: {
      ticks: { color: "#e5e3f0" },
      grid: { color: "#3b3b5e" }
    },
    y: {
      ticks: { color: "#e5e3f0" },
      grid: { color: "#3b3b5e" },
      beginAtZero: true
    }
  },
};

// Date change handlers
const handleStartDateChange = () => {
  dateError.value = "";
  if (endDate.value && new Date(endDate.value) < new Date(startDate.value)) {
    endDate.value = startDate.value;
  }
};

const handleEndDateChange = () => {
  dateError.value = "";
  if (new Date(endDate.value) < new Date(startDate.value)) {
    dateError.value = "End date cannot be earlier than start date";
    endDate.value = startDate.value;
  }
};

// Group by change handler
const handleGroupByChange = () => {
  groupByWarning.value = "";
  if (groupBy.value === "week" && dateDifference.value < 7) {
    groupBy.value = "day";
    groupByWarning.value = "Date range too short for weekly grouping. Switched to daily view.";
  } else if (groupBy.value === "month" && dateDifference.value < 30) {
    groupBy.value = "day";
    groupByWarning.value = "Date range too short for monthly grouping. Switched to daily view.";
  }
};

// Watch for date changes to validate grouping
watch([startDate, endDate], () => {
  if (groupBy.value === "week" && dateDifference.value < 7) {
    groupBy.value = "day";
    groupByWarning.value = "Switched to daily view due to short date range.";
  } else if (groupBy.value === "month" && dateDifference.value < 30) {
    groupBy.value = "day";
    groupByWarning.value = "Switched to daily view due to short date range.";
  }
});

// Fetch emotion trends
async function fetchEmotionTrends() {
  if (!startDate.value || !endDate.value) {
    error.value = "Please select both start and end dates.";
    return;
  }

  loading.value = true;
  error.value = "";
  
  try {
    const response = await axios.get("https://deep-purple-databaseservice-fbj1.onrender.com/emotion-trends", {
      params: {
        start_date: startDate.value,
        end_date: endDate.value,
        group_by: groupBy.value,
        emotions: selectedEmotions.value.join(','), // Pass selected emotions to the backend
      },
    });

    const trends = response.data.emotion_trends;

    // Update chart data
    chartData.value = {
      labels: trends.map((trend: { date: string; anger: number; disgust: number; fear: number; joy: number; neutral: number; sadness: number; surprise: number }) => trend.date),
      datasets: Object.entries(emotionColors)
        .filter(([emotion]) => selectedEmotions.value.length === 0 || selectedEmotions.value.includes(emotion))
        .map(([emotion, colors]) => ({
          label: emotion.charAt(0).toUpperCase() + emotion.slice(1),
          data: trends.map((trend: { date: string; anger: number; disgust: number; fear: number; joy: number; neutral: number; sadness: number; surprise: number }) => trend[emotion as keyof typeof trend]),
          borderColor: colors.border,
          backgroundColor: colors.background,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          borderWidth: 2,
        })),
    };
  } catch (err) {
    console.error("Error fetching emotion trends:", err);
    error.value = "Failed to fetch emotion trends. Please try again.";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
input[type="date"]::-webkit-calendar-picker-indicator {
  filter: invert(0.8);
  cursor: pointer;
}
</style>