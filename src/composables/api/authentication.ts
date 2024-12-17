import { fetcher } from "@/composables/utils/fetcher";
import type { AuthResponse } from "@/types/auth";

function useAuthAPI() {
    async function login(email: string, password: string): Promise<AuthResponse> {
        try {
            const res = await fetcher("/login", {
                method: "POST",
                retry: 1,
                json: {credentials: {email, password}}
            });

            const data = await res.json<AuthResponse>();
            return data;
        } catch (error: unknown) {
            const err = error as Error;
            throw new Error(err.message || "An error occurred while logging in.");
        }
    }

    return {login}
}

export {useAuthAPI}
