import { fetcher } from "@/composables/utils/fetcher";
import type { EmotionResult } from "@/types/emotion";

function useEmotionAPI() {
    async function getAll(): Promise<EmotionResult[]> {
        try {
            const res = await fetcher("/results", {
                method: "GET",
                retry: 1,
            });

            const data = await res.json<EmotionResult[]>();
            return data;
        } catch (error: unknown) {
            const err = error as Error;
            throw new Error(err.message || "An error occurred while fetching emotion results.");
        }
    }

    async function get(id: number): Promise<EmotionResult> {
        try {
            const res = await fetcher(`/results/${id}`, {
                method: "GET",
                retry: 1,
            });

            const data = await res.json<EmotionResult>();
            return data;
        } catch (error: unknown) {
            const err = error as Error;
            throw new Error(err.message || "An error occurred while fetching emotion result.");
        }
    }

    async function remove(id: number){
        try {
            await fetcher(`/results/${id}`, {
                method: "DELETE",
                retry: 1,
            });
            return;
        } catch (error: unknown) {
            const err = error as Error;
            throw new Error(err.message || "An error occurred while deleting emotion result.");
        }
    }

    return {getAll, get, remove};
}

export {useEmotionAPI}
