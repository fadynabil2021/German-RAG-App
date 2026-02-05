"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '@/services/api';

interface User {
    user_id: number;
    email: string;
    role: string;
    proficiency_level: string;
}

type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

interface AuthContextType {
    user: User | null;
    token: string | null;
    authStatus: AuthStatus;
    login: (token: string, userData: User) => void;
    logout: () => void;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [authStatus, setAuthStatus] = useState<AuthStatus>('loading');

    const clearAuth = useCallback(() => {
        setToken(null);
        setUser(null);
        setAuthStatus('unauthenticated');
        localStorage.removeItem('minirag_token');
        localStorage.removeItem('minirag_user');
    }, []);

    const refreshUser = useCallback(async () => {
        const savedToken = localStorage.getItem('minirag_token');
        if (!savedToken) {
            clearAuth();
            return;
        }

        try {
            const response = await api.get('/auth/me');
            const userData: User = {
                user_id: response.data.user_id,
                email: response.data.email,
                role: response.data.role,
                proficiency_level: response.data.proficiency_level,
            };
            setUser(userData);
            setToken(savedToken);
            setAuthStatus('authenticated');
            localStorage.setItem('minirag_user', JSON.stringify(userData));
        } catch (err) {
            console.error('Failed to refresh user - forcing logout:', err);
            clearAuth();
        }
    }, [clearAuth]);

    useEffect(() => {
        refreshUser();
    }, [refreshUser]);

    const login = (newToken: string, userData: User) => {
        setToken(newToken);
        setUser(userData);
        setAuthStatus('authenticated');
        localStorage.setItem('minirag_token', newToken);
        localStorage.setItem('minirag_user', JSON.stringify(userData));
    };

    const logout = () => {
        clearAuth();
    };

    return (
        <AuthContext.Provider value={{ user, token, authStatus, login, logout, refreshUser }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
