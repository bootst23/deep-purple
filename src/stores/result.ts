import { defineStore } from 'pinia';

export interface Result {
    id: number;
    name: string;
    content: string;
    input_type: string;
    anger_score: number;
    disgust_score: number;
    fear_score: number;
    joy_score: number;
    neutral_score: number;
    sadness_score: number;
    surprise_score: number;
    createdAt: string;
    updatedAt: string;
  }
  

export const useResultStore = defineStore('result', {
    state: () => ({
      result: null as Result | null, 
    }),
    actions: {
      setResult(result: Result) {
        this.result = result; 
      },
    },
});