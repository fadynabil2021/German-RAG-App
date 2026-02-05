"use client";

import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { CheckCircle2, Circle, Star, Target, Trophy, ArrowRight } from 'lucide-react';

const levels = [
    { id: 'A1', name: 'Anfänger (A1)', status: 'completed', topics: ['Grundwortschatz', 'Satzbau', 'Zahlen & Zeit'] },
    { id: 'A2', name: 'Grundlegende Kenntnisse (A2)', status: 'active', topics: ['Vergangenheit', 'Modalverben', 'Nebensätze'] },
    { id: 'B1', name: 'Fortgeschrittene Sprachverwendung (B1)', status: 'locked', topics: ['Passiv', 'Konjunktiv II', 'Textverständnis'] },
    { id: 'B2', name: 'Selbstständige Sprachverwendung (B2)', status: 'locked', topics: ['Abstraktes Denken', 'Debatten', 'Komplexe Texte'] },
    { id: 'C1', name: 'Fachkundige Sprachkenntnisse (C1)', status: 'locked', topics: ['Akademisches Deutsch', 'Nuancen', 'Strukturierte Aufsätze'] },
    { id: 'C2', name: 'Annähernd muttersprachliche Kenntnisse (C2)', status: 'locked', topics: ['Perfektion', 'Literatur', 'Präzision'] },
];

export default function LearningPathPage() {
    const { user } = useAuth();

    // In a real app, status would come from user.proficiency_level
    const currentLevel = user?.proficiency_level || 'A1';

    return (
        <div className="fade-in">
            <div style={{ marginBottom: '40px' }}>
                <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>Mein Lernpfad</h1>
                <p style={{ color: '#94a3b8' }}>Dein Weg zur Meisterschaft der deutschen Sprache.</p>
            </div>

            <div style={{ display: 'grid', gap: '24px' }}>
                {levels.map((level, index) => {
                    const isCompleted = index < levels.findIndex(l => l.id === currentLevel);
                    const isActive = level.id === currentLevel;
                    const isLocked = !isCompleted && !isActive;

                    return (
                        <div
                            key={level.id}
                            className="glass"
                            style={{
                                padding: '32px',
                                borderLeft: isActive ? '4px solid var(--primary)' : '1px solid var(--card-border)',
                                opacity: isLocked ? 0.6 : 1,
                                position: 'relative'
                            }}
                        >
                            <div style={{ display: 'flex', gap: '24px', alignItems: 'flex-start' }}>
                                <div style={{
                                    width: '48px',
                                    height: '48px',
                                    borderRadius: '50%',
                                    background: isCompleted ? 'var(--success-glow)' : (isActive ? 'var(--primary-glow)' : 'rgba(255,255,255,0.05)'),
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: isCompleted ? 'var(--success)' : (isActive ? 'var(--primary)' : '#64748b')
                                }}>
                                    {isCompleted ? <CheckCircle2 size={24} /> : (isActive ? <Target size={24} /> : <Circle size={24} />)}
                                </div>

                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                                        <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>{level.name}</h2>
                                        {isActive && <div className="glass-pill" style={{ background: 'var(--primary)', color: 'white', border: 'none' }}>Aktuell</div>}
                                        {isCompleted && <div className="glass-pill" style={{ color: 'var(--success)' }}>Abgeschlossen</div>}
                                    </div>

                                    <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '20px' }}>
                                        {level.topics.map(topic => (
                                            <span key={topic} style={{ fontSize: '0.8rem', padding: '4px 12px', borderRadius: '100px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--card-border)' }}>
                                                {topic}
                                            </span>
                                        ))}
                                    </div>

                                    {isActive && (
                                        <div style={{
                                            background: 'rgba(99, 102, 241, 0.05)',
                                            padding: '16px',
                                            borderRadius: '12px',
                                            border: '1px solid rgba(99, 102, 241, 0.1)',
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            alignItems: 'center'
                                        }}>
                                            <div>
                                                <p style={{ fontWeight: 600, fontSize: '0.9rem' }}>Nächster Meilenstein: Passiv & Konjunktiv</p>
                                                <div style={{ width: '200px', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '10px', marginTop: '8px', overflow: 'hidden' }}>
                                                    <div style={{ width: '65%', height: '100%', background: 'var(--primary)' }} />
                                                </div>
                                            </div>
                                            <button style={{ background: 'var(--primary)', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '8px', fontWeight: 600, fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                Lektion fortsetzen <ArrowRight size={16} />
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {index < levels.length - 1 && (
                                <div style={{
                                    position: 'absolute',
                                    left: '55px',
                                    bottom: '-24px',
                                    width: '2px',
                                    height: '24px',
                                    background: isCompleted ? 'var(--success)' : 'var(--card-border)',
                                    opacity: 0.3
                                }} />
                            )}
                        </div>
                    );
                })}
            </div>

            <div className="glass" style={{ marginTop: '40px', padding: '32px', textAlign: 'center', background: 'linear-gradient(to right, rgba(236, 72, 153, 0.05), rgba(99, 102, 241, 0.05))' }}>
                <Trophy size={48} color="#f59e0b" style={{ margin: '0 auto 20px' }} />
                <h2 style={{ fontSize: '1.5rem', marginBottom: '12px' }}>Bereit für den C2 Master?</h2>
                <p style={{ color: '#94a3b8', maxWidth: '600px', margin: '0 auto 24px' }}>
                    Bleib am Ball! Mit täglichem Üben und der Unterstützung deiner Dokumente wirst du die deutsche Sprache in Rekordzeit meistern.
                </p>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Star size={18} color="#f59e0b" fill="#f59e0b" />
                        <span style={{ fontWeight: 600 }}>Tagesziel erreicht</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Star size={18} color="#f59e0b" fill="#f59e0b" />
                        <span style={{ fontWeight: 600 }}>7-Tage Streak</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
