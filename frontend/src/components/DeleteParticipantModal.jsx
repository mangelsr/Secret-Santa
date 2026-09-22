import React, { useState } from 'react';
import { removeParticipant } from '../services/api';

/**
 * Modal confirmation dialog for removing a participant from an open Secret Santa group.
 */
export default function DeleteParticipantModal({
  isOpen,
  onClose,
  groupId,
  participant,
  onParticipantDeleted
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen || !participant) return null;

  const handleConfirmDelete = async () => {
    setError('');
    setLoading(true);
    try {
      await removeParticipant(groupId, participant.participant_id);
      onParticipantDeleted(participant);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className="modal-content glass-card glow-red" 
        style={{ padding: '32px', maxWidth: '480px' }} 
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <div style={{ 
            width: '44px', 
            height: '44px', 
            borderRadius: '50%', 
            background: 'rgba(239, 68, 68, 0.2)', 
            border: '1px solid #ef4444',
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            fontSize: '1.4rem' 
          }}>
            🗑️
          </div>
          <div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: '700', color: '#f8fafc' }}>
              Confirmar Eliminación
            </h2>
            <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Esta acción no se puede deshacer</p>
          </div>
        </div>

        {error && (
          <div style={{ 
            background: 'rgba(239, 68, 68, 0.2)', 
            border: '1px solid #ef4444', 
            color: '#fca5a5', 
            padding: '12px', 
            borderRadius: '8px', 
            marginBottom: '16px', 
            fontSize: '0.9rem' 
          }}>
            ⚠️ {error}
          </div>
        )}

        <div style={{ 
          background: 'rgba(15, 23, 42, 0.6)', 
          border: '1px solid rgba(255, 255, 255, 0.08)', 
          borderRadius: '12px', 
          padding: '16px', 
          marginBottom: '20px' 
        }}>
          <p style={{ fontSize: '0.95rem', color: '#e2e8f0', marginBottom: '6px' }}>
            ¿Estás seguro de que deseas eliminar a <strong>{participant.name}</strong>?
          </p>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
            Correo: <code>{participant.email}</code>
          </p>
        </div>

        <p style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '24px', lineHeight: '1.5' }}>
          El integrante será removido de la lista y no formará parte del sorteo de regalos.
        </p>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button 
            type="button" 
            className="btn-secondary" 
            onClick={onClose} 
            disabled={loading}
          >
            Cancelar
          </button>
          <button 
            type="button" 
            className="btn-danger" 
            onClick={handleConfirmDelete} 
            disabled={loading}
          >
            {loading ? 'Eliminando...' : '🗑️ Sí, Eliminar Miembro'}
          </button>
        </div>
      </div>
    </div>
  );
}
