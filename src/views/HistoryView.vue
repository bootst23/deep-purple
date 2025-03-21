<template>
  <div class="min-h-screen p-8 bg-[#1e1b29] text-white flex flex-col">
    <header class="text-center mb-8">
      <h1 class="text-2xl font-bold text-[#d3bafc]">History</h1>
      <p class="text-base text-[#a8a6b3]">View all past sentiment analysis results in one place.</p>
    </header>

    <!-- Results Grid -->
    <div class="flex-1 flex flex-wrap gap-5 justify-center items-center">
      <div
        v-for="result in paginatedResults"
        :key="result.id"
        class="bg-[#2b223c] rounded-lg shadow-lg w-72 p-5 cursor-pointer transition duration-300 ease-in-out flex flex-col justify-between hover:translate-y-[-5px] hover:shadow-2xl"
        @click="navigateTo({
          name: 'result',
          params: { resultId: result.id }
        })"
      >
        <div class="mb-5">
          <h3 class="text-xl font-bold text-white">{{ result.name }}</h3>
        </div>
        <div class="mb-2.5">
          <p class="text-sm text-[#c3bdd7] mb-2.5"><strong>Date Created:</strong> {{ result.createdAt }}</p>
          <p class="text-sm text-[#c3bdd7]"><strong>Input Type: </strong> {{ result.input_type }}</p>
        </div>
        <div
          class="py-2 px-3 rounded-full text-sm font-bold text-white mt-4 self-start w-[110px] text-center"
          :class="getEmotionClass(result.majorEmotion)"
        >
          {{ result.majorEmotion }}
        </div>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div class="flex justify-center items-center mt-8 space-x-4">
      <button
        class="bg-[#8a4fff] text-white px-4 py-2 rounded-md hover:bg-[#6f3bbd] transition"
        @click="previousPage"
        :disabled="currentPage === 1"
      >
        Previous
      </button>
      <span class="text-[#c3bdd7]">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <button
        class="bg-[#8a4fff] text-white px-4 py-2 rounded-md hover:bg-[#6f3bbd] transition"
        @click="nextPage"
        :disabled="currentPage === totalPages"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import ResultsService from '@/services/ResultsService.js';
import type { RouteLocationRaw } from 'vue-router';

export default {
  data() {
    return {
      pastResults: null as { id: number; name: string; createdAt: string; input_type: string; majorEmotion: string }[] | null,
      currentPage: 1, // Current page number
      itemsPerPage: 6, // Number of items per page
    };
  },
  async mounted() {
    try {
      const response = await ResultsService.index();
      this.pastResults = response.data.map((result) => {
        // Find the dominant emotion
        const emotions = {
          anger: result.anger_score,
          disgust: result.disgust_score,
          fear: result.fear_score,
          joy: result.joy_score,
          neutral: result.neutral_score,
          sadness: result.sadness_score,
          surprise: result.surprise_score,
        };
        const majorEmotion = Object.keys(emotions).reduce((a, b) => {
          return emotions[a as keyof typeof emotions] > emotions[b as keyof typeof emotions] ? a : b;
        });

        // Format createdAt to dd/mm/yyyy
        const formattedDate = new Date(result.createdAt).toLocaleDateString(
          'en-GB'
        );

        return {
          ...result,
          majorEmotion,
          createdAt: formattedDate, // Replace ISO date with formatted date
        };
      });
    } catch (error) {
      console.error('Error fetching results:', error);
    }
  },
  computed: {
    // Calculate total number of pages
    totalPages() {
      if (!this.pastResults) return 0;
      return Math.ceil(this.pastResults.length / this.itemsPerPage);
    },
    // Get results for the current page
    paginatedResults() {
      if (!this.pastResults) return [];
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.pastResults.slice(start, end);
    },
  },
  methods: {
    getEmotionClass(emotion: string) {
      const emotionClasses: { [key: string]: string } = {
        anger: 'bg-[#ff4c4c]',
        disgust: 'bg-[#32cd32]',
        fear: 'bg-[#800080]',   
        joy: 'bg-[#FFCE56]',
        neutral: 'bg-[#576574]',
        sadness: 'bg-[#1e90ff]',
        surprise: 'bg-[#ffa500]',

      };

      if (emotion in emotionClasses) {
        return emotionClasses[emotion as keyof typeof emotionClasses];
      } else {
        return 'bg-gray-500';
      }
    },

    navigateTo(route: RouteLocationRaw) {
      this.$router.push(route);
    },

    // Pagination methods
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
      }
    },
  },
};
</script>

<style scoped>
/* Add any custom styles here */
</style>