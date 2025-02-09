export interface EmotionResult {
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
