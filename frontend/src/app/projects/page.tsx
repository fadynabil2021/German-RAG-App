"use client";

import React, { useState, useEffect } from 'react';
import { Plus, Upload, FileText, Trash2, ExternalLink, Library, Loader2, CheckCircle } from 'lucide-react';
import styles from './projects.module.css';
import api from '@/services/api';

interface Project {
    project_id: number;
    project_name: string;
    asset_count: number;
    created_at: string;
}

export default function ProjectsPage() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isUploading, setIsUploading] = useState(false);

    useEffect(() => {
        // Mock projects for demo
        const mockProjects: Project[] = [
            { project_id: 1, project_name: 'Meine ersten Lektionen', asset_count: 5, created_at: '2026-01-20' },
            { project_id: 2, project_name: 'Grammatik B1', asset_count: 3, created_at: '2026-01-25' },
        ];

        setTimeout(() => {
            setProjects(mockProjects);
            setIsLoading(false);
        }, 800);
    }, []);

    const handleUpload = () => {
        setIsUploading(true);
        setTimeout(() => {
            setIsUploading(false);
            alert('Datei erfolgreich hochgeladen und verarbeitet!');
        }, 2000);
    };

    return (
        <div className="fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
                <div>
                    <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>Meine Lernprojekte</h1>
                    <p style={{ color: '#94a3b8' }}>Verwalte deine Dokumente und PDF-Materialien.</p>
                </div>
                <button className={styles.btnPrimary}>
                    <Plus size={20} /> Neues Projekt
                </button>
            </div>

            <div className={styles.uploadZone}>
                <div style={{ background: 'rgba(99, 102, 241, 0.1)', padding: '20px', borderRadius: '50%', color: 'var(--primary)', marginBottom: '10px' }}>
                    {isUploading ? <Loader2 className="animate-spin" size={32} /> : <Upload size={32} />}
                </div>
                <div style={{ textAlign: 'center' }}>
                    <h3 style={{ fontSize: '1.25rem', marginBottom: '4px' }}>Dateien hochladen</h3>
                    <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>PDF oder TXT Dateien hierher ziehen oder klicken.</p>
                </div>
                <input type="file" style={{ display: 'none' }} id="fileUpload" onChange={handleUpload} />
                <label htmlFor="fileUpload" className={styles.btnPrimary} style={{ marginTop: '10px', cursor: 'pointer' }}>
                    Datei auswählen
                </label>
            </div>

            <h2 style={{ fontSize: '1.25rem', marginBottom: '24px' }}>Aktive Projekte</h2>

            {isLoading ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '100px' }}>
                    <Loader2 className="animate-spin" size={40} color="var(--primary)" />
                </div>
            ) : (
                <div className={styles.grid}>
                    {projects.map((proj) => (
                        <div key={proj.project_id} className={`${styles.card} glass`}>
                            <div className={styles.cardHeader}>
                                <div className={styles.iconBox}>
                                    <Library size={24} />
                                </div>
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <button style={{ color: '#94a3b8' }}><Trash2 size={18} /></button>
                                    <button style={{ color: '#94a3b8' }}><ExternalLink size={18} /></button>
                                </div>
                            </div>

                            <h3 style={{ fontSize: '1.2rem', marginBottom: '4px' }}>{proj.project_name}</h3>
                            <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Erstellt am {proj.created_at}</p>

                            <div className={styles.statsRow}>
                                <div className={styles.stat}>
                                    <p className={styles.statLabel}>Assets</p>
                                    <p className={styles.statValue}>{proj.asset_count} Dateien</p>
                                </div>
                                <div className={styles.stat}>
                                    <p className={styles.statLabel}>Status</p>
                                    <p className={styles.statValue} style={{ color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                        <CheckCircle size={14} /> Bereit
                                    </p>
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '8px' }}>
                                <button
                                    className={styles.btnPrimary}
                                    style={{ flex: 1, justifyContent: 'center', background: 'rgba(99, 102, 241, 0.1)', color: 'var(--primary)', border: '1px solid rgba(99, 102, 241, 0.2)' }}
                                >
                                    Details
                                </button>
                                <button className={styles.btnPrimary} style={{ flex: 1, justifyContent: 'center' }}>
                                    Lernen
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
