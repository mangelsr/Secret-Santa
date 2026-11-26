import assert from 'node:assert/strict';
import test from 'node:test';

import {
  createGroup,
  executeDraw,
  getGroupDetails,
  registerParticipant,
  removeParticipant,
  updateParticipant,
} from '../src/services/api.js';

function withMockFetch(handler, fn) {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = handler;
  return Promise.resolve()
    .then(fn)
    .finally(() => {
      globalThis.fetch = originalFetch;
    });
}

test('createGroup sends POST with JSON payload', async () => {
  await withMockFetch(
    async (url, init) => {
      assert.equal(url, 'http://localhost:8000/api/v1/groups');
      assert.equal(init.method, 'POST');
      assert.deepEqual(JSON.parse(init.body), {
        name: 'Familia',
        admin_email: 'admin@example.com',
        admin_passcode: '1234',
      });
      return new Response(JSON.stringify({ group_id: 'g-abc', status: 'OPEN' }), { status: 201 });
    },
    async () => {
      const res = await createGroup('Familia', 'admin@example.com', '1234');
      assert.equal(res.group_id, 'g-abc');
    },
  );
});

test('registerParticipant includes edit_passcode only when non-empty', async () => {
  const bodies = [];
  await withMockFetch(
    async (_url, init) => {
      bodies.push(JSON.parse(init.body));
      return new Response(JSON.stringify({ participant_id: 'p-1' }), { status: 201 });
    },
    async () => {
      await registerParticipant('g-1', 'Ana', 'ana@example.com', ['p-0'], '   ');
      await registerParticipant('g-1', 'Luis', 'luis@example.com', [], '9876');
      assert.equal('edit_passcode' in bodies[0], false);
      assert.equal(bodies[1].edit_passcode, '9876');
    },
  );
});

test('updateParticipant sends X-Admin-Passcode header and supports null email', async () => {
  await withMockFetch(
    async (url, init) => {
      assert.equal(url, 'http://localhost:8000/api/v1/groups/g-1/participants/p-2');
      assert.equal(init.method, 'PUT');
      assert.equal(init.headers['X-Admin-Passcode'], 'pin123');
      assert.deepEqual(JSON.parse(init.body), {
        name: 'Carlos',
        email: null,
        excluded_participant_ids: ['p-1'],
      });
      return new Response(JSON.stringify({ participant_id: 'p-2' }), { status: 200 });
    },
    async () => {
      const res = await updateParticipant('g-1', 'p-2', 'Carlos', null, ['p-1'], 'pin123');
      assert.equal(res.participant_id, 'p-2');
    },
  );
});

test('removeParticipant sends DELETE with X-Admin-Passcode header and surfaces backend error', async () => {
  await withMockFetch(
    async (_url, init) => {
      assert.equal(init.method, 'DELETE');
      assert.equal(init.headers['X-Admin-Passcode'], 'wrong');
      return new Response(JSON.stringify({ detail: 'Incorrect admin passcode' }), { status: 401 });
    },
    async () => {
      await assert.rejects(
        () => removeParticipant('g-1', 'p-2', 'wrong'),
        /Incorrect admin passcode/,
      );
    },
  );
});

test('getGroupDetails and executeDraw propagate responses and errors', async () => {
  await withMockFetch(
    async (url, init) => {
      if (!init) {
        assert.equal(url, 'http://localhost:8000/api/v1/groups/g-1');
        return new Response(JSON.stringify({ group_id: 'g-1', participants: [] }), { status: 200 });
      }
      assert.equal(url, 'http://localhost:8000/api/v1/groups/g-1/draw');
      assert.equal(init.method, 'POST');
      return new Response(JSON.stringify({ status: 'CLOSED', emails_sent: 3 }), { status: 200 });
    },
    async () => {
      const group = await getGroupDetails('g-1');
      assert.equal(group.group_id, 'g-1');
      const draw = await executeDraw('g-1', 'admin123');
      assert.equal(draw.status, 'CLOSED');
    },
  );
});
