"use client";

import React, { useState } from 'react';
import { Bug, X, ChevronDown, ChevronUp } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { getApiBaseUrl } from '@/services/api';

interface DevPanelProps {
    activeProject?: { project_id: number; project_name: string } | null;
    currentMode?: string;
}

export default function DevDebugPanel({ activeProject, currentMode }: DevPanelProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(true);
    const { user, authStatus } = useAuth();

    // Only show in development
    if (process.env.NODE_ENV !== 'development') {
        return null;
    }

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                style={{
                    position: 'fixed',
                    bottom: '20px',
                    right: '20px',
                    background: '#1e293b',
                    color: '#f59e0b',
                    border: '1px solid #f59e0b',
                    borderRadius: '50%',
                    width: '48px',
                    height: '48px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    zIndex: 9999,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
                }}
                title="Open Dev Panel"
            >
                <Bug size={20} />
            </button>
        );
    }

    return (
        <div style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            background: '#0f172a',
            border: '1px solid #334155',
            borderRadius: '12px',
            width: '320px',
            zIndex: 9999,
            boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
            fontFamily: 'monospace',
            fontSize: '12px'
        }}>
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '12px 16px',
                borderBottom: isMinimized ? 'none' : '1px solid #334155',
                background: '#1e293b',
                borderRadius: isMinimized ? '12px' : '12px 12px 0 0'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#f59e0b' }}>
                    <Bug size={16} />
                    <span style={{ fontWeight: 600 }}>DEV DEBUG</span>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                        onClick={() => setIsMinimized(!isMinimized)}
                        style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}
                    >
                        {isMinimized ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </button>
                    <button
                        onClick={() => setIsOpen(false)}
                        style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}
                    >
                        <X size={16} />
                    </button>
                </div>
            </div>

            {!isMinimized && (
                <div style={{ padding: '16px' }}>
                    <div style={{ marginBottom: '16px' }}>
                        <p style={{ color: '#64748b', marginBottom: '4px' }}>Auth Status</p>
                        <p style={{
                            color: authStatus === 'authenticated' ? '#22c55e' : authStatus === 'loading' ? '#f59e0b' : '#ef4444'
                        }}>
                            {authStatus.toUpperCase()}
                        </p>
                    </div>

                    <div style={{ marginBottom: '16px' }}>
                        <p style={{ color: '#64748b', marginBottom: '4px' }}>User</p>
                        {user ? (
                            <div style={{ color: '#e2e8f0' }}>
                                <p>ID: {user.user_id}</p>
                                <p>Email: {user.email}</p>
                                <p>Level: {user.proficiency_level}</p>
                                <p>Role: {user.role}</p>
                            </div>
                        ) : (
                            <p style={{ color: '#94a3b8' }}>null</p>
                        )}
                    </div>

                    <div style={{ marginBottom: '16px' }}>
                        <p style={{ color: '#64748b', marginBottom: '4px' }}>Active Project</p>
                        {activeProject ? (
                            <div style={{ color: '#e2e8f0' }}>
                                <p>ID: {activeProject.project_id}</p>
                                <p>Name: {activeProject.project_name}</p>
                            </div>
                        ) : (
                            <p style={{ color: '#94a3b8' }}>none</p>
                        )}
                    </div>

                    <div style={{ marginBottom: '16px' }}>
                        <p style={{ color: '#64748b', marginBottom: '4px' }}>Current Mode</p>
                        <p style={{ color: '#e2e8f0' }}>{currentMode || 'N/A'}</p>
                    </div>

                    <div>
                        <p style={{ color: '#64748b', marginBottom: '4px' }}>API Base URL</p>
                        <p style={{ color: '#60a5fa', wordBreak: 'break-all' }}>{getApiBaseUrl()}</p>
                    </div>
                </div>
            )}
        </div>
    );
}
