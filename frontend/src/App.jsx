import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import CreateGroupModal from './components/CreateGroupModal';
import RegisterModal from './components/RegisterModal';
import AdminDrawModal from './components/AdminDrawModal';
import { getGroupDetails } from './services/api';

/**
 * Main application component managing active group view and modals.
 */
export default function App() {
  const [groupId, setGroupId] = useState('');
  const [group, setGroup] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);
  const [isAdminDrawOpen, setIsAdminDrawOpen] = useState(false);
  const [drawSuccessInfo, setDrawSuccessInfo] = useState(null);

  // Parse Group ID from URL Hash or Query Parameters
  useEffect(() => {
    const parseGroupId = () => {
      const hash = window.location.hash.replace('#', '');
      const params = new URLSearchParams(window.location.search);
      const queryId = params.get('group');
      if (hash) return hash;
      if (queryId) return queryId;
      return '';
    };

    const currentId = parseGroupId();
    if (currentId) {
      setGroupId(currentId);
      loadGroup(currentId);
    }
  }, []);

  const loadGroup = async (id) => {
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
  };

  const handleGroupCreated = (newGroup) => {
    setGroup(newGroup);
    setGroupId(newGroup.group_id);
    window.location.hash = newGroup.group_id;
  };

  const handleDrawSuccess = (result) => {
    setDrawSuccessInfo(result);
    loadGroup(groupId);
  };

  return (
    <div style={{ minHeight: '100vh', paddingBottom: '60px' }}>
      <Navbar onCreateClick={() => setIsCreateOpen(true)} currentGroup={group} />

      <main style={{ maxWidth: '1000px', margin: '0 auto', padding: '0 20px' }}>
        {/* Landing Section / Group Lookup */}
        {!group && !loading && (
          <div className="glass-card" style={{ padding: '48px 32px', textAlign: 'center', margin: '40px 0' }}>
            <span style={{ fontSize: '4rem', display: 'block', marginBottom: '16px' }}>🎄🎅🎁</span>
            <h1 style={{ fontSize: '2.4rem', fontWeight: '800', marginBottom: '16px', background: 'linear-gradient(135deg, #f59e0b, #ef4444)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Organiza tu Santa Secreto Familiar
            </h1>
            <p style={{ color: '#94a3b8', fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto 32px' }}>
              Registra integrantes, marca a quiénes **ya les regalaste en años pasados** para evitar repeticiones y realiza el sorteo automático con notificaciones secretas por correo.
            </p>

            <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button className="btn-festive" style={{ fontSize: '1.1rem', padding: '14px 28px' }} onClick={() => setIsCreateOpen(true)}>
                ✨ Crear un Grupo Navideño
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

        {loading && (
          <div className="glass-card" style={{ padding: '60px', textAlign: 'center', margin: '40px 0' }}>
            <p style={{ fontSize: '1.2rem', color: '#f59e0b' }}>⌛ Cargando grupo navideño...</p>
          </div>
        )}

        {error && !group && (
          <div className="glass-card" style={{ padding: '32px', textAlign: 'center', margin: '40px 0', border: '1px solid #ef4444' }}>
            <p style={{ color: '#fca5a5', fontSize: '1.1rem', marginBottom: '16px' }}>❌ {error}</p>
            <button className="btn-secondary" onClick={() => { setError(''); setGroupId(''); window.location.hash = ''; }}>Volver al Inicio</button>
          </div>
        )}

        {/* Active Group Dashboard */}
        {group && (
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

                <div style={{ display: 'flex', gap: '12px' }}>
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
                      ✅ El sorteo fue realizado y los correos han sido enviados vía AWS SES
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
                  Se despacharon {drawSuccessInfo.emails_sent} de {drawSuccessInfo.total_participants} correos electrónicos individuales a través de AWS SES. Revisa tu bandeja de entrada.
                </p>
              </div>
            )}

            {/* Registered Participants Grid */}
            <div className="glass-card" style={{ padding: '32px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
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
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
                  {group.participants.map((p) => (
                    <div key={p.participant_id} className="glass-card" style={{ padding: '20px', background: 'rgba(15,23,42,0.5)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                        <div style={{ width: '42px', height: '42px', borderRadius: '50%', background: 'linear-gradient(135deg, #ef4444, #f59e0b)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '1.2rem' }}>
                          {p.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <h4 style={{ fontWeight: '700', fontSize: '1.05rem' }}>{p.name}</h4>
                          <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{p.email}</p>
                        </div>
                      </div>

                      <div style={{ fontSize: '0.8rem', color: '#cbd5e1', paddingTop: '8px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                        🚫 {p.excluded_participant_ids?.length || 0} Exclusiones registradas
                      </div>
                    </div>
                  ))}
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
            onParticipantRegistered={() => loadGroup(group.group_id)} 
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
