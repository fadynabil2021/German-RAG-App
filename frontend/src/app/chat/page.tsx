"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Languages, HelpCircle, BookOpen, Loader2 } from 'lucide-react';
import styles from './chat.module.css';
import { useAuth } from '@/context/AuthContext';
import api from '@/services/api';

interface Message {
    role: 'bot' | 'user';
    content: string;
    id: string;
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([
        { role: 'bot', content: 'Hallo! Ich bin dein Deutsch-Tutor. Wie kann ich dir heute helfen?', id: '1' }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const { user } = useAuth();
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isTyping) return;

        const userMessage: Message = {
            role: 'user',
            content: input,
            id: Date.now().toString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsTyping(true);

        try {
            // API call to Backend
            // For Demo, since we might not have a project yet, we use a fallback or specific project ID
            const response = await api.post('/nlp/index/answer/1', {
                text: input,
                limit: 3
            });

            const botMessage: Message = {
                role: 'bot',
                content: response.data.answer || 'Tut mir leid, ich konnte keine Antwort generieren.',
                id: (Date.now() + 1).toString()
            };
            setMessages(prev => [...prev, botMessage]);
        } catch (err) {
            console.error('Chat error:', err);
            setMessages(prev => [...prev, {
                role: 'bot',
                content: 'Es gab ein Problem bei der Verbindung zum Server. Bist du sicher, dass das Backend läuft?',
                id: Date.now().toString()
            }]);
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className={styles.chatContainer}>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <div>
                    <h1 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <Sparkles color="var(--primary)" /> KI-Deutsch Tutor
                    </h1>
                    <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Aktueller Modus: <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Sokratisch</span></p>
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="glass-pill" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><Languages size={14} /> Übersetzen</button>
                    <button className="glass-pill" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><BookOpen size={14} /> Grammatik</button>
                    <button className="glass-pill" style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'var(--primary)', border: 'none' }}><HelpCircle size={14} /> Sokratisch</button>
                </div>
            </header>

            <div className={`${styles.messageArea} glass`}>
                {messages.map((m) => (
                    <div key={m.id} className={`${styles.message} ${m.role === 'bot' ? styles.botMessage : styles.userMessage} fade-in`}>
                        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                            <div style={{ marginTop: '4px' }}>
                                {m.role === 'bot' ? <Bot size={18} /> : <User size={18} />}
                            </div>
                            <div>
                                <p style={{ fontSize: '0.75rem', opacity: 0.7, marginBottom: '4px', fontWeight: 600 }}>
                                    {m.role === 'bot' ? 'G-RAG Tutor' : 'Du'}
                                </p>
                                <div dangerouslySetInnerHTML={{ __html: m.content.replace(/\n/g, '<br/>') }} />
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
                System bereit • Level: {user?.proficiency_level}
            </div>
        </div>
    );
}
