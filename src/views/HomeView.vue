<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ref } from "vue";

const userInput = ref("");

function handleSubmit() {
  console.log(userInput.value);
}
</script>

<template>
  <main
    class="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-purple-700 to-purple-900 p-4"
  >
    <h1 class="text-4xl md:text-6xl font-bold text-white mb-2 text-center">
      Welcome to
      <span
        class="text-purple-300 bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-300"
      >
        DeepPurple
      </span>
    </h1>
    <p class="text-xl text-purple-200 mb-8 text-center max-w-2xl">
      Your Emotional Detection AI
    </p>
    <form class="w-full max-w-md" @submit.prevent="handleSubmit">
      <div class="flex gap-2">
        <Input
          type="text"
          placeholder="Ask me anything..."
          class="flex-grow"
          v-model="userInput"
        />
        <Button
          type="submit"
          variant="secondary"
          class="bg-purple-500 hover:bg-purple-600 text-white"
        >
          Ask
        </Button>
      </div>
    </form>
  </main>
</template>
