import React, { useState } from 'react';
import { updateParticipant } from '../services/api';

function EditParticipantForm({ 
  groupId, 
  participant, 
  allParticipants, 
  onParticipantUpdated, 
  onClose 
}) {
  const [name, setName] = useState(participant.name || '');
  const [email, setEmail] = useState(participant.email || '');
  const [selectedExclusions, setSelectedExclusions] = useState(participant.excluded_participant_ids || []);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Filter out current participant from potential exclusions list
  const otherParticipants = allParticipants.filter(
    (p) => p.participant_id !== participant.participant_id
  );

  const toggleExclusion = (id) => {
    if (selectedExclusions.includes(id)) {
      setSelectedExclusions(selectedExclusions.filter((item) => item !== id));
    } else {
      setSelectedExclusions([...selectedExclusions, id]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await updateParticipant(
        groupId,
        participant.participant_id,
        name.trim(),
        email.trim(),
        selectedExclusions
      );
      onParticipantUpdated();
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '1.5rem' }}>✏️</span>
          <h2 style={{ fontSize: '1.4rem', fontWeight: '700' }}>Editar Datos del Miembro</h2>
        </div>
        <button 
          onClick={onClose} 
          style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '1.5rem', cursor: 'pointer' }}
        >
          ×
        </button>
      </div>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#fca5a5', padding: '12px', borderRadius: '8px', marginBottom: '16px', fontSize: '0.9rem' }}>
          ⚠️ {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Nombre Completo</label>
          <input 
            type="text" 
            className="form-input" 
            placeholder="Ej: Tío Carlos" 
            value={name} 
            onChange={(e) => setName(e.target.value)} 
            required 
          />
        </div>

        <div className="form-group">
          <label className="form-label">Correo Electrónico (para recibir la asignación)</label>
          <input 
            type="email" 
            className="form-input" 
            placeholder="carlos@familia.com" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)} 
            required 
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            Exclusiones Navideñas 🚫
            <span style={{ display: 'block', fontWeight: '400', fontSize: '0.8rem', color: '#94a3b8', marginTop: '4px' }}>
              Selecciona a los familiares a quienes **ya les regaló en años anteriores** para evitar que le toque regalarles de nuevo:
            </span>
          </label>

          {otherParticipants.length === 0 ? (
            <p style={{ fontSize: '0.85rem', color: '#64748b', fontStyle: 'italic', marginTop: '8px' }}>
              No hay otros participantes en el grupo para seleccionar exclusiones.
            </p>
          ) : (
            <div className="tag-selector">
              {otherParticipants.map((p) => {
                const isSelected = selectedExclusions.includes(p.participant_id);
                return (
                  <div 
                    key={p.participant_id} 
                    className={`tag-item ${isSelected ? 'selected' : ''}`}
                    onClick={() => toggleExclusion(p.participant_id)}
                    title={isSelected ? 'Clic para desmarcar exclusión' : 'Clic para marcar como excluido'}
                  >
                    {isSelected ? '🚫' : '👤'} {p.name}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '28px' }}>
          <button type="button" className="btn-secondary" onClick={onClose} disabled={loading}>
            Cancelar
          </button>
          <button type="submit" className="btn-festive" disabled={loading}>
            {loading ? 'Guardando...' : '💾 Guardar Cambios'}
          </button>
        </div>
      </form>
    </div>
  );
}

/**
 * Modal component for updating an existing participant's info and exclusions.
 */
export default function EditParticipantModal({ 
  isOpen, 
  onClose, 
  groupId, 
  participant, 
  allParticipants = [], 
  onParticipantUpdated 
}) {
  if (!isOpen || !participant) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className="modal-content glass-card glow-gold" 
        style={{ padding: '32px' }} 
        onClick={(e) => e.stopPropagation()}
      >
        <EditParticipantForm
          key={participant.participant_id}
          groupId={groupId}
          participant={participant}
          allParticipants={allParticipants}
          onParticipantUpdated={onParticipantUpdated}
          onClose={onClose}
        />
      </div>
    </div>
  );
}
