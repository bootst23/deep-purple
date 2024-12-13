declare module '@/services/AuthenticationService.js' {
    interface Credentials {
      email: string;
      password: string;
      profile: string;
    }

    interface LoginResponse {
      token: string;
      user: {
        id: string;
        name: string;
        email: string;
      };
    }
  
    const AuthenticationService: {
      login(credentials: Credentials): Promise<LoginResponse>;
    };
  
    export default AuthenticationService;
  }
  