import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capture
import brain
import install_capture


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.vault = self.base / 'vault'
        self.vault.mkdir()
        self.project = self.base / 'project'
        self.project.mkdir()
        self.transcripts = self.base / 'sessions'
        self.transcripts.mkdir()
        self.path = self.transcripts / 'session.jsonl'
        self.config = {'enabled': True, 'vault': str(self.vault), 'allowed_roots': [str(self.project)],
                       'transcript_roots': [str(self.transcripts)], 'activated_utc': '2026-11-24T00:00:00Z',
                       'codex': 'unused', 'debounce_seconds': 0}
        self.append({'type': 'session_meta', 'payload': {'id': 'test-1', 'cwd': str(self.project), 'source': 'vscode'}})
        self.message('Prefiero ejemplos concretos antes de la teoría.')

    def tearDown(self):
        self.temporary.cleanup()

    def append(self, record):
        with self.path.open('a', encoding='utf-8', newline='\n') as output:
            output.write(json.dumps(record, ensure_ascii=False) + '\n')

    def message(self, text, role='user', timestamp='2026-11-24T15:00:00Z'):
        self.append({'timestamp': timestamp, 'type': 'response_item', 'payload': {
            'type': 'message', 'role': role, 'content': [{'type': 'input_text' if role == 'user' else 'output_text', 'text': text}]}})

    def event(self, **overrides):
        return {'session_id': 'test-1', 'cwd': str(self.project), 'transcript_path': str(self.path), 'hook_event_name': 'Stop', **overrides}

    def enqueue(self):
        return capture.enqueue(self.config, self.event())

    def extractor(self, config, messages, catalog):
        evidence = next(m for m in messages if m['role'] == 'user')
        return {'candidates': [{'title': 'Ejemplos antes de teoría', 'body': 'El usuario prefiere empezar con ejemplos concretos.',
            'category': '2', 'kind': 'conocimiento', 'state': 'confirmado', 'utility': 'Organizar explicaciones futuras.',
            'query': 'preferencia ejemplos teoría', 'evidence': [{'message_id': evidence['id'], 'quote': evidence['text']}]}]}

    def run_worker(self, extractor=None):
        return capture.process(self.config, force=True, extractor=extractor or self.extractor)

    def candidates(self):
        with capture.database(self.config) as db:
            return db.execute('SELECT * FROM candidates').fetchall()

    def test_duplicate_events_and_runs_create_one_candidate_no_note(self):
        self.assertTrue(self.enqueue()['queued'])
        self.assertFalse(self.enqueue()['queued'])
        self.assertEqual(self.run_worker()['processed'], 1)
        self.assertEqual(self.run_worker()['processed'], 0)
        self.assertEqual(len(self.candidates()), 1)
        self.assertFalse((self.vault / '00-entrada').exists())
        self.assertIn('todavía no son conocimiento', (self.vault / 'CAPTURA-PILOTO.md').read_text(encoding='utf-8'))

    def test_reopen_processes_new_messages_and_deduplicates_same_result(self):
        self.enqueue(); self.run_worker()
        self.message('Sigo prefiriendo ejemplos concretos antes de la teoría.')
        self.enqueue(); self.run_worker()
        self.assertEqual(len(self.candidates()), 1)
        self.assertEqual(capture.status(self.config)['sessions_pending'], 0)

    def test_model_failure_keeps_cursor_for_retry(self):
        self.enqueue()
        def fail(*args):
            raise RuntimeError('Modelo no disponible')
        self.assertIn('error', self.run_worker(fail))
        with capture.database(self.config) as db:
            row = db.execute('SELECT * FROM sessions').fetchone()
            self.assertEqual(row['cursor'], 0)
            self.assertGreater(row['retry_after'], 0)
            db.execute('UPDATE sessions SET retry_after=0')
        self.assertEqual(self.run_worker()['processed'], 1)

    def test_new_event_during_model_call_is_not_acknowledged_as_processed(self):
        self.enqueue()
        def racing(config, messages, catalog):
            self.message('Una corrección nueva mientras se extrae.')
            self.enqueue()
            return self.extractor(config, messages, catalog)
        self.run_worker(racing)
        self.assertEqual(capture.status(self.config)['sessions_pending'], 1)
        self.run_worker()
        self.assertEqual(capture.status(self.config)['sessions_pending'], 0)

    def test_fabricated_evidence_rejected_and_remains_pending(self):
        self.enqueue()
        def bad(config, messages, catalog):
            result = self.extractor(config, messages, catalog)
            result['candidates'][0]['evidence'][0]['quote'] = 'Esto nunca se dijo'
            return result
        self.assertIn('error', self.run_worker(bad))
        self.assertEqual(len(self.candidates()), 0)
        self.assertEqual(capture.status(self.config)['sessions_pending'], 1)

    def test_no_memory_request_prevents_extraction(self):
        self.message('No guardes esto en la memoria.')
        self.enqueue()
        def forbidden(*args):
            self.fail('No debería llamar al modelo')
        result = self.run_worker(forbidden)
        self.assertEqual(result['reason'], 'omitted-by-user')
        self.assertEqual(len(self.candidates()), 0)

    def test_secrets_tools_and_reasoning_are_not_passed_to_model(self):
        self.message('api_key=sk-' + 'x' * 30)
        self.append({'type': 'response_item', 'payload': {'type': 'function_call_output', 'output': 'secret-tool'}})
        self.append({'type': 'response_item', 'payload': {'type': 'reasoning', 'summary': 'secret-reasoning'}})
        self.enqueue()
        def checked(config, messages, catalog):
            serialized = json.dumps(messages)
            for secret in ['api_key', 'secret-tool', 'secret-reasoning']:
                self.assertNotIn(secret, serialized)
            return self.extractor(config, messages, catalog)
        self.assertEqual(self.run_worker(checked)['processed'], 1)

    def test_scope_and_subagent_excluded(self):
        self.assertFalse(capture.enqueue(self.config, self.event(cwd=str(self.base)))['queued'])
        self.assertFalse(capture.enqueue(self.config, self.event(agent_id='child'))['queued'])
        self.path.write_text(json.dumps({'type': 'session_meta', 'payload': {'parent_thread_id': 'parent'}}) + '\n', encoding='utf-8')
        self.assertFalse(self.enqueue()['queued'])

    def test_path_escape_or_session_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            capture.enqueue(self.config, self.event(transcript_path=str(self.base / 'outside.jsonl')))
        capture.enqueue(self.config, self.event(session_id='different'))
        self.assertIn('error', self.run_worker())

    def test_cutoff_excludes_past_messages(self):
        self.path.write_text('', encoding='utf-8')
        self.append({'type': 'session_meta', 'payload': {'id': 'test-1', 'cwd': str(self.project), 'source': 'vscode'}})
        self.message('Un mensaje histórico que no se debe enviar.', timestamp='2026-01-01T00:00:00Z')
        self.message('Un dato nuevo que sí se puede evaluar.')
        self.enqueue()
        def checked(config, messages, catalog):
            self.assertEqual(len(messages), 1)
            self.assertNotIn('histórico', messages[0]['text'])
            return self.extractor(config, messages, catalog)
        self.run_worker(checked)

    def test_accept_publishes_once_with_exact_evidence_source_and_lint(self):
        self.enqueue(); self.run_worker()
        candidate_id = self.candidates()[0]['id']
        result = capture.decide(self.config, candidate_id, 'accept')
        self.assertEqual(result['status'], 'accepted')
        self.assertTrue((self.vault / result['note']).exists())
        self.assertFalse(capture.decide(self.config, candidate_id, 'accept')['changed'])
        self.assertEqual(len(list((self.vault / '00-entrada').glob('*.md'))), 1)
        self.assertEqual(len(list((self.vault / '80-fuentes').glob('*.json'))), 2)
        self.assertTrue(brain.lint(self.vault)['ok'])

    def test_related_note_requires_review_and_never_overwrites(self):
        folder = self.vault / '30-conocimiento'
        folder.mkdir()
        existing = folder / 'preferencia.md'
        existing.write_text('# Preferencia\n\nEjemplos y teoría.\n', encoding='utf-8')
        self.enqueue(); self.run_worker()
        candidate_id = self.candidates()[0]['id']
        with self.assertRaises(ValueError):
            capture.decide(self.config, candidate_id, 'accept')
        self.assertEqual(existing.read_text(encoding='utf-8'), '# Preferencia\n\nEjemplos y teoría.\n')
        capture.decide(self.config, candidate_id, 'accept', allow_new=True)

    def test_reject_does_not_publish(self):
        self.enqueue(); self.run_worker()
        capture.decide(self.config, self.candidates()[0]['id'], 'reject')
        self.assertFalse((self.vault / '00-entrada').exists())
        self.assertEqual(capture.status(self.config)['candidates'], {'rejected': 1})

    def test_truncated_or_missing_transcript_remains_pending(self):
        self.enqueue()
        self.path.write_text('', encoding='utf-8')
        self.assertIn('truncado', self.run_worker()['error'])
        self.assertEqual(capture.status(self.config)['sessions_pending'], 1)

    def test_assistant_claim_is_not_confirmed(self):
        messages = [{'id': 'a', 'role': 'assistant', 'text': 'Esto funciona.'}]
        result = self.extractor(self.config, [{'id': 'a', 'role': 'user', 'text': 'Esto funciona.'}], '')
        validated = capture.validate_result(result, messages)
        self.assertEqual(validated[0]['state'], 'hipotesis')

    def test_unknown_transcript_message_format_stays_pending(self):
        self.path.write_text('', encoding='utf-8')
        self.append({'type': 'session_meta', 'payload': {'id': 'test-1', 'cwd': str(self.project), 'source': 'vscode'}})
        self.append({'timestamp': '2026-11-24T15:00:00Z', 'type': 'event_msg', 'payload': {'type': 'user_message', 'message': 'Formato distinto'}})
        self.enqueue()
        self.assertIn('no soportado', self.run_worker()['error'])
        self.assertEqual(capture.status(self.config)['sessions_pending'], 1)

    def test_partial_last_line_is_not_acknowledged(self):
        self.enqueue(); self.run_worker()
        with self.path.open('ab') as output:
            output.write(b'{"partial":')
        self.enqueue()
        self.assertIn('error', self.run_worker())
        self.assertEqual(capture.status(self.config)['sessions_pending'], 1)

    def test_pause_prevents_queue_and_processing(self):
        self.enqueue()
        self.config['enabled'] = False
        self.assertFalse(self.enqueue()['queued'])
        self.assertTrue(self.run_worker()['disabled'])
        self.assertEqual(len(self.candidates()), 0)

    def test_reject_clears_candidate_content(self):
        self.enqueue(); self.run_worker()
        candidate_id = self.candidates()[0]['id']
        capture.decide(self.config, candidate_id, 'reject')
        row = self.candidates()[0]
        self.assertEqual(row['payload'], '{}')
        self.assertEqual(row['evidence'], '[]')

    def test_hook_installation_preserves_unrelated_handlers_and_is_idempotent(self):
        existing = {'description': 'Mis hooks', 'hooks': {'Stop': [{'hooks': [{'type': 'command', 'command': 'python other.py'}]}], 'SessionStart': [{'hooks': [{'type': 'command', 'command': 'python start.py'}]}]}}
        installed = install_capture.hook_document(existing)
        self.assertEqual(installed['hooks']['SessionStart'], existing['hooks']['SessionStart'])
        self.assertEqual(installed['hooks']['Stop'][0], existing['hooks']['Stop'][0])
        self.assertEqual(install_capture.hook_document(installed), installed)
        self.assertEqual(install_capture.hook_document(installed, include=False), existing)

    def test_command_hook_receives_stdin_json_and_never_requests_continuation(self):
        config_path = self.base / 'capture-config.json'
        config_path.write_text(json.dumps(self.config), encoding='utf-8')
        command = subprocess.run([sys.executable, str(Path(capture.__file__)), '--config', str(config_path), 'hook'],
                                 input=json.dumps(self.event()), capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(command.returncode, 0, command.stderr)
        self.assertEqual(json.loads(command.stdout), {})
        self.assertEqual(capture.status(self.config)['sessions_pending'], 1)

    def test_messages_written_during_pause_are_not_recovered_on_resume(self):
        self.config['paused_intervals'] = [{'start': '2026-11-24T14:59:00Z', 'end': '2026-11-24T15:01:00Z'}]
        self.message('Un dato después de reanudar.', timestamp='2026-11-24T15:02:00Z')
        self.enqueue()
        def checked(config, messages, catalog):
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0]['text'], 'Un dato después de reanudar.')
            return {'candidates': []}
        self.assertEqual(self.run_worker(checked)['processed'], 1)

    def test_pause_and_resume_record_one_exclusion_interval(self):
        with patch.object(capture.brain, 'stamp', return_value='2026-11-24T15:00:00Z'):
            capture.set_enabled(self.config, False)
            capture.set_enabled(self.config, False)
        with patch.object(capture.brain, 'stamp', return_value='2026-11-24T16:00:00Z'):
            capture.set_enabled(self.config, True)
        self.assertEqual(self.config['paused_intervals'], [{'start': '2026-11-24T15:00:00Z', 'end': '2026-11-24T16:00:00Z'}])

    def checkpoint(self, **kwargs):
        return capture.checkpoint(self.config, session_id='test-1', transcript=self.path,
                                  project=self.project, **kwargs)

    def test_manual_snapshot_and_native_stop_share_deduplication(self):
        self.assertTrue(self.checkpoint()['queued'])
        self.assertEqual(self.checkpoint()['reason'], 'same-snapshot')
        self.assertEqual(self.enqueue()['reason'], 'same-snapshot')
        self.run_worker()
        self.assertEqual(len(self.candidates()), 1)
        self.assertFalse((self.vault / '00-entrada').exists())
        self.message('Puedo continuar después del checkpoint.')
        self.assertTrue(self.enqueue()['queued'])

    def test_manual_event_is_not_accepted_as_native_hook(self):
        self.assertEqual(capture.enqueue(self.config, self.event(hook_event_name='Checkpoint'))['reason'], 'unsupported-event')

    def test_manual_uses_exact_environment_identity_and_never_latest_chat(self):
        self.path = self.path.rename(self.transcripts / 'rollout-test-1.jsonl')
        with patch.dict(capture.os.environ, {'CODEX_THREAD_ID': 'test-1', 'CODEX_SESSION_ID': 'test-1'}):
            self.assertTrue(capture.checkpoint(self.config, project=self.project)['queued'])
        with patch.dict(capture.os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, '--session-id'):
                capture.checkpoint(self.config, project=self.project)
        with patch.dict(capture.os.environ, {'CODEX_THREAD_ID': 'test-1', 'CODEX_SESSION_ID': 'test-2'}):
            with self.assertRaisesRegex(ValueError, 'ambigua'):
                capture.checkpoint(self.config, project=self.project)

    def test_manual_rejects_ambiguous_transcript_and_metadata_mismatch(self):
        original = self.path.read_bytes()
        (self.transcripts / 'a-test-1.jsonl').write_bytes(original)
        (self.transcripts / 'b-test-1.jsonl').write_bytes(original)
        with self.assertRaisesRegex(ValueError, 'ambiguo'):
            capture.checkpoint(self.config, 'test-1', project=self.project)
        with self.assertRaisesRegex(ValueError, 'identidad'):
            capture.checkpoint(self.config, 'test-2', self.path, self.project)
        child = self.project / 'child'
        child.mkdir()
        with self.assertRaisesRegex(ValueError, 'proyecto'):
            capture.checkpoint(self.config, 'test-1', self.path, child)

    def test_manual_respects_scope_pause_worker_and_subagent_exclusion(self):
        self.assertEqual(capture.checkpoint(self.config, 'test-1', self.path, self.base)['reason'], 'outside-pilot')
        self.config['enabled'] = False
        self.assertEqual(self.checkpoint(process_now=True)['reason'], 'disabled-or-worker')
        self.config['enabled'] = True
        with patch.dict(capture.os.environ, {'SECOND_BRAIN_CAPTURE_WORKER': '1'}):
            self.assertEqual(self.checkpoint()['reason'], 'disabled-or-worker')
        self.path.write_text(json.dumps({'type': 'session_meta', 'payload': {
            'id': 'test-1', 'cwd': str(self.project), 'parent_thread_id': 'parent'}}) + '\n', encoding='utf-8')
        self.assertEqual(self.checkpoint()['reason'], 'subagent')

    def test_manual_processing_targets_this_session_and_propagates_error(self):
        with patch.object(capture, 'process', return_value={'processed': 0, 'error': 'Pendiente de revisión'}) as worker:
            result = self.checkpoint(process_now=True)
        worker.assert_called_once_with(self.config, force=True, session_id='test-1')
        self.assertEqual(result['error'], 'Pendiente de revisión')
        with patch.object(capture, 'process', return_value={'processed': 0}) as worker:
            self.checkpoint(process_now=True)  # Same snapshot can still need processing.
        worker.assert_called_once()

    def test_targeted_worker_does_not_consume_another_session_or_bypass_retry(self):
        second = self.transcripts / 'second.jsonl'
        second.write_text(self.path.read_text(encoding='utf-8').replace('test-1', 'test-2'), encoding='utf-8')
        capture.enqueue(self.config, self.event(session_id='test-2', transcript_path=str(second)))
        self.checkpoint()
        result = capture.process(self.config, force=True, extractor=self.extractor, session_id='test-1')
        self.assertEqual(result['session'], 'test-1')
        with capture.database(self.config) as db:
            row = db.execute("SELECT * FROM sessions WHERE id='test-2'").fetchone()
            self.assertEqual(row['cursor'], 0)
            db.execute("UPDATE sessions SET retry_after=? WHERE id='test-2'", (capture.time.time() + 600,))
        self.assertEqual(capture.process(self.config, force=True, extractor=self.extractor, session_id='test-2')['processed'], 0)

    def test_checkpoint_cli_queues_without_model_or_lifecycle_event(self):
        config_path = self.base / 'capture-config.json'
        config_path.write_text(json.dumps(self.config), encoding='utf-8')
        command = subprocess.run([sys.executable, str(Path(capture.__file__)), '--config', str(config_path),
            'checkpoint', '--session-id', 'test-1', '--transcript', str(self.path), '--project', str(self.project)],
            capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(command.returncode, 0, command.stderr)
        self.assertEqual(json.loads(command.stdout)['trigger'], 'manual-checkpoint')
        self.assertEqual(capture.status(self.config)['sessions_pending'], 1)


if __name__ == '__main__':
    unittest.main()
