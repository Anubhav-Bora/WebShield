import apiClient from './api'

export interface LoginCredentials {
    username: string
    password: string
}

export interface RegisterData {
    email: string
    username: string
    full_name: string
    password: string
}

export interface User {
    id: string
    email: string
    username: string
    full_name: string
    is_active: boolean
    created_at: string
    last_login: string | null
}

export interface AuthResponse {
    access_token: string
    token_type: string
}

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const { data } = await apiClient.post('/auth/login', credentials)
    return data
}

export const register = async (userData: RegisterData): Promise<User> => {
    const { data } = await apiClient.post('/auth/register', userData)
    return data
}

export const getCurrentUser = async (): Promise<User> => {
    const { data } = await apiClient.get('/auth/me')
    return data
}

export const logout = async (): Promise<void> => {
    await apiClient.post('/auth/logout')
}
