"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import styles from './login.module.css';
import { Mail, Lock, Languages, Loader2 } from 'lucide-react';
import api from '@/services/api';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');

    const { login } = useAuth();
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!email || !password) {
            setError('Bitte geben Sie E-Mail und Passwort ein.');
            return;
        }

        setIsSubmitting(true);
        setError('');

        try {
            // 1. Authenticate and get token
            const loginResponse = await api.post('/auth/login', { email, password });
            const { access_token } = loginResponse.data;

            // Temporary set token to allow following request
            localStorage.setItem('minirag_token', access_token);

            // 2. Fetch user profile
            const userResponse = await api.get('/auth/me');

            login(access_token, userResponse.data);
            router.push('/');
        } catch (err: any) {
            console.error('Login error:', err);
            if (err.response?.status === 401) {
                setError('Ungültige E-Mail oder Passwort.');
            } else {
                setError('Ein interner Fehler ist aufgetreten. Bitte später versuchen.');
            }
            localStorage.removeItem('minirag_token');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className={styles.loginWrapper}>
            <div className={`${styles.loginCard} glass fade-in`}>
                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px' }}>
                    <div style={{ background: 'var(--primary)', padding: '12px', borderRadius: '16px', boxShadow: '0 0 20px var(--primary-glow)' }}>
                        <Languages color="white" size={32} />
                    </div>
                </div>

                <h1 className={styles.loginTitle}>G-RAG Tutor</h1>
                <p className={styles.loginSubtitle}>Lerne Deutsch mit künstlicher Intelligenz</p>

                {error && (
                    <div style={{
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid var(--error)',
                        color: 'var(--error)',
                        padding: '12px',
                        borderRadius: '8px',
                        fontSize: '0.9rem',
                        marginBottom: '10px'
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div className={styles.formGroup}>
                        <label className={styles.label}>E-Mail Adresse</label>
                        <div style={{ position: 'relative' }}>
                            <Mail size={18} color="#64748b" style={{ position: 'absolute', left: '14px', top: '14px' }} />
                            <input
                                type="email"
                                className={styles.input}
                                style={{ paddingLeft: '44px', width: '100%' }}
                                placeholder="name@beispiel.de"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    <div className={styles.formGroup}>
                        <label className={styles.label}>Passwort</label>
                        <div style={{ position: 'relative' }}>
                            <Lock size={18} color="#64748b" style={{ position: 'absolute', left: '14px', top: '14px' }} />
                            <input
                                type="password"
                                className={styles.input}
                                style={{ paddingLeft: '44px', width: '100%' }}
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    <button type="submit" className={styles.submitBtn} disabled={isSubmitting}>
                        {isSubmitting ? <Loader2 className="animate-spin" size={20} style={{ margin: '0 auto' }} /> : 'Anmelden'}
                    </button>
                </form>

                <p className={styles.footerText}>
                    Noch keinen Account? <a href="/register" className={styles.link}>Jetzt registrieren</a>
                </p>
            </div>
        </div>
    );
}
