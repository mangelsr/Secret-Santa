const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * Creates a new Christmas Secret Santa group.
 */
export async function createGroup(name, adminEmail, adminPasscode) {
  const response = await fetch(`${API_BASE_URL}/groups`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, admin_email: adminEmail, admin_passcode: adminPasscode })
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Error al crear el grupo');
  }
  return await response.json();
}

/**
 * Fetches group metadata and public participant list.
 */
export async function getGroupDetails(groupId) {
  const response = await fetch(`${API_BASE_URL}/groups/${groupId}`);
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Grupo no encontrado');
  }
  return await response.json();
}

/**
 * Registers a new participant specifying historical gift exclusions.
 */
export async function registerParticipant(groupId, name, email, excludedParticipantIds) {
  const response = await fetch(`${API_BASE_URL}/groups/${groupId}/participants`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name,
      email,
      excluded_participant_ids: excludedParticipantIds
    })
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Error al inscribirse');
  }
  return await response.json();
}

/**
 * Triggers the Secret Santa draw and dispatches email notifications via AWS SES.
 */
export async function executeDraw(groupId, adminPasscode) {
  const response = await fetch(`${API_BASE_URL}/groups/${groupId}/draw`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ admin_passcode: adminPasscode })
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Error al ejecutar el sorteo');
  }
  return await response.json();
}

/**
 * Removes a participant from an open group (Admin action).
 */
export async function removeParticipant(groupId, participantId, adminPasscode) {
  const response = await fetch(`${API_BASE_URL}/groups/${groupId}/participants/${participantId}`, {
    method: 'DELETE',
    headers: {
      'X-Admin-Passcode': adminPasscode
    }
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Error al eliminar participante');
  }
  return true;
}
