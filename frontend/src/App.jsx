import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import CreateGroupModal from './components/CreateGroupModal';
import RegisterModal from './components/RegisterModal';
import EditParticipantModal from './components/EditParticipantModal';
import DeleteParticipantModal from './components/DeleteParticipantModal';
import AdminDrawModal from './components/AdminDrawModal';
import TutorialPage from './components/TutorialPage';
import { getGroupDetails } from './services/api';

const TUTORIAL_HASH = 'tutorial';

/**
 * Main application component managing active group view, tutorial page, participant cards, and modals.
 */
export default function App() {
  const [groupId, setGroupId] = useState('');
  const [group, setGroup] = useState(null);
  const [isTutorial, setIsTutorial] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notification, setNotification] = useState('');

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);
  const [isAdminDrawOpen, setIsAdminDrawOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editingParticipant, setEditingParticipant] = useState(null);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [deletingParticipant, setDeletingParticipant] = useState(null);
  const [drawSuccessInfo, setDrawSuccessInfo] = useState(null);

  const loadGroup = useCallback(async (id) => {
    setLoading(true);
    setError('');
    try {
      const data = await getGroupDetails(id);
      setGroup(data);
    } catch (err) {
      setError(err.message);
      setGroup(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Sync view and active Group ID from URL Hash or Query Parameters
  useEffect(() => {
    const syncFromLocation = () => {
      const hash = window.location.hash.replace('#', '');
      if (hash === TUTORIAL_HASH) {
        setIsTutorial(true);
        setError('');
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }

      setIsTutorial(false);
      const params = new URLSearchParams(window.location.search);
      const queryId = params.get('group');
      const currentId = hash || queryId || '';

      if (currentId) {
        setGroupId(currentId);
        loadGroup(currentId);
      } else {
        setGroupId('');
        setGroup(null);
        setError('');
        setDrawSuccessInfo(null);
      }
    };

    syncFromLocation();
    window.addEventListener('hashchange', syncFromLocation);
    return () => window.removeEventListener('hashchange', syncFromLocation);
  }, [loadGroup]);

  // Auto-hide temporary notifications
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(''), 4000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const openHome = () => {
    setIsTutorial(false);
    setGroup(null);
    setGroupId('');
    setError('');
    setDrawSuccessInfo(null);
    if (window.location.search || window.location.hash) {
      window.history.replaceState(null, '', window.location.pathname);
    }
  };

  const openTutorial = () => {
    setIsTutorial(true);
    window.location.hash = TUTORIAL_HASH;
  };

  const backToGroup = () => {
    if (!group) {
      openHome();
      return;
    }
    setIsTutorial(false);
    window.location.hash = group.group_id;
  };

  const handleGroupCreated = (newGroup) => {
    setIsTutorial(false);
    setGroup(newGroup);
    setGroupId(newGroup.group_id);
    window.location.hash = newGroup.group_id;
    setNotification('¡Grupo creado exitosamente! Comparte el enlace con tu familia.');
  };

  const handleDrawSuccess = (result) => {
    setDrawSuccessInfo(result);
    loadGroup(groupId);
  };

  const handleEditClick = (participant) => {
    setEditingParticipant(participant);
    setIsEditOpen(true);
  };

  const handleDeleteClick = (participant) => {
    setDeletingParticipant(participant);
    setIsDeleteOpen(true);
  };

  const handleParticipantUpdated = () => {
    loadGroup(group.group_id);
    setNotification('¡Datos del participante actualizados correctamente! ✨');
  };

  const handleParticipantDeleted = (deletedParticipant) => {
    loadGroup(group.group_id);
    setNotification(`Miembro "${deletedParticipant.name}" eliminado del grupo.`);
  };

  const handleParticipantRegistered = () => {
    loadGroup(group.group_id);
    setNotification('¡Inscripción confirmada con éxito! 🎁');
  };

  // Helper to resolve exclusion participant IDs to their names
  const getExcludedParticipantNames = (excludedIds) => {
    if (!excludedIds || excludedIds.length === 0 || !group?.participants) return [];
    const participantMap = new Map(group.participants.map((p) => [p.participant_id, p.name]));
    return excludedIds.map((id) => participantMap.get(id) || id);
  };

  return (
    <div style={{ minHeight: '100vh', paddingBottom: '60px' }}>
      <Navbar
        onCreateClick={() => setIsCreateOpen(true)}
        onTutorialClick={openTutorial}
        onHomeClick={openHome}
        currentGroup={group}
        isTutorial={isTutorial}
      />

      <main style={{ maxWidth: '1000px', margin: '0 auto', padding: '0 20px' }}>
        {/* Toast Notification */}
        {notification && (
          <div 
            className="glass-card glow-gold" 
            style={{ 
              padding: '14px 20px', 
              margin: '20px 0', 
              background: 'rgba(34, 197, 94, 0.25)', 
              border: '1px solid #22c55e',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              animation: 'modalIn 0.25s ease'
            }}
          >
            <span style={{ fontWeight: '600', color: '#4ade80' }}>{notification}</span>
            <button 
              onClick={() => setNotification('')} 
              style={{ background: 'none', border: 'none', color: '#cbd5e1', cursor: 'pointer', fontSize: '1.2rem' }}
            >
              ×
            </button>
          </div>
        )}

        {/* Tutorial Page */}
        {isTutorial && (
          <TutorialPage
            onBackHome={openHome}
            onBackToGroup={backToGroup}
            onCreateClick={() => setIsCreateOpen(true)}
            activeGroup={group}
          />
        )}

        {/* Landing Section / Group Lookup */}
        {!isTutorial && !group && !loading && (
          <div className="glass-card" style={{ padding: '48px 32px', textAlign: 'center', margin: '40px 0' }}>
            <span style={{ fontSize: '4rem', display: 'block', marginBottom: '16px' }}>🎄🎅🎁</span>
            <h1 style={{ fontSize: '2.4rem', fontWeight: '800', marginBottom: '16px', background: 'linear-gradient(135deg, #f59e0b, #ef4444)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Organiza tu Santa Secreto Familiar
            </h1>
            <p style={{ color: '#94a3b8', fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto 32px' }}>
              Registra integrantes, marca a quiénes <strong>ya les regalaste en años pasados</strong> para evitar repeticiones y realiza el sorteo automático con notificaciones secretas por correo.
            </p>

            <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button className="btn-festive" style={{ fontSize: '1.1rem', padding: '14px 28px' }} onClick={() => setIsCreateOpen(true)}>
                ✨ Crear un Grupo Navideño
              </button>
              <button className="btn-secondary" style={{ fontSize: '1.05rem', padding: '14px 24px' }} onClick={openTutorial}>
                📖 ¿Cómo funciona?
              </button>
            </div>

            <div style={{ marginTop: '40px', paddingTop: '32px', borderTop: '1px solid rgba(255,255,255,0.1)', maxWidth: '400px', margin: '40px auto 0' }}>
              <p style={{ fontSize: '0.9rem', color: '#94a3b8', marginBottom: '12px' }}>¿Ya tienes un código o ID de grupo?</p>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="ID del Grupo (ej: g-12345)" 
                  value={groupId} 
                  onChange={(e) => setGroupId(e.target.value)} 
                />
                <button className="btn-secondary" onClick={() => {
                  if (groupId) {
                    window.location.hash = groupId;
                    loadGroup(groupId);
                  }
                }}>Buscar</button>
              </div>
            </div>
          </div>
        )}

        {!isTutorial && loading && (
          <div className="glass-card" style={{ padding: '60px', textAlign: 'center', margin: '40px 0' }}>
            <p style={{ fontSize: '1.2rem', color: '#f59e0b' }}>⌛ Cargando grupo navideño...</p>
          </div>
        )}

        {!isTutorial && error && !group && (
          <div className="glass-card" style={{ padding: '32px', textAlign: 'center', margin: '40px 0', border: '1px solid #ef4444' }}>
            <p style={{ color: '#fca5a5', fontSize: '1.1rem', marginBottom: '16px' }}>❌ {error}</p>
            <button className="btn-secondary" onClick={openHome}>Volver al Inicio</button>
          </div>
        )}

        {/* Active Group Dashboard */}
        {!isTutorial && group && (
          <div>
            {/* Group Header Card */}
            <div className="glass-card glow-gold" style={{ padding: '32px', marginBottom: '32px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                    <h2 style={{ fontSize: '2rem', fontWeight: '800' }}>{group.name}</h2>
                    <span className={`status-badge ${group.status === 'OPEN' ? 'status-open' : 'status-closed'}`}>
                      {group.status === 'OPEN' ? '🟢 Registro Abierto' : '🔴 Sorteo Realizado'}
                    </span>
                  </div>
                  <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>
                    Organizado por: <strong>{group.admin_email}</strong> • Código: <code style={{ color: '#f59e0b', background: 'rgba(245,158,11,0.1)', padding: '2px 8px', borderRadius: '4px' }}>{group.group_id}</code>
                  </p>
                </div>

                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                  {group.status === 'OPEN' ? (
                    <>
                      <button className="btn-festive" onClick={() => setIsRegisterOpen(true)}>
                        👤 Inscribirme en este Grupo
                      </button>
                      <button className="btn-gold" onClick={() => setIsAdminDrawOpen(true)}>
                        🎲 Realizar Sorteo
                      </button>
                    </>
                  ) : (
                    <div style={{ padding: '12px 20px', background: 'rgba(34,197,94,0.15)', border: '1px solid #22c55e', borderRadius: '12px', color: '#4ade80', fontSize: '0.95rem', fontWeight: '600' }}>
                      ✅ El sorteo fue realizado y los correos han sido enviados
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Draw Success Alert Banner */}
            {drawSuccessInfo && (
              <div className="glass-card" style={{ padding: '24px', marginBottom: '32px', background: 'rgba(34,197,94,0.2)', border: '1px solid #22c55e' }}>
                <h3 style={{ color: '#4ade80', fontSize: '1.2rem', fontWeight: '700', marginBottom: '8px' }}>🎉 ¡Sorteo completado con éxito!</h3>
                <p style={{ color: '#e2e8f0', fontSize: '0.95rem' }}>
                  Se despacharon {drawSuccessInfo.emails_sent} de {drawSuccessInfo.total_participants} correos electrónicos individuales. Revisa tu bandeja de entrada.
                </p>
              </div>
            )}

            {/* Registered Participants Grid */}
            <div className="glass-card" style={{ padding: '32px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
                <h3 style={{ fontSize: '1.3rem', fontWeight: '700' }}>
                  👥 Miembros Inscritos ({group.participants?.length || 0})
                </h3>
                <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>🔒 Los amigos secretos asignados son confidenciales</span>
              </div>

              {(!group.participants || group.participants.length === 0) ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
                  <p style={{ fontSize: '1.1rem', marginBottom: '12px' }}>Aún no hay familiares inscritos en este grupo.</p>
                  <button className="btn-festive" onClick={() => setIsRegisterOpen(true)}>Sé el primero en inscribirte</button>
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '18px' }}>
                  {group.participants.map((p) => {
                    const excludedNames = getExcludedParticipantNames(p.excluded_participant_ids);

                    return (
                      <div key={p.participant_id} className="member-card">
                        <div>
                          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '10px', marginBottom: '12px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
                              <div style={{ 
                                width: '44px', 
                                height: '44px', 
                                minWidth: '44px',
                                borderRadius: '50%', 
                                background: 'linear-gradient(135deg, #ef4444, #f59e0b)', 
                                display: 'flex', 
                                alignItems: 'center', 
                                justifyContent: 'center', 
                                fontWeight: 'bold', 
                                fontSize: '1.25rem',
                                color: '#ffffff',
                                boxShadow: '0 4px 10px rgba(239, 68, 68, 0.3)'
                              }}>
                                {p.name.charAt(0).toUpperCase()}
                              </div>
                              <div style={{ minWidth: 0 }}>
                                <h4 style={{ fontWeight: '700', fontSize: '1.05rem', color: '#f8fafc', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                  {p.name}
                                </h4>
                                <p style={{ fontSize: '0.8rem', color: '#94a3b8', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                  {p.email}
                                </p>
                              </div>
                            </div>

                            {group.status === 'OPEN' && (
                              <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                                <button 
                                  className="btn-card-edit" 
                                  onClick={() => handleEditClick(p)}
                                  title="Editar datos y exclusiones"
                                >
                                  ✏️ Editar
                                </button>
                                <button 
                                  className="btn-card-delete" 
                                  onClick={() => handleDeleteClick(p)}
                                  title={`Eliminar a ${p.name}`}
                                >
                                  🗑️
                                </button>
                              </div>
                            )}
                          </div>

                          {/* Exclusions info */}
                          <div style={{ fontSize: '0.82rem', color: '#cbd5e1', paddingTop: '10px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: excludedNames.length > 0 ? '6px' : '0' }}>
                              <span>🚫</span>
                              <span style={{ fontWeight: '600' }}>
                                {excludedNames.length === 0 ? 'Sin exclusiones' : `${excludedNames.length} Exclusión${excludedNames.length > 1 ? 'es' : ''}:`}
                              </span>
                            </div>

                            {excludedNames.length > 0 && (
                              <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                                {excludedNames.map((exName, idx) => (
                                  <span key={idx} className="exclusion-chip">
                                    {exName}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Modals */}
      <CreateGroupModal 
        isOpen={isCreateOpen} 
        onClose={() => setIsCreateOpen(false)} 
        onGroupCreated={handleGroupCreated} 
      />

      {group && (
        <>
          <RegisterModal 
            isOpen={isRegisterOpen} 
            onClose={() => setIsRegisterOpen(false)} 
            groupId={group.group_id} 
            existingParticipants={group.participants || []} 
            onParticipantRegistered={handleParticipantRegistered} 
          />

          <EditParticipantModal
            isOpen={isEditOpen}
            onClose={() => {
              setIsEditOpen(false);
              setEditingParticipant(null);
            }}
            groupId={group.group_id}
            participant={editingParticipant}
            allParticipants={group.participants || []}
            onParticipantUpdated={handleParticipantUpdated}
          />

          <DeleteParticipantModal
            isOpen={isDeleteOpen}
            onClose={() => {
              setIsDeleteOpen(false);
              setDeletingParticipant(null);
            }}
            groupId={group.group_id}
            participant={deletingParticipant}
            onParticipantDeleted={handleParticipantDeleted}
          />

          <AdminDrawModal 
            isOpen={isAdminDrawOpen} 
            onClose={() => setIsAdminDrawOpen(false)} 
            groupId={group.group_id} 
            onDrawSuccess={handleDrawSuccess} 
          />
        </>
      )}
    </div>
  );
}
