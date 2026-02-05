"use client";

import React from 'react';
import { Book, CheckCircle2, ChevronRight, Info } from 'lucide-react';

const topics = [
    { title: 'Die Artikel (der, die, das)', level: 'A1', description: 'Grundregeln für grammatikalische Geschlechter im Deutschen.' },
    { title: 'Verbkonjugation (Präsens)', level: 'A1', description: 'Regelmäßige und unregelmäßige Verben im Präsens.' },
    { title: 'Die vier Fälle (Kasus)', level: 'A2', description: 'Nominativ, Akkusativ, Dativ und Genitiv einfach erklärt.' },
    { title: 'Modalverben', level: 'A2', description: 'können, müssen, dürfen, sollen, wollen, mögen.' },
    { title: 'Perfekt & Präteritum', level: 'B1', description: 'Wann benutzt man welches Tempus für die Vergangenheit?' },
    { title: 'Passivformen', level: 'B1', description: 'Vorgangspassiv vs. Zustandspassiv.' },
    { title: 'Konjunktiv II', level: 'B2', description: 'Wünsche, Hypothesen und Höflichkeit ausdrücken.' },
];

export default function GrammarPage() {
    return (
        <div className="fade-in">
            <div style={{ marginBottom: '40px' }}>
                <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>Grammatik-Leitfaden</h1>
                <p style={{ color: '#94a3b8' }}>Schnelle Referenz für die wichtigsten Konzepte der deutschen Grammatik.</p>
            </div>

            <div className="glass" style={{ padding: '24px', marginBottom: '32px', background: 'rgba(99, 102, 241, 0.05)', display: 'flex', gap: '16px', alignItems: 'center' }}>
                <Info color="var(--primary)" />
                <p style={{ fontSize: '0.9rem' }}>
                    Benutze den <strong>AI Tutor</strong> im Grammatik-Modus, um personalisierte Erklärungen zu deinen Dokumenten zu erhalten.
                </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))', gap: '24px' }}>
                {topics.map((topic) => (
                    <div key={topic.title} className="glass" style={{ padding: '24px', cursor: 'default', transition: 'transform 0.2s' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                            <div style={{ padding: '8px', borderRadius: '10px', background: 'rgba(255,255,255,0.05)', color: 'var(--primary)' }}>
                                <Book size={20} />
                            </div>
                            <span className="glass-pill">{topic.level}</span>
                        </div>
                        <h3 style={{ fontSize: '1.2rem', marginBottom: '8px' }}>{topic.title}</h3>
                        <p style={{ fontSize: '0.9rem', color: '#94a3b8', lineHeight: '1.5', marginBottom: '20px' }}>
                            {topic.description}
                        </p>
                        <button style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            color: 'var(--primary)',
                            background: 'none',
                            border: 'none',
                            fontWeight: 600,
                            fontSize: '0.9rem',
                            padding: 0
                        }}>
                            Details ansehen <ChevronRight size={16} />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}
