import React, { useState } from 'react';
import { executeDraw } from '../services/api';

/**
 * Modal component for organizer confirmation and Secret Santa draw execution.
 */
export default function AdminDrawModal({ isOpen, onClose, groupId, onDrawSuccess }) {
  const [adminPasscode, setAdminPasscode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await executeDraw(groupId, adminPasscode);
      onDrawSuccess(result);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass-card glow-gold" style={{ padding: '32px' }} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.4rem', fontWeight: '700' }}>🎲 Realizar Sorteo Final</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '1.5rem', cursor: 'pointer' }}>×</button>
        </div>

        <p style={{ fontSize: '0.9rem', color: '#cbd5e1', marginBottom: '20px' }}>
          Al realizar el sorteo, el grupo se cerrará de forma permanente y se enviarán automáticamente las asignaciones secretas por correo electrónico vía **AWS SES** a todos los integrantes.
        </p>

        {error && <div style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#fca5a5', padding: '12px', borderRadius: '8px', marginBottom: '16px' }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Clave de Administrador (PIN)</label>
            <input 
              type="password" 
              className="form-input" 
              placeholder="Ingresa la clave creada al registrar el grupo" 
              value={adminPasscode} 
              onChange={(e) => setAdminPasscode(e.target.value)} 
              required 
            />
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '28px' }}>
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-gold" disabled={loading}>
              {loading ? 'Ejecutando Sorteo...' : '🚀 Cerrar Grupo y Enviar Correos'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
