export interface UserRegister {
  name: string;
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface AdminRegister {
  name: string;
  email: string;
  password: string;
  code: string;
}

export interface AdminLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: string;
  email: string;
  name: string;
  user_id: string;
}