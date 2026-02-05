"use client";

import React, { useState, useEffect } from 'react';
import { WifiOff, RefreshCw, Loader2 } from 'lucide-react';
import { checkBackendHealth, getApiBaseUrl } from '@/services/api';

export default function BackendStatusBanner() {
    const [isConnected, setIsConnected] = useState<boolean | null>(null);
    const [isChecking, setIsChecking] = useState(false);

    const checkConnection = async () => {
        setIsChecking(true);
        const healthy = await checkBackendHealth();
        setIsConnected(healthy);
        setIsChecking(false);
    };

    useEffect(() => {
        checkConnection();
        // Re-check every 30 seconds
        const interval = setInterval(checkConnection, 30000);
        return () => clearInterval(interval);
    }, []);

    if (isConnected === null || isConnected) {
        return null;
    }

    return (
        <div style={{
            background: 'linear-gradient(90deg, #dc2626, #b91c1c)',
            color: 'white',
            padding: '12px 20px',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '12px',
            fontSize: '0.9rem',
            fontWeight: 500,
        }}>
            <WifiOff size={18} />
            <span>Backend nicht erreichbar ({getApiBaseUrl()})</span>
            <button
                onClick={checkConnection}
                disabled={isChecking}
                style={{
                    background: 'rgba(255,255,255,0.2)',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    color: 'white',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                }}
            >
                {isChecking ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                Erneut versuchen
            </button>
        </div>
    );
}
