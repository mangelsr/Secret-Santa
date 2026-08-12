import React, { useState } from 'react';
import { registerParticipant } from '../services/api';

/**
 * Modal component for participant signup and selection of historical gift exclusions.
 */
export default function RegisterModal({ isOpen, onClose, groupId, existingParticipants, onParticipantRegistered }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [selectedExclusions, setSelectedExclusions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const toggleExclusion = (id) => {
    if (selectedExclusions.includes(id)) {
      setSelectedExclusions(selectedExclusions.filter(item => item !== id));
    } else {
      setSelectedExclusions([...selectedExclusions, id]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await registerParticipant(groupId, name, email, selectedExclusions);
      setName('');
      setEmail('');
      setSelectedExclusions([]);
      onParticipantRegistered();
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass-card" style={{ padding: '32px' }} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.4rem', fontWeight: '700' }}>🎁 Registrarse en el Grupo</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '1.5rem', cursor: 'pointer' }}>×</button>
        </div>

        {error && <div style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#fca5a5', padding: '12px', borderRadius: '8px', marginBottom: '16px' }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Tu Nombre Completo</label>
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
            <label className="form-label">Tu Correo Electrónico (para recibir tu resultado)</label>
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
                Selecciona a qué familiares **ya les has regalado en años anteriores** para que el algoritmo no te los vuelva a asignar:
              </span>
            </label>

            {existingParticipants.length === 0 ? (
              <p style={{ fontSize: '0.85rem', color: '#64748b', fontStyle: 'italic', marginTop: '8px' }}>
                Eres el primero en registrarte en este grupo. Tus familiares podrán seleccionarte a ti cuando se registren.
              </p>
            ) : (
              <div className="tag-selector">
                {existingParticipants.map((p) => {
                  const isSelected = selectedExclusions.includes(p.participant_id);
                  return (
                    <div 
                      key={p.participant_id} 
                      className={`tag-item ${isSelected ? 'selected' : ''}`}
                      onClick={() => toggleExclusion(p.participant_id)}
                    >
                      {isSelected ? '🚫' : '👤'} {p.name}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '28px' }}>
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-festive" disabled={loading}>
              {loading ? 'Inscribiendo...' : '✅ Confirmar Inscripción'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
