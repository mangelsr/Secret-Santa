import React from 'react';

/**
 * Navbar component featuring festive brand header and action buttons.
 */
export default function Navbar({ onCreateClick, currentGroup }) {
  const handleCopyLink = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url);
    alert('¡Enlace del grupo copiado al portapapeles!');
  };

  return (
    <nav className="glass-card" style={{ borderRadius: '0 0 16px 16px', padding: '16px 32px', marginBottom: '40px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => window.location.hash = ''}>
          <span style={{ fontSize: '2rem' }}>🎅</span>
          <div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: '800', background: 'linear-gradient(135deg, #f59e0b, #ef4444)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Santa Secreto
            </h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Edición Familiar 🎁</p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          {currentGroup && (
            <button className="btn-secondary" onClick={handleCopyLink}>
              🔗 Copiar Enlace
            </button>
          )}
          <button className="btn-festive" onClick={onCreateClick}>
            ✨ Crear Nuevo Grupo
          </button>
        </div>
      </div>
    </nav>
  );
}
