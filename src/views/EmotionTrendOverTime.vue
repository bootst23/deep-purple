<!-- eslint-disable @typescript-eslint/no-unused-vars -->
<template>
    <div>
      <h2 class="text-[1.125rem] font-bold text-[#a8a6b3] mb-4">Emotion Trends Over Time</h2>
      <div class="flex space-x-4 mb-4">
        <input
          type="date"
          v-model="startDate"
          class="p-2 border border-[#a692cc] rounded-md bg-[#2b223c] text-[#c3bdd7]"
        />
        <input
          type="date"
          v-model="endDate"
          class="p-2 border border-[#a692cc] rounded-md bg-[#2b223c] text-[#c3bdd7]"
        />
        <select
          v-model="groupBy"
          class="p-2 border border-[#a692cc] rounded-md bg-[#2b223c] text-[#c3bdd7]"
        >
          <option value="day">Daily</option>
          <option value="week">Weekly</option>
          <option value="month">Monthly</option>
        </select>
        <button
          class="bg-[#8a4fff] text-white px-4 py-2 rounded-md hover:bg-[#6f3bbd] transition"
          @click="fetchEmotionTrends"
        >
          Fetch Trends
        </button>
      </div>
  
      <!-- Emotion Trends Chart -->
      <div class="bg-[#1e1b29] p-4 rounded-md">
        <Line :data="chartData" :options="chartOptions" />
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from "vue";
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
  } from "chart.js";
  
  ChartJS.register(
    Title,
    Tooltip,
    Legend,
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement
  );
  
  const startDate = ref("");
  const endDate = ref("");
  const groupBy = ref("day");
  interface Trend {
    date: string;
    sadness: number;
    joy: number;
    anger: number;
    // Add more emotions as needed
  }
  
  const chartData = ref<{
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      borderColor: string;
      fill: boolean;
    }[];
  }>({
    labels: [],
    datasets: [],
  });
  
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
  };
  async function fetchEmotionTrends() {
    if (!startDate.value || !endDate.value) {
      alert("Please select a start date and end date.");
      return;
    }
  
    try {
      const response = await axios.get("http://localhost:8080/emotion-trends", {
        params: {
          start_date: startDate.value,
          end_date: endDate.value,
          group_by: groupBy.value,
        },
      });
  
      const trends = response.data.emotion_trends;
  
      // Update chart data
      chartData.value = {
        labels: trends.map((trend: Trend) => trend.date),
        datasets: [
          {
            label: "Sadness",
            data: trends.map((trend: Trend) => trend.sadness),
            borderColor: "#FF6384",
            fill: false,
          },
          {
            label: "Joy",
            data: trends.map((trend: Trend) => trend.joy),
            borderColor: "#36A2EB",
            fill: false,
          },
          {
            label: "Anger",
            data: trends.map((trend: Trend) => trend.anger),
            borderColor: "#FFCE56",
            fill: false,
          },
          // Add more emotions as needed
        ],
      };
    } catch (error) {
      console.error("Error fetching emotion trends:", error);
      alert("Failed to fetch emotion trends. Please try again.");
    }
  }
  </script>