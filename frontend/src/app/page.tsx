"use client";

import React from 'react';
import {
  Rocket,
  Book,
  Clock,
  ArrowRight,
  TrendingUp,
  FileText,
  Activity
} from 'lucide-react';

export default function Dashboard() {
  const stats = [
    { label: 'Gelernte Wörter', value: '1,240', trend: '+12%', icon: Book, color: '#6366f1' },
    { label: 'Sitzungszeit', value: '14.5h', trend: '+5%', icon: Clock, color: '#ec4899' },
    { label: 'Fortschritt', value: '62%', trend: '+8%', icon: TrendingUp, color: '#10b981' },
    { label: 'Dokumente', value: '8', trend: '0%', icon: FileText, color: '#8b5cf6' },
  ];

  return (
    <div className="fade-in">
      <div style={{ marginBottom: '40px' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>Dashboard</h1>
        <p style={{ color: '#94a3b8' }}>Verfolge deinen Fortschritt und starte neue Lerneinheiten.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '24px', marginBottom: '40px' }}>
        {stats.map((stat) => (
          <div key={stat.label} className="glass" style={{ padding: '24px', position: 'relative', overflow: 'hidden' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div style={{ padding: '10px', borderRadius: '12px', background: `${stat.color}20`, color: stat.color }}>
                <stat.icon size={24} />
              </div>
              <span style={{ fontSize: '0.8rem', fontWeight: 600, color: stat.trend.startsWith('+') ? 'var(--success)' : 'var(--foreground)' }}>
                {stat.trend}
              </span>
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
            <button style={{ color: 'var(--primary)', fontSize: '0.9rem', fontWeight: 600 }}>Alle anzeigen</button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {[1, 2, 3].map((i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '16px', borderRadius: '12px', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--card-border)' }}>
                <div style={{ height: '48px', width: '48px', borderRadius: '12px', background: 'var(--sidebar-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Activity size={20} color="var(--primary)" />
                </div>
                <div style={{ flex: 1 }}>
                  <p style={{ fontWeight: 600 }}>Grammatik-Übung: Modalverben</p>
                  <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Vor 2 Stunden abgeschlossen</p>
                </div>
                <div className="glass-pill">B1 Level</div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass" style={{ padding: '32px', background: 'linear-gradient(135deg, var(--primary), var(--accent))', border: 'none' }}>
          <Rocket size={40} color="white" style={{ marginBottom: '20px' }} />
          <h2 style={{ color: 'white', marginBottom: '12px', fontSize: '1.5rem' }}>Bereit für mehr?</h2>
          <p style={{ color: 'rgba(255, 255, 255, 0.8)', marginBottom: '24px', lineHeight: '1.6' }}>
            Starte eine neue Konversation mit dem KI-Tutor, um dein Vokabular zu festigen.
          </p>
          <button style={{ background: 'white', color: 'var(--primary)', padding: '12px 24px', borderRadius: '12px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
            Jetzt chatten <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
