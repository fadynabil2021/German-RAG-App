"use client";

import React from 'react';
import Sidebar from './Sidebar';
import styles from './layout.module.css';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import BackendStatusBanner from '@/components/BackendStatusBanner';
import DevDebugPanel from '@/components/DevDebugPanel';

export default function AppLayout({ children }: { children: React.ReactNode }) {
    const { user, authStatus } = useAuth();
    const router = useRouter();

    React.useEffect(() => {
        if (authStatus === 'unauthenticated') {
            const publicPaths = ['/login', '/register'];
            if (!publicPaths.includes(window.location.pathname)) {
                router.push('/login');
            }
        }
    }, [authStatus, router]);

    if (authStatus === 'loading') {
        return (
            <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--background)' }}>
                <div className="animate-pulse-subtle" style={{ color: 'var(--primary)', fontSize: '1.2rem', fontWeight: 600 }}>Loading G-RAG...</div>
            </div>
        );
    }

    if (!user && (window.location.pathname === '/login' || window.location.pathname === '/register')) {
        return <>{children}</>;
    }

    if (!user) return null;

    return (
        <div className={styles.mainContainer}>
            <Sidebar />
            <main className={styles.content}>
                <BackendStatusBanner />
                <header className={styles.topbar}>
                    <div style={{ fontSize: '0.9rem', color: '#94a3b8' }}>
                        Willkommen zurück, <span style={{ color: 'var(--foreground)', fontWeight: 600 }}>{user.email.split('@')[0]}</span>
                    </div>
                    <div className={styles.userBadge}>
                        <div style={{ textAlign: 'right' }}>
                            <p style={{ fontSize: '0.85rem', fontWeight: 600 }}>{user.email.split('@')[0]}</p>
                            <p style={{ fontSize: '0.7rem', color: 'var(--primary)', fontWeight: 700 }}>{user.proficiency_level}</p>
                        </div>
                        <div className={styles.avatar} />
                    </div>
                </header>
                <div style={{ flex: 1, padding: '32px', overflowY: 'auto' }}>
                    {children}
                </div>
            </main>
            <DevDebugPanel />
        </div>
    );
}
