import React, { useState } from 'react';
import { createGroup } from '../services/api';

/**
 * Modal component for creating a new Secret Santa group.
 */
export default function CreateGroupModal({ isOpen, onClose, onGroupCreated }) {
  const [name, setName] = useState('');
  const [adminEmail, setAdminEmail] = useState('');
  const [adminPasscode, setAdminPasscode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const newGroup = await createGroup(name, adminEmail, adminPasscode);
      onGroupCreated(newGroup, adminPasscode);
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
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '700' }}>🎄 Crear Grupo Navideño</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '1.5rem', cursor: 'pointer' }}>×</button>
        </div>

        {error && <div style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#fca5a5', padding: '12px', borderRadius: '8px', marginBottom: '16px' }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Nombre del Grupo</label>
            <input 
              type="text" 
              className="form-input" 
              placeholder="Ej: Navidad Familia García 2026" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              required 
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email del Organizador (Admin)</label>
            <input 
              type="email" 
              className="form-input" 
              placeholder="organizador@familia.com" 
              value={adminEmail} 
              onChange={(e) => setAdminEmail(e.target.value)} 
              required 
            />
          </div>

          <div className="form-group">
            <label className="form-label">Clave de Administrador (PIN o Contraseña)</label>
            <input 
              type="password" 
              className="form-input" 
              placeholder="Para realizar el sorteo final" 
              value={adminPasscode} 
              onChange={(e) => setAdminPasscode(e.target.value)} 
              required 
            />
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '28px' }}>
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-festive" disabled={loading}>
              {loading ? 'Creando...' : '✨ Crear Grupo'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
