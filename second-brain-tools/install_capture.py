"""Preview/install/pause/remove personal hooks and the hourly review-first capture task."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib
import uuid

import brain
import capture

ROOT = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))).resolve()
HOOKS = HOME / 'hooks.json'
CONFIG = capture.DEFAULT_CONFIG
MANIFEST = ROOT / '.second-brain-runtime/capture-installation.json'
TASK = 'SecondBrain-CapturePilot'


def owned(handler):
    return str(ROOT / 'second-brain-tools/capture.py').replace('\\', '/').casefold() in str(handler.get('command', '')).replace('\\', '/').casefold()


def hook_document(previous, include=True):
    document = json.loads(json.dumps(previous))
    events = document.setdefault('hooks', {})
    command = subprocess.list2cmdline([sys.executable, str(ROOT / 'second-brain-tools/capture.py'), '--config', str(CONFIG), 'hook'])
    for event in ['Stop', 'SessionEnd']:
        groups = []
        for group in events.get(event, []):
            cleaned = {**group, 'hooks': [handler for handler in group.get('hooks', []) if not owned(handler)]}
            if cleaned['hooks']:
                groups.append(cleaned)
        if include:
            groups.append({'hooks': [{'type': 'command', 'command': command, 'timeout': 3,
                                      'statusMessage': 'Encolando candidatos del Second Brain'}]})
        if groups:
            events[event] = groups
        else:
            events.pop(event, None)
    return document


def configuration():
    if CONFIG.exists():
        return capture.load_config(CONFIG)
    codex = shutil.which('codex')
    if not codex:
        raise ValueError('No se encontró codex en PATH')
    current = tomllib.loads((HOME / 'config.toml').read_text(encoding='utf-8-sig')) if (HOME / 'config.toml').exists() else {}
    return {'enabled': True, 'vault': str(ROOT / 'second-brain'),
            'allowed_roots': [str(ROOT)], 'transcript_roots': [str(HOME / 'sessions')],
            'activated_utc': brain.stamp(), 'codex': codex, 'model': current.get('model'),
            'debounce_seconds': 600, 'model_timeout_seconds': 180,
            'mode': 'review-first', 'auto_publish': False}


def task_script(remove=False):
    # Pass paths as UTF-8 JSON, never interpolate user paths into PowerShell source.
    descriptor = ROOT / '.second-brain-runtime/capture-task.json'
    descriptor.parent.mkdir(parents=True, exist_ok=True)
    pythonw = Path(sys.executable).with_name('pythonw.exe')
    if not pythonw.is_file():
        raise ValueError('Se requiere pythonw.exe para la tarea oculta de Windows')
    descriptor.write_text(json.dumps({'name': TASK, 'python': str(pythonw),
        'arguments': subprocess.list2cmdline([str(ROOT / 'second-brain-tools/capture.py'), '--config', str(CONFIG), 'process']),
        'cwd': str(ROOT)}, ensure_ascii=False), encoding='utf-8')
    script = ROOT / '.second-brain-runtime/manage-capture-task.ps1'
    script.write_text('''param([string]$Descriptor, [switch]$Remove)
$ErrorActionPreference = 'Stop'
$definition = Get-Content -Raw -LiteralPath $Descriptor -Encoding UTF8 | ConvertFrom-Json
$existing = Get-ScheduledTask -TaskName $definition.name -ErrorAction SilentlyContinue
if ($existing -and $existing.Description -ne 'WORKFLOW second-brain review-first pilot') {
    throw 'Ya existe una tarea ajena con el mismo nombre; no se reemplazará.'
}
if ($Remove) {
    if ($existing) { Unregister-ScheduledTask -TaskName $definition.name -Confirm:$false }
    exit 0
}
$action = New-ScheduledTaskAction -Execute $definition.python -Argument $definition.arguments -WorkingDirectory $definition.cwd
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Hours 1)
$principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -Hidden -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
if ($existing -and [string]$existing.State -eq 'Queued') { Stop-ScheduledTask -TaskName $definition.name }
Register-ScheduledTask -TaskName $definition.name -Description 'WORKFLOW second-brain review-first pilot' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
$actual = Get-ScheduledTask -TaskName $definition.name
if ($actual.Actions.Execute -ne $definition.python) { throw 'La verificación de la tarea falló' }
''', encoding='utf-8-sig')
    return ['powershell.exe', '-NoProfile', '-NonInteractive', '-WindowStyle', 'Hidden', '-File', str(script), '-Descriptor', str(descriptor)] + (['-Remove'] if remove else [])


def check():
    hooks = json.loads(HOOKS.read_text(encoding='utf-8-sig')) if HOOKS.exists() else {}
    config = configuration()
    counts = {event: sum(owned(handler) for group in hooks.get('hooks', {}).get(event, []) for handler in group.get('hooks', [])) for event in ['Stop', 'SessionEnd']}
    result = {'config': str(CONFIG), 'hooks_file': str(HOOKS), 'owned_hooks': counts,
              'enabled': config['enabled'], 'auto_publish': False,
              'trust': 'Debe comprobarse en /hooks del cliente; no se modifica la confianza por archivo',
              'manifest_exists': MANIFEST.exists()}
    if os.name == 'nt':
        query = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command',
             "$ErrorActionPreference='Stop'; Get-ScheduledTask -TaskName 'SecondBrain-CapturePilot' -ErrorAction Stop | Select-Object TaskName,State,@{n='Execute';e={$_.Actions.Execute}},@{n='Arguments';e={$_.Actions.Arguments}} | ConvertTo-Json -Compress"], capture_output=True, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
        result['scheduled_task'] = json.loads(query.stdout) if query.stdout.strip() else None
        if query.returncode:
            result['scheduled_task_query_error'] = 'No se pudo consultar la tarea: comprobar permisos del entorno o su existencia. No significa que la tarea no exista.'
    return result


def apply(remove=False):
    previous = json.loads(HOOKS.read_text(encoding='utf-8-sig')) if HOOKS.exists() else {}
    updated = hook_document(previous, include=not remove)
    config = configuration()
    capture.set_enabled(config, not remove)
    backup = ROOT / 'second-brain-backups' / ('capture-' + brain.stamp().replace(':', '') + '-' + uuid.uuid4().hex[:6])
    backup.mkdir(parents=True)
    for name, path in [('hooks.json', HOOKS), ('capture-config.json', CONFIG), ('installation.json', MANIFEST)]:
        if path.exists():
            shutil.copy2(path, backup / name)
    brain.atomic_text(CONFIG, json.dumps(config, ensure_ascii=False, indent=2) + '\n')
    # Only hooks owned by this exact helper path are added/removed.
    brain.atomic_text(HOOKS, json.dumps(updated, ensure_ascii=False, indent=2) + '\n')
    task_result = {'returncode': None}
    if os.name == 'nt':
        execution = subprocess.run(task_script(remove), capture_output=True, text=True, encoding='utf-8', errors='replace', creationflags=subprocess.CREATE_NO_WINDOW)
        task_result = {'returncode': execution.returncode, 'detail': execution.stderr.strip()[:1200]}
    manifest = {'managed_by': 'workflow-second-brain-capture', 'installed_utc': brain.stamp(),
                'hooks_file': str(HOOKS), 'config': str(CONFIG), 'backup': str(backup),
                'scheduled_task': TASK, 'task_result': task_result, 'removed': remove}
    brain.atomic_text(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    capture.render(config)
    return {**manifest, 'check': check()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument('--apply', action='store_true')
    operation.add_argument('--check', action='store_true')
    operation.add_argument('--pause', action='store_true')
    operation.add_argument('--remove', action='store_true')
    args = parser.parse_args()
    if args.check:
        result = check()
    elif args.pause:
        config = configuration()
        capture.set_enabled(config, False)
        brain.atomic_text(CONFIG, json.dumps(config, ensure_ascii=False, indent=2) + '\n')
        capture.render(config)
        result = {'paused': True, 'data_preserved': True}
    elif args.apply or args.remove:
        result = apply(args.remove)
    else:
        existing = json.loads(HOOKS.read_text(encoding='utf-8-sig')) if HOOKS.exists() else {}
        result = {'preview': True, 'hooks_file': str(HOOKS), 'hooks_proposed': hook_document(existing),
                  'configuration_proposed': configuration(), 'task': TASK, 'cadence': 'cada hora, con usuario conectado',
                  'auto_publish': False, 'trust_step': 'Revisar las dos definiciones en /hooks; reiniciar cliente si es necesario'}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get('task_result', {}).get('returncode') not in {None, 0} else 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
