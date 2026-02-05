"use client";

import React, { useState, useEffect } from 'react';
import { Plus, Upload, FileText, Trash2, MessageSquare, Library, Loader2, CheckCircle, AlertCircle, FolderPlus } from 'lucide-react';
import styles from './projects.module.css';
import api from '@/services/api';
import { useRouter } from 'next/navigation';

interface Project {
    project_id: number;
    project_name: string;
    project_description: string;
    asset_count: number;
    created_at: string;
}

export default function ProjectsPage() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isCreating, setIsCreating] = useState(false);
    const [newProjectName, setNewProjectName] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const router = useRouter();

    const fetchProjects = async () => {
        try {
            const response = await api.get('/projects');
            setProjects(response.data);
            setError(null);
        } catch (err: any) {
            console.error('Failed to fetch projects:', err);
            setError('Projekte konnten nicht geladen werden');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchProjects();
    }, []);

    const handleCreateProject = async () => {
        if (!newProjectName.trim()) return;

        setIsCreating(true);
        try {
            const response = await api.post('/projects', {
                project_name: newProjectName,
                project_description: ''
            });
            setProjects([response.data, ...projects]);
            setNewProjectName('');
            setShowCreateModal(false);
        } catch (err: any) {
            console.error('Failed to create project:', err);
            alert('Projekt konnte nicht erstellt werden');
        } finally {
            setIsCreating(false);
        }
    };

    const handleDeleteProject = async (projectId: number) => {
        if (!confirm('Möchten Sie dieses Projekt wirklich löschen?')) return;

        try {
            await api.delete(`/projects/${projectId}`);
            setProjects(projects.filter(p => p.project_id !== projectId));
        } catch (err) {
            console.error('Failed to delete project:', err);
            alert('Projekt konnte nicht gelöscht werden');
        }
    };

    const handleStartChat = (projectId: number) => {
        router.push(`/chat?project=${projectId}`);
    };

    if (isLoading) {
        return (
            <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
                <Loader2 className="animate-spin" size={40} color="var(--primary)" />
                <p style={{ marginTop: '16px', color: '#94a3b8' }}>Lade Projekte...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="fade-in" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
                <AlertCircle size={40} color="var(--error)" />
                <p style={{ marginTop: '16px', color: 'var(--error)' }}>{error}</p>
                <button
                    onClick={() => { setIsLoading(true); fetchProjects(); }}
                    style={{ marginTop: '16px', padding: '8px 16px', background: 'var(--primary)', color: 'white', borderRadius: '8px', border: 'none', cursor: 'pointer' }}
                >
                    Erneut versuchen
                </button>
            </div>
        );
    }

    return (
        <div className="fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
                <div>
                    <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>Meine Lernprojekte</h1>
                    <p style={{ color: '#94a3b8' }}>Verwalte deine Dokumente und PDF-Materialien.</p>
                </div>
                <button className={styles.btnPrimary} onClick={() => setShowCreateModal(true)}>
                    <Plus size={20} /> Neues Projekt
                </button>
            </div>

            {/* Create Modal */}
            {showCreateModal && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0,0,0,0.7)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000
                }}>
                    <div className="glass" style={{ padding: '32px', width: '400px', maxWidth: '90vw' }}>
                        <h2 style={{ marginBottom: '24px' }}>Neues Projekt erstellen</h2>
                        <input
                            type="text"
                            placeholder="Projektname"
                            value={newProjectName}
                            onChange={(e) => setNewProjectName(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '12px 16px',
                                borderRadius: '8px',
                                border: '1px solid var(--card-border)',
                                background: 'var(--sidebar-bg)',
                                color: 'var(--foreground)',
                                marginBottom: '20px'
                            }}
                            onKeyDown={(e) => e.key === 'Enter' && handleCreateProject()}
                        />
                        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                            <button
                                onClick={() => setShowCreateModal(false)}
                                style={{ padding: '10px 20px', borderRadius: '8px', border: '1px solid var(--card-border)', background: 'transparent', color: 'var(--foreground)', cursor: 'pointer' }}
                            >
                                Abbrechen
                            </button>
                            <button
                                onClick={handleCreateProject}
                                disabled={!newProjectName.trim() || isCreating}
                                className={styles.btnPrimary}
                            >
                                {isCreating ? <Loader2 className="animate-spin" size={18} /> : 'Erstellen'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Empty State */}
            {projects.length === 0 ? (
                <div className="glass" style={{ padding: '60px', textAlign: 'center' }}>
                    <FolderPlus size={60} color="var(--primary)" style={{ marginBottom: '20px', opacity: 0.6 }} />
                    <h2 style={{ marginBottom: '12px' }}>Noch keine Projekte</h2>
                    <p style={{ color: '#94a3b8', marginBottom: '24px', maxWidth: '400px', margin: '0 auto 24px' }}>
                        Erstelle dein erstes Projekt, um Dokumente hochzuladen und mit dem KI-Tutor zu lernen.
                    </p>
                    <button className={styles.btnPrimary} onClick={() => setShowCreateModal(true)}>
                        <Plus size={20} /> Erstes Projekt erstellen
                    </button>
                </div>
            ) : (
                <>
                    <div className={styles.uploadZone}>
                        <div style={{ background: 'rgba(99, 102, 241, 0.1)', padding: '20px', borderRadius: '50%', color: 'var(--primary)', marginBottom: '10px' }}>
                            <Upload size={32} />
                        </div>
                        <div style={{ textAlign: 'center' }}>
                            <h3 style={{ fontSize: '1.25rem', marginBottom: '4px' }}>Dateien hochladen</h3>
                            <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Wähle zuerst ein Projekt, dann lade Dateien hoch.</p>
                        </div>
                    </div>

                    <h2 style={{ fontSize: '1.25rem', marginBottom: '24px' }}>Aktive Projekte ({projects.length})</h2>

                    <div className={styles.grid}>
                        {projects.map((proj) => (
                            <div key={proj.project_id} className={`${styles.card} glass`}>
                                <div className={styles.cardHeader}>
                                    <div className={styles.iconBox}>
                                        <Library size={24} />
                                    </div>
                                    <div style={{ display: 'flex', gap: '8px' }}>
                                        <button
                                            onClick={() => handleDeleteProject(proj.project_id)}
                                            style={{ color: '#94a3b8', background: 'none', border: 'none', cursor: 'pointer' }}
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                </div>

                                <h3 style={{ fontSize: '1.2rem', marginBottom: '4px' }}>{proj.project_name}</h3>
                                <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                                    Erstellt am {new Date(proj.created_at).toLocaleDateString('de-DE')}
                                </p>

                                <div className={styles.statsRow}>
                                    <div className={styles.stat}>
                                        <p className={styles.statLabel}>Assets</p>
                                        <p className={styles.statValue}>{proj.asset_count} Dateien</p>
                                    </div>
                                    <div className={styles.stat}>
                                        <p className={styles.statLabel}>Status</p>
                                        <p className={styles.statValue} style={{ color: proj.asset_count > 0 ? 'var(--success)' : '#94a3b8', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                            {proj.asset_count > 0 ? (
                                                <><CheckCircle size={14} /> Bereit</>
                                            ) : (
                                                <>Leer</>
                                            )}
                                        </p>
                                    </div>
                                </div>

                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <button
                                        onClick={() => handleStartChat(proj.project_id)}
                                        disabled={proj.asset_count === 0}
                                        className={styles.btnPrimary}
                                        style={{
                                            flex: 1,
                                            justifyContent: 'center',
                                            opacity: proj.asset_count === 0 ? 0.5 : 1,
                                            cursor: proj.asset_count === 0 ? 'not-allowed' : 'pointer'
                                        }}
                                    >
                                        <MessageSquare size={16} /> Lernen
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}
