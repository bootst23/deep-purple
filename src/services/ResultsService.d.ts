// /services/ResultsService.d.ts

declare module '@/services/ResultsService.js' {
  interface SentimentResult {
    id: string;
    name: string;
    content: string;
    anger_score: number;
    disgust_score: number;
    fear_score: number;
    joy_score: number;
    neutral_score: number;
    sadness_score: number;
    surprise_score: number;
    createdAt: string;
    input_type: string;
  }

  const ResultsService: {
    index: () => Promise<{ data: SentimentResult[] }>;
  };

  export default ResultsService;
}
