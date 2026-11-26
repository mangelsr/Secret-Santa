import React, { useState } from 'react';

const STEPS = [
  {
    number: '1',
    icon: '🎄',
    title: 'Crea un Grupo Navideño',
    role: 'Organizador',
    description:
      'El organizador crea el grupo ingresando un nombre (ej. "Navidad Familia García 2026"), su correo y una Clave de Administrador (PIN) secreta que usará al final para ejecutar el sorteo.',
  },
  {
    number: '2',
    icon: '🔗',
    title: 'Comparte el Enlace o Código',
    role: 'Organizador',
    description:
      'Al crear el grupo se genera un código único (ej. g-12345678). Usa el botón "🔗 Copiar Enlace" de la barra superior y envíalo por WhatsApp o correo a toda la familia.',
  },
  {
    number: '3',
    icon: '🚫',
    title: 'Inscríbete y Marca Exclusiones',
    role: 'Todos',
    description:
      'Cada persona entra al enlace, se registra con su nombre y correo único, y selecciona a los familiares a quienes ya les regaló en años pasados para evitar repeticiones.',
  },
  {
    number: '4',
    icon: '🎲',
    title: 'Realiza el Sorteo Secreto',
    role: 'Organizador',
    description:
      'Cuando estén todos inscritos (mínimo 3 personas), el organizador ingresa su PIN para sortear. El sistema envía un correo privado a cada integrante con su amigo secreto.',
  },
];

const FAQS = [
  {
    question: 'Fui el primero en registrarme y no aparecía nadie para excluir, ¿qué hago?',
    answer:
      '¡Es normal! Regístrate normalmente primero. Una vez que tus familiares se vayan inscribiendo en el grupo, busca tu tarjeta y haz clic en "✏️ Editar" para agregar tus exclusiones antes de que el organizador cierre el grupo.',
  },
  {
    question: '¿Cuántos participantes se necesitan como mínimo para el sorteo?',
    answer:
      'Se requieren al menos 3 participantes inscritos para poder realizar el sorteo de Santa Secreto.',
  },
  {
    question: '¿Qué pasa si hay demasiadas exclusiones y no hay combinación posible?',
    answer:
      'Si el algoritmo detecta que las reglas de exclusión impiden asignar a todos sin conflictos, mostrará un aviso antes de cerrar el grupo. Pueden ajustar algunas exclusiones usando "✏️ Editar" e intentar el sorteo nuevamente.',
  },
  {
    question: '¿Puedo inscribir a dos familiares con el mismo correo electrónico?',
    answer:
      'No. Cada participante dentro de un mismo grupo debe tener un correo electrónico único para garantizar que reciba su asignación de forma privada y confidencial.',
  },
  {
    question: '¿Se pueden modificar o eliminar participantes después del sorteo?',
    answer:
      'No. Una vez que el organizador ejecuta el sorteo, el estado cambia de "🟢 Registro Abierto" a "🔴 Sorteo Realizado" de forma permanente y se despachan los correos.',
  },
  {
    question: 'No encuentro el correo con mi amigo secreto, ¿dónde reviso?',
    answer:
      'Revisa tu bandeja de Correo no deseado (Spam) o la pestaña de Promociones. También confirma con el organizador que tu correo esté escrito correctamente en la lista del grupo.',
  },
];

/**
 * Interactive tutorial page explaining how to organize and participate in Secret Santa.
 */
export default function TutorialPage({ onBackHome, onBackToGroup, onCreateClick, activeGroup }) {
  const [activeTab, setActiveTab] = useState('organizer');
  const [openFaqIndex, setOpenFaqIndex] = useState(0);

  const toggleFaq = (idx) => {
    setOpenFaqIndex((prev) => (prev === idx ? null : idx));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px', marginBottom: '20px' }}>
      {/* Hero Banner */}
      <section className="glass-card glow-gold" style={{ padding: '40px 32px', textAlign: 'center' }}>
        <span style={{ fontSize: '3.2rem', display: 'block', marginBottom: '12px' }}>📖🎅✨</span>
        <h1
          style={{
            fontSize: '2.2rem',
            fontWeight: '800',
            marginBottom: '12px',
            background: 'linear-gradient(135deg, #f59e0b, #ef4444)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Cómo funciona Santa Secreto
        </h1>
        <p style={{ color: '#cbd5e1', fontSize: '1.05rem', maxWidth: '660px', margin: '0 auto 24px' }}>
          Organiza tu intercambio navideño en pocos minutos, evita regalos repetidos de años anteriores y mantén el secreto de principio a fin.
        </p>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
          {activeGroup ? (
            <button className="btn-secondary" onClick={onBackToGroup}>
              ← Volver al grupo &ldquo;{activeGroup.name}&rdquo;
            </button>
          ) : (
            <button className="btn-secondary" onClick={onBackHome}>
              ← Volver al Inicio
            </button>
          )}
          <button className="btn-festive" onClick={onCreateClick}>
            ✨ Crear un Grupo Navideño
          </button>
        </div>
      </section>

      {/* 4-Step Overview */}
      <section className="glass-card" style={{ padding: '32px' }}>
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '1.45rem', fontWeight: '700', marginBottom: '6px' }}>
            🗺️ El flujo en 4 pasos simples
          </h2>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>
            Desde crear el grupo hasta recibir el correo secreto con tu amigo asignado.
          </p>
        </div>

        <div className="tutorial-steps-grid">
          {STEPS.map((step) => (
            <div key={step.number} className="tutorial-step-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <span className="tutorial-step-badge">Paso {step.number}</span>
                <span className="tutorial-role-pill">{step.role}</span>
              </div>
              <div style={{ fontSize: '2rem', marginBottom: '10px' }}>{step.icon}</div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#f8fafc', marginBottom: '8px' }}>
                {step.title}
              </h3>
              <p style={{ fontSize: '0.9rem', color: '#cbd5e1', lineHeight: '1.55' }}>
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Role-Based Detailed Guide */}
      <section className="glass-card" style={{ padding: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '24px' }}>
          <div>
            <h2 style={{ fontSize: '1.45rem', fontWeight: '700', marginBottom: '4px' }}>
              🎯 Guía detallada según tu rol
            </h2>
            <p style={{ color: '#94a3b8', fontSize: '0.92rem' }}>
              Elige una vista para ver las instrucciones paso a paso.
            </p>
          </div>

          <div className="tutorial-tabs" role="tablist" aria-label="Guía por rol">
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'organizer'}
              className={`tutorial-tab-btn ${activeTab === 'organizer' ? 'active' : ''}`}
              onClick={() => setActiveTab('organizer')}
            >
              👑 Soy Organizador
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'participant'}
              className={`tutorial-tab-btn ${activeTab === 'participant' ? 'active' : ''}`}
              onClick={() => setActiveTab('participant')}
            >
              🎁 Soy Participante
            </button>
          </div>
        </div>

        {activeTab === 'organizer' ? (
          <div className="tutorial-guide-list">
            <div className="tutorial-guide-item">
              <div className="tutorial-guide-icon">1️⃣</div>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '4px' }}>
                  Crea el grupo y guarda tu PIN de Administrador
                </h3>
                <p style={{ color: '#cbd5e1', fontSize: '0.92rem' }}>
                  Haz clic en <strong>&ldquo;✨ Crear Nuevo Grupo&rdquo;</strong>, define el nombre de la reunión, tu correo de organizador y una clave o PIN. <strong>Guarda muy bien esa clave</strong>, porque la necesitarás para iniciar el sorteo final.
                </p>
              </div>
            </div>

            <div className="tutorial-guide-item">
              <div className="tutorial-guide-icon">2️⃣</div>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '4px' }}>
                  Invita a tu familia o amigos
                </h3>
                <p style={{ color: '#cbd5e1', fontSize: '0.92rem' }}>
                  Copia el enlace con el botón <strong>&ldquo;🔗 Copiar Enlace&rdquo;</strong> o comparte el código del grupo (ejemplo: <code style={{ color: '#f59e0b' }}>g-1a2b3c4d</code>). Recuerda inscribirte tú también en el grupo si vas a participar en el intercambio.
                </p>
              </div>
            </div>

            <div className="tutorial-guide-item">
              <div className="tutorial-guide-icon">3️⃣</div>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '4px' }}>
                  Supervisa y corrige la lista antes del cierre
                </h3>
                <p style={{ color: '#cbd5e1', fontSize: '0.92rem' }}>
                  Mientras el grupo esté en estado <span style={{ color: '#4ade80', fontWeight: '600' }}>🟢 Registro Abierto</span>, puedes usar <strong>&ldquo;✏️ Editar&rdquo;</strong> para corregir nombres, correos o exclusiones, o <strong>&ldquo;🗑️&rdquo;</strong> para quitar a alguien que ya no participará.
                </p>
              </div>
            </div>

            <div className="tutorial-guide-item">
              <div className="tutorial-guide-icon">4️⃣</div>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '4px' }}>
                  Ejecuta el sorteo con tu PIN
                </h3>
                <p style={{ color: '#cbd5e1', fontSize: '0.92rem' }}>
                  Cuando haya al menos <strong>3 inscritos</strong> y todos hayan configurado sus exclusiones, presiona <strong>&ldquo;🎲 Realizar Sorteo&rdquo;</strong> e ingresa tu clave. El sistema calculará las parejas válidas, cerrará el grupo y enviará cada resultado por correo electrónico.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="tutorial-guide-list">
            <div className="tutorial-guide-item">
              <div className="tutorial-guide-icon">1️⃣</div>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '4px' }}>
                  Entra al grupo de tu familia
                </h3>
                <p style={{ color: '#cbd5e1', fontSize: '0.92rem' }}>
                  Abre el enlace que te compartió el organizador, o escribe el código del grupo (ej. <code style={{ color: '#f59e0b' }}>g-1a2b3c4d</code>) en el buscador de la página de inicio y pulsa <strong>&ldquo;Buscar&rdquo;</strong>.
                </p>
              </div>
            </div>

            <div className="tutorial-guide-item">
              <div className="tutorial-guide-icon">2️⃣</div>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '4px' }}>
                  Completa tu inscripción
                </h3>
                <p style={{ color: '#cbd5e1', fontSize: '0.92rem' }}>
                  Haz clic en <strong>&ldquo;👤 Inscribirme en este Grupo&rdquo;</strong>, escribe tu nombre completo y tu correo electrónico personal (asegúrate de escribirlo sin errores, ahí llegará el nombre de tu amigo secreto).
                </p>
              </div>
            </div>

            <div className="tutorial-guide-item">
              <div className="tutorial-guide-icon">3️⃣</div>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '4px' }}>
                  Marca a quiénes ya les regalaste (Exclusiones 🚫)
                </h3>
                <p style={{ color: '#cbd5e1', fontSize: '0.92rem' }}>
                  Selecciona las etiquetas de los familiares a los que <strong>ya les diste regalo en años anteriores</strong> (o tu pareja si prefieren evitarse). Si todavía faltan personas por inscribirse, vuelve después y usa <strong>&ldquo;✏️ Editar&rdquo;</strong> en tu tarjeta para actualizar tus exclusiones.
                </p>
              </div>
            </div>

            <div className="tutorial-guide-item">
              <div className="tutorial-guide-icon">4️⃣</div>
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '4px' }}>
                  Revisa tu correo el día del sorteo
                </h3>
                <p style={{ color: '#cbd5e1', fontSize: '0.92rem' }}>
                  Cuando el organizador realice el sorteo, verás el estado <span style={{ color: '#f87171', fontWeight: '600' }}>🔴 Sorteo Realizado</span> y recibirás un correo confidencial indicando a quién te toca regalar. ¡Nadie más en la página puede ver tu resultado!
                </p>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* FAQ Accordion */}
      <section className="glass-card" style={{ padding: '32px' }}>
        <h2 style={{ fontSize: '1.45rem', fontWeight: '700', marginBottom: '20px' }}>
          ❓ Preguntas Frecuentes
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {FAQS.map((item, idx) => {
            const isOpen = openFaqIndex === idx;
            return (
              <div key={item.question} className="faq-item">
                <button
                  type="button"
                  className="faq-question"
                  aria-expanded={isOpen}
                  onClick={() => toggleFaq(idx)}
                >
                  <span>{item.question}</span>
                  <span style={{ color: '#f59e0b', fontSize: '1.2rem', flexShrink: 0 }}>
                    {isOpen ? '−' : '+'}
                  </span>
                </button>
                {isOpen && (
                  <div className="faq-answer">
                    {item.answer}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="glass-card" style={{ padding: '28px 32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: '700', marginBottom: '4px' }}>
            ¿Todo listo para empezar? 🎁
          </h3>
          <p style={{ color: '#94a3b8', fontSize: '0.92rem' }}>
            Crea un grupo nuevo o regresa para unirte con un código existente.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {activeGroup ? (
            <button className="btn-secondary" onClick={onBackToGroup}>
              ← Volver al grupo
            </button>
          ) : (
            <button className="btn-secondary" onClick={onBackHome}>
              Ir al Inicio
            </button>
          )}
          <button className="btn-festive" onClick={onCreateClick}>
            ✨ Crear Grupo Navideño
          </button>
        </div>
      </section>
    </div>
  );
}
