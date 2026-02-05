"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    MessageSquare,
    Library,
    Settings,
    LogOut,
    BookOpen,
    User as UserIcon,
    ShieldCheck,
    Trophy
} from 'lucide-react';
import styles from './layout.module.css';
import { useAuth } from '@/context/AuthContext';

export default function Sidebar() {
    const pathname = usePathname();
    const { user, logout } = useAuth();

    const navItems = [
        { name: 'Dashboard', href: '/', icon: LayoutDashboard },
        { name: 'AI Tutor', href: '/chat', icon: MessageSquare },
        { name: 'My Projects', href: '/projects', icon: Library },
        { name: 'Learning Path', href: '/learning-path', icon: Trophy },
        { name: 'Grammar Guide', href: '/grammar', icon: BookOpen },
    ];

    const adminItems = [
        { name: 'Admin Panel', href: '/admin', icon: ShieldCheck },
    ];

    return (
        <aside className={styles.sidebar}>
            <div className={styles.logo}>
                <div className={styles.logoDot} />
                <span>G-RAG Tutor</span>
            </div>

            <nav style={{ flex: 1 }}>
                <p style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '16px', fontWeight: 600, textTransform: 'uppercase' }}>Menu</p>
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link key={item.name} href={item.href} className={`${styles.navItem} ${isActive ? styles.navItemActive : ''}`}>
                            <item.icon size={20} />
                            <span>{item.name}</span>
                        </Link>
                    );
                })}

                {user?.role === 'admin' && (
                    <>
                        <p style={{ fontSize: '0.75rem', color: '#64748b', margin: '24px 0 16px', fontWeight: 600, textTransform: 'uppercase' }}>System</p>
                        {adminItems.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link key={item.name} href={item.href} className={`${styles.navItem} ${isActive ? styles.navItemActive : ''}`}>
                                    <item.icon size={20} />
                                    <span>{item.name}</span>
                                </Link>
                            );
                        })}
                    </>
                )}
            </nav>

            <div style={{ borderTop: '1px solid var(--card-border)', paddingTop: '24px' }}>
                <Link href="/profile" className={styles.navItem}>
                    <UserIcon size={20} />
                    <span>Profile</span>
                </Link>
                <button onClick={logout} className={styles.navItem} style={{ width: '100%', cursor: 'pointer' }}>
                    <LogOut size={20} />
                    <span>Sign Out</span>
                </button>
            </div>
        </aside>
    );
}
