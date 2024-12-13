<template>
  <div class="history-page">
    <header class="history-header">
      <h1>History</h1>
      <p>View all past sentiment analysis results in one place.</p>
    </header>
    <div class="record-container">
      <div
        v-for="result in pastResults"
        :key="result.id"
        class="record-card"
        @click="navigateTo({
          name: 'result', 
          params:{resultId: result.id}
          })"
      >
        <div class="card-header">
          <h3>{{ result.name }}</h3>
        </div>
        <div class="card-body">
          <p><strong>Date Created:</strong> {{ result.createdAt }}</p>
          <p><strong>Input Type: </strong> {{ result.input_type }}</p>
        </div>
        <div
          class="emotion-badge"
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
      pastResults: null as { id: string; name: string; createdAt: string; input_type: string; majorEmotion: string }[] | null,
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
  methods: {
  getEmotionClass(emotion: string) {
    const emotionClasses: { [key: string]: string } = {
      anger: 'emotion-anger',
      surprise: 'emotion-surprise',
      sadness: 'emotion-sadness',
      joy: 'emotion-joy',
      neutral: 'emotion-neutral',
      disgust: 'emotion-disgust',
      fear: 'emotion-fear',
    };

    if (emotion in emotionClasses) {
      return emotionClasses[emotion as keyof typeof emotionClasses];
    } else {
      return 'emotion-default';
    }
  },

  navigateTo(route: RouteLocationRaw) {
    this.$router.push(route);
  },
},

};
</script>



<style scoped>
/* General Styles with Deep Purple Theme */
.history-page {
  padding: 30px;
  background-color: #1e1b29; /* Deep purple background */
  color: #ffffff; /* White text for readability */
  min-height: 100vh; /* Ensure full viewport height */
  display: flex;
  flex-direction: column;
}

.history-header {
  text-align: center;
  margin-bottom: 30px;
}

.history-header h1 {
  font-size: 2rem;
  font-weight: bold;
  color: #d3bafc; /* Light purple for header */
}

.history-header p {
  font-size: 1rem;
  color: #a8a6b3; /* Muted lavender for subtext */
}

/* Record Card Container */
.record-container {
  flex: 1; /* Stretch to take available space */
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
  align-items: center; /* Center if there's not enough data */
}

/* Individual Record Cards */
.record-card {
  background-color: #2b223c; /* Dark purple card background */
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5); /* Subtle shadow */
  width: 300px;
  padding: 20px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.record-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.7);
}

.card-header h3 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #ffffff; /* White text for header */
  margin-bottom: 20px;
}

.card-body p {
  font-size: 0.9rem;
  color: #c3bdd7; /* Soft lavender for body text */
  margin-bottom: 10px;
}

/* Emotion Badge */
.emotion-badge {
  text-align: center;
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
  color: #fff;
  margin-top: 15px;
  align-self: flex-start;
  width: 110px;
}

/* Emotion Classes with Vibrant Colors */
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

/* Responsive Adjustments */
@media (max-width: 768px) {
  .record-container {
    flex-direction: column;
    align-items: center;
  }
}

</style>
