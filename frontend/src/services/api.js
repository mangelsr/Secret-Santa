const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

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

export async function getGroupDetails(groupId) {
  const response = await fetch(`${API_BASE_URL}/groups/${groupId}`);
  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Grupo no encontrado');
  }
  return await response.json();
}

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
