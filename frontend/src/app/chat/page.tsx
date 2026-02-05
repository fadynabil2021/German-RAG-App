"use client";

import React, { useState, useRef, useEffect, Suspense } from 'react';
import { Send, Bot, User, Sparkles, Languages, HelpCircle, BookOpen, Loader2, AlertCircle, ArrowLeft } from 'lucide-react';
import styles from './chat.module.css';
import { useAuth } from '@/context/AuthContext';
import api from '@/services/api';
import { useSearchParams, useRouter } from 'next/navigation';

interface Message {
    role: 'bot' | 'user';
    content: string;
    id: string;
    error?: boolean;
}

interface Project {
    project_id: number;
    project_name: string;
}

function ChatContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const projectId = searchParams.get('project');

    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [mode, setMode] = useState<'SOCRATIC' | 'GRAMMAR' | 'TRANSLATE'>('SOCRATIC');
    const [project, setProject] = useState<Project | null>(null);
    const [isLoadingProject, setIsLoadingProject] = useState(true);
    const { user } = useAuth();
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Load project on mount
    useEffect(() => {
        if (!projectId) {
            router.push('/projects');
            return;
        }

        const fetchProject = async () => {
            try {
                const response = await api.get(`/projects/${projectId}`);
                setProject(response.data);
                setMessages([
                    {
                        role: 'bot',
                        content: `Hallo! Ich bin dein Deutsch-Tutor für "${response.data.project_name}". Wie kann ich dir heute helfen?`,
                        id: '1'
                    }
                ]);
            } catch (err) {
                console.error('Failed to load project:', err);
                router.push('/projects');
            } finally {
                setIsLoadingProject(false);
            }
        };

        fetchProject();
    }, [projectId, router]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isTyping || !project) return;

        const userMessage: Message = {
            role: 'user',
            content: input,
            id: Date.now().toString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsTyping(true);

        try {
            const response = await api.post(`/nlp/index/answer/${project.project_id}`, {
                text: input,
                limit: 3,
                mode: mode
            });

            const botMessage: Message = {
                role: 'bot',
                content: response.data.answer || 'Tut mir leid, ich konnte keine Antwort generieren.',
                id: (Date.now() + 1).toString()
            };
            setMessages(prev => [...prev, botMessage]);
        } catch (err: any) {
            console.error('Chat error:', err);

            // Handle structured error responses
            let errorMessage = 'Es gab ein Problem bei der Verbindung zum Server.';
            if (err.response?.data?.message) {
                errorMessage = err.response.data.message;
            } else if (err.response?.data?.error_type === 'NO_INDEXED_DOCUMENTS') {
                errorMessage = 'Dieses Projekt hat noch keine indizierten Dokumente. Bitte laden Sie zuerst Dateien hoch.';
            }

            setMessages(prev => [...prev, {
                role: 'bot',
                content: errorMessage,
                id: Date.now().toString(),
                error: true
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    const modeLabels: Record<string, string> = {
        'SOCRATIC': 'Sokratisch',
        'GRAMMAR': 'Grammatik',
        'TRANSLATE': 'Übersetzen'
    };

    if (isLoadingProject) {
        return (
            <div className={styles.chatContainer} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Loader2 className="animate-spin" size={40} color="var(--primary)" />
            </div>
        );
    }

    if (!project) {
        return (
            <div className={styles.chatContainer} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <AlertCircle size={40} color="var(--error)" />
                <p style={{ marginTop: '16px', color: 'var(--error)' }}>Projekt nicht gefunden</p>
                <button
                    onClick={() => router.push('/projects')}
                    style={{ marginTop: '16px', padding: '8px 16px', background: 'var(--primary)', color: 'white', borderRadius: '8px', border: 'none', cursor: 'pointer' }}
                >
                    Zurück zu Projekten
                </button>
            </div>
        );
    }

    return (
        <div className={styles.chatContainer}>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <div>
                    <button
                        onClick={() => router.push('/projects')}
                        style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px', fontSize: '0.85rem' }}
                    >
                        <ArrowLeft size={14} /> Zurück zu Projekten
                    </button>
                    <h1 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Sparkles color="var(--primary)" /> {project.project_name}
                    </h1>
                    <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                        Modus: <span style={{ color: 'var(--primary)', fontWeight: 600 }}>{modeLabels[mode]}</span>
                    </p>
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                        onClick={() => setMode('TRANSLATE')}
                        disabled={isTyping}
                        className="glass-pill"
                        style={{
                            display: 'flex', alignItems: 'center', gap: '6px',
                            background: mode === 'TRANSLATE' ? 'var(--primary)' : '',
                            border: mode === 'TRANSLATE' ? 'none' : '',
                            opacity: isTyping ? 0.5 : 1,
                            cursor: isTyping ? 'not-allowed' : 'pointer'
                        }}
                    >
                        <Languages size={14} /> Übersetzen
                    </button>
                    <button
                        onClick={() => setMode('GRAMMAR')}
                        disabled={isTyping}
                        className="glass-pill"
                        style={{
                            display: 'flex', alignItems: 'center', gap: '6px',
                            background: mode === 'GRAMMAR' ? 'var(--primary)' : '',
                            border: mode === 'GRAMMAR' ? 'none' : '',
                            opacity: isTyping ? 0.5 : 1,
                            cursor: isTyping ? 'not-allowed' : 'pointer'
                        }}
                    >
                        <BookOpen size={14} /> Grammatik
                    </button>
                    <button
                        onClick={() => setMode('SOCRATIC')}
                        disabled={isTyping}
                        className="glass-pill"
                        style={{
                            display: 'flex', alignItems: 'center', gap: '6px',
                            background: mode === 'SOCRATIC' ? 'var(--primary)' : '',
                            border: mode === 'SOCRATIC' ? 'none' : '',
                            opacity: isTyping ? 0.5 : 1,
                            cursor: isTyping ? 'not-allowed' : 'pointer'
                        }}
                    >
                        <HelpCircle size={14} /> Sokratisch
                    </button>
                </div>
            </header>

            <div className={`${styles.messageArea} glass`}>
                {messages.map((m) => (
                    <div key={m.id} className={`${styles.message} ${m.role === 'bot' ? styles.botMessage : styles.userMessage} ${m.error ? styles.errorMessage : ''} fade-in`}>
                        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                            <div style={{ marginTop: '4px' }}>
                                {m.role === 'bot' ? (
                                    m.error ? <AlertCircle size={18} color="var(--error)" /> : <Bot size={18} />
                                ) : <User size={18} />}
                            </div>
                            <div>
                                <p style={{ fontSize: '0.75rem', opacity: 0.7, marginBottom: '4px', fontWeight: 600 }}>
                                    {m.role === 'bot' ? 'G-RAG Tutor' : 'Du'}
                                </p>
                                <div
                                    style={{ color: m.error ? 'var(--error)' : 'inherit' }}
                                    dangerouslySetInnerHTML={{ __html: m.content.replace(/\n/g, '<br/>') }}
                                />
                            </div>
                        </div>
                    </div>
                ))}
                {isTyping && (
                    <div className={`${styles.message} styles.botMessage fade-in`} style={{ display: 'flex', gap: '10px', alignItems: 'center', background: 'none', border: 'none' }}>
                        <Loader2 className="animate-spin" size={18} color="var(--primary)" />
                        <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>Tutor denkt nach...</span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className={`${styles.inputWrapper} glass`}>
                <form onSubmit={handleSend} style={{ display: 'flex', width: '100%', gap: '12px' }}>
                    <input
                        className={styles.chatInput}
                        placeholder="Schreibe etwas auf Deutsch..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={isTyping}
                    />
                    <button type="submit" className={styles.sendBtn} disabled={!input.trim() || isTyping}>
                        {isTyping ? <Loader2 className="animate-spin" /> : <Send size={24} />}
                    </button>
                </form>
            </div>
            <div className={styles.statusIndicator}>
                <div className={styles.statusDot} />
                System bereit • Level: {user?.proficiency_level} • Modus: {modeLabels[mode]}
            </div>
        </div>
    );
}

export default function ChatPage() {
    return (
        <Suspense fallback={
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <Loader2 className="animate-spin" size={40} color="var(--primary)" />
            </div>
        }>
            <ChatContent />
        </Suspense>
    );
}
