export interface EmotionResult {
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