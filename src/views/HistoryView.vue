<template>
  <div class="min-h-screen p-8 bg-[#1e1b29] text-white flex flex-col">
    <header class="text-center mb-8">
      <h1 class="text-2xl font-bold text-[#d3bafc]">History</h1>
      <p class="text-base text-[#a8a6b3]">View all past sentiment analysis results in one place.</p>
    </header>
    <div class="flex-1 flex flex-wrap gap-5 justify-center items-center">
      <div
        v-for="result in pastResults"
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
  </div>
</template>

<script lang="ts">
import ResultsService from '@/services/ResultsService.js';
import type { RouteLocationRaw } from 'vue-router';

export default {
  data() {
    return {
      pastResults: null as { id: number; name: string; createdAt: string; input_type: string; majorEmotion: string }[] | null,
    };
  },
  async mounted() {
    try {
      const response = await ResultsService.index();
      this.pastResults = response.data.map((result) => {
        // Find the dominant emotion
        const emotions = {
          joy: result.joy_score,
          love: result.love_score,
          anger: result.anger_score,
          fear: result.fear_score,
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
  methods: {
    getEmotionClass(emotion: string) {
      const emotionClasses: { [key: string]: string } = {
        anger: 'bg-[#ff4c4c]',
        surprise: 'bg-[#ffa502]',
        sadness: 'bg-[#3742fa]',
        joy: 'bg-[#2ed573]',
        love: 'bg-[#ffc0cb]',
        fear: 'bg-[#6c5ce7]',
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
  },
};
</script>

<style scoped>
/* Add only unique styles here that Tailwind cannot handle */
</style>
