"""Windows-only end-to-end context budgeting through the actual Jarvis owner."""
import json
import os
from pathlib import Path
import sys

if os.name != 'nt':
    raise SystemExit('Windows-only integration proof.')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from local_model.native_chat_adapter import NativeChatAdapter
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeConversationSession
from local_model.memory_preferences import MemoryPreferences

root = Path(sys.argv[1]).resolve()
config = NativeModelConfig(model=str(Path(sys.argv[2]).resolve(strict=True)),
    dll=str(root / 'koboldcpp_noavx2.dll'), context_size=2048, max_output=32,
    threads=2, temperature=0.1, seed=123)
adapter = NativeChatAdapter(root / 'koboldcpp.py')
adapter.prepare(config=config)
k = adapter.provider.bridge.upstream
original_load, original_generate = k.load_model, k.generate
loads, generations = [], []
def load(model):
    loads.append(model)
    return original_load(model)
def generate(arguments):
    result = original_generate(arguments)
    generations.append((arguments['prompt'], result))
    return result
k.load_model, k.generate = load, generate
session = NativeConversationSession(adapter, config_loader=lambda: config,
                                    memory_loader=MemoryPreferences)
metrics = []
try:
    for question in ('Saluta brevemente in italiano.', 'Perché hai risposto così?'):
        turn = session.prepare_turn(question)
        prompt, result = generations[-1]
        if turn.context_metrics['unit'] != 'tokens':
            raise RuntimeError('Exact native policy was not activated.')
        if turn.context_metrics['input_size'] != result['prompt_tokens']:
            raise RuntimeError('Jarvis/backend input token mismatch.')
        if result['prompt_tokens'] + config.max_output + 128 > config.context_size:
            raise RuntimeError('Physical context overflow.')
        if not turn.commit():
            raise RuntimeError('Turn acceptance failed.')
        metrics.append(turn.context_metrics)
    if len(loads) != 1 or len(generations) != 2:
        raise RuntimeError('Extra model load or generation.')
    if 'Saluta brevemente in italiano.' not in generations[1][0]:
        raise RuntimeError('Immediate history missing from actual native input.')
    # Reopen a bounded SQLite archive and a fresh session, using the same native
    # owner: tests restoration without a redundant model allocation.
    from tempfile import TemporaryDirectory
    from second_brain import SecondBrain
    with TemporaryDirectory() as folder:
        path = Path(folder) / 'brain.sqlite3'
        SecondBrain(path).remember_turn('Parliamo di Mussolini',
            'Una spiegazione storica dettagliata. ' * 90 + 'Clown era una metafora conclusiva.')
        brain = SecondBrain(path)
        def read(budget):
            return ''
        read.recent_pairs = brain.dialogue_pairs
        restored = NativeConversationSession(adapter, config_loader=lambda: config,
                                            memory_loader=MemoryPreferences)
        turn = restored.prepare_turn('Perché hai detto clown?', memory_context=read)
        prompt, result = generations[-1]
        if 'clown era una metafora' not in prompt.casefold() or 'Parliamo di Mussolini' not in prompt:
            raise RuntimeError('Restored reference missing from actual native input.')
        if turn.context_metrics['input_size'] != result['prompt_tokens']:
            raise RuntimeError('Restored prompt tokenizer mismatch.')
        if len(loads) != 1 or len(generations) != 3 or not turn.commit():
            raise RuntimeError('Restoration added a model load/generation or failed acceptance.')
        metrics.append(turn.context_metrics)
    report = dict(proof='Jarvis_native_context_integration', model_loads=len(loads),
                  generations=len(generations), metrics=metrics, pavilion_verified=False)
    Path('native-context-integration-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('NATIVE_CONTEXT_INTEGRATION=' + json.dumps(report))
finally:
    session.close()
