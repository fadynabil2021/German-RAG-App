"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import styles from '../login/login.module.css';
import { Mail, Lock, Languages, Loader2, User as UserIcon } from 'lucide-react';
import api from '@/services/api';

export default function RegisterPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [proficiency, setProficiency] = useState('A1');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');

    const { login } = useAuth();
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('Passwörter stimmen nicht überein.');
            return;
        }

        setIsSubmitting(true);

        try {
            // 1. Register User
            await api.post('/auth/register', {
                email,
                password,
                proficiency_level: proficiency
            });

            // 2. Login immediately
            const loginResponse = await api.post('/auth/login', { email, password });
            const { access_token } = loginResponse.data;

            localStorage.setItem('minirag_token', access_token);
            const userResponse = await api.get('/auth/me');

            login(access_token, userResponse.data);
            router.push('/');
        } catch (err: any) {
            console.error('Registration error:', err);
            if (err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Registrierung fehlgeschlagen. Bitte versuchen Sie es erneut.');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className={styles.loginWrapper}>
            <div className={`${styles.loginCard} glass fade-in`} style={{ maxWidth: '480px' }}>
                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px' }}>
                    <div style={{ background: 'var(--accent)', padding: '12px', borderRadius: '16px', boxShadow: '0 0 20px rgba(139, 92, 246, 0.5)' }}>
                        <UserIcon color="white" size={32} />
                    </div>
                </div>

                <h1 className={styles.loginTitle}>Registrieren</h1>
                <p className={styles.loginSubtitle}>Starte heute dein Deutsch-Abenteuer</p>

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

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
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

                    <div style={{ display: 'flex', gap: '16px' }}>
                        <div className={styles.formGroup} style={{ flex: 1 }}>
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

                        <div className={styles.formGroup} style={{ flex: 1 }}>
                            <label className={styles.label}>Bestätigen</label>
                            <div style={{ position: 'relative' }}>
                                <Lock size={18} color="#64748b" style={{ position: 'absolute', left: '14px', top: '14px' }} />
                                <input
                                    type="password"
                                    className={styles.input}
                                    style={{ paddingLeft: '44px', width: '100%' }}
                                    placeholder="••••••••"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    required
                                />
                            </div>
                        </div>
                    </div>

                    <div className={styles.formGroup}>
                        <label className={styles.label}>Aktuelles Sprachniveau (GER)</label>
                        <select
                            className={styles.input}
                            value={proficiency}
                            onChange={(e) => setProficiency(e.target.value)}
                            style={{ width: '100%', appearance: 'none', background: 'var(--input-bg)' }}
                        >
                            <option value="A1">A1 - Anfänger</option>
                            <option value="A2">A2 - Grundlagen</option>
                            <option value="B1">B1 - Fortgeschrittene</option>
                            <option value="B2">B2 - Selbstständig</option>
                            <option value="C1">C1 - Fachkundig</option>
                            <option value="C2">C2 - Annähernd muttersprachlich</option>
                        </select>
                    </div>

                    <button type="submit" className={styles.submitBtn} disabled={isSubmitting} style={{ background: 'linear-gradient(135deg, var(--accent), var(--secondary))' }}>
                        {isSubmitting ? <Loader2 className="animate-spin" size={20} style={{ margin: '0 auto' }} /> : 'Konto erstellen'}
                    </button>
                </form>

                <p className={styles.footerText}>
                    Bereits ein Konto? <a href="/login" className={styles.link}>Hier anmelden</a>
                </p>
            </div>
        </div>
    );
}
