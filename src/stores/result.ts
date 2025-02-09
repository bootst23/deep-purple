import { defineStore } from 'pinia';

export interface Result {

  id: number; 
  name: string;
  content: string;
  input_type: string;
  sadness_score: number;
  joy_score: number;
  love_score: number;
  anger_score: number;
  fear_score: number;
  surprise_score: number;
  dominant_emotion: string;
  summary: string;
  actionable_insights: string;
  suggested_response: string;
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