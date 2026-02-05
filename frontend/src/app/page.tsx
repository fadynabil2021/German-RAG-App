"use client";

import React, { useState, useEffect } from 'react';
import {
  Rocket,
  Book,
  Clock,
  ArrowRight,
  TrendingUp,
  FileText,
  Activity,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import api from '@/services/api';

interface DashboardStats {
  words_learned: number;
  total_sessions: number;
  total_time_minutes: number;
  streak_days: number;
  project_count: number;
  message_count: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/dashboard/stats');
        setStats(response.data);
      } catch (err: any) {
        console.error('Failed to fetch dashboard stats:', err);
        setError('Statistiken konnten nicht geladen werden');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  const formatTime = (minutes: number): string => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  const statCards = stats ? [
    { label: 'Gelernte Wörter', value: stats.words_learned.toLocaleString(), trend: '', icon: Book, color: '#6366f1' },
    { label: 'Lernzeit', value: formatTime(stats.total_time_minutes), trend: '', icon: Clock, color: '#ec4899' },
    { label: 'Sitzungen', value: stats.total_sessions.toString(), trend: '', icon: TrendingUp, color: '#10b981' },
    { label: 'Projekte', value: stats.project_count.toString(), trend: '', icon: FileText, color: '#8b5cf6' },
  ] : [];

  if (isLoading) {
    return (
      <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
        <Loader2 className="animate-spin" size={40} color="var(--primary)" />
        <p style={{ marginTop: '16px', color: '#94a3b8' }}>Lade Dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
        <AlertCircle size={40} color="var(--error)" />
        <p style={{ marginTop: '16px', color: 'var(--error)' }}>{error}</p>
        <button
          onClick={() => window.location.reload()}
          style={{ marginTop: '16px', padding: '8px 16px', background: 'var(--primary)', color: 'white', borderRadius: '8px', border: 'none', cursor: 'pointer' }}
        >
          Erneut versuchen
        </button>
      </div>
    );
  }

  const hasActivity = stats && stats.message_count > 0;

  return (
    <div className="fade-in">
      <div style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>Dashboard</h1>
        <p style={{ color: '#94a3b8' }}>Verfolge deinen Fortschritt und starte neue Lerneinheiten.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '24px', marginBottom: '40px' }}>
        {statCards.map((stat) => (
          <div key={stat.label} className="glass" style={{ padding: '24px', position: 'relative', overflow: 'hidden' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div style={{ padding: '10px', borderRadius: '12px', background: `${stat.color}20`, color: stat.color }}>
                <stat.icon size={24} />
              </div>
            </div>
            <h3 style={{ fontSize: '1.75rem', marginBottom: '4px' }}>{stat.value}</h3>
            <p style={{ fontSize: '0.9rem', color: '#94a3b8' }}>{stat.label}</p>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        <div className="glass" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <h2 style={{ fontSize: '1.25rem' }}>Letzte Aktivitäten</h2>
          </div>

          {hasActivity ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '16px', borderRadius: '12px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--card-border)' }}>
                <div style={{ height: '48px', width: '48px', borderRadius: '12px', background: 'var(--sidebar-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Activity size={20} color="var(--primary)" />
                </div>
                <div style={{ flex: 1 }}>
                  <p style={{ fontWeight: 600 }}>{stats?.message_count} Nachrichten gesendet</p>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{stats?.streak_days} Tage Streak</p>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
              <Activity size={40} style={{ marginBottom: '16px', opacity: 0.5 }} />
              <p>Noch keine Lernaktivitäten.</p>
              <p style={{ fontSize: '0.85rem', marginTop: '8px' }}>Starte jetzt mit dem KI-Tutor!</p>
            </div>
          )}
        </div>

        <div className="glass" style={{ padding: '32px', background: 'linear-gradient(135deg, var(--primary), var(--accent))', border: 'none' }}>
          <Rocket size={40} color="white" style={{ marginBottom: '20px' }} />
          <h2 style={{ color: 'white', marginBottom: '12px', fontSize: '1.5rem' }}>Bereit für mehr?</h2>
          <p style={{ color: 'rgba(255, 255, 255, 0.8)', marginBottom: '24px', lineHeight: '1.6' }}>
            Starte eine neue Konversation mit dem KI-Tutor, um dein Vokabular zu festigen.
          </p>
          <button
            onClick={() => router.push('/projects')}
            style={{ background: 'white', color: 'var(--primary)', padding: '12px 24px', borderRadius: '12px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px', border: 'none', cursor: 'pointer' }}
          >
            Projekte öffnen <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
