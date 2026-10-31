"""Public synthetic wire examples; no Python sizing or matching implementation."""
import hashlib
import json
import os
from pathlib import Path

import pytest

from portfolio_backtester.backends.engine_sessions import EngineClient, EngineProtocolError

FIXTURES = Path(__file__).parent / 'fixtures' / 'engine_sessions'


def request(name='request'):
    return json.loads((FIXTURES / f'{name}.json').read_text())


def executable(tmp_path, response):
    path = tmp_path / 'engine with spaces'
    path.write_text('#!/usr/bin/env python3\nprint(' + repr(json.dumps(response)) + ')\n')
    path.chmod(0o700)
    return EngineClient(path, hashlib.sha256(path.read_bytes()).hexdigest())


def test_explicit_pin_and_timeout(tmp_path):
    with pytest.raises(ValueError):
        EngineClient(Path('relative'), '0' * 64)
    client = executable(tmp_path, {})
    client.executable.write_text('changed')
    with pytest.raises(EngineProtocolError, match='digest'):
        client.size(request('sizing'))
    with pytest.raises(ValueError):
        EngineClient(client.executable, '0' * 64, timeout=0)


def test_invalid_sizing_response(tmp_path):
    with pytest.raises(EngineProtocolError):
        executable(tmp_path, {'schema_version': 'sizing_result.v1'}).size(request('sizing'))


@pytest.mark.parametrize('value', ['NaN', 'Infinity', '-1', '1.5'])
def test_invalid_quantity(tmp_path, value):
    result = {'schema_version': 'sizing_result.v1', 'currency': 'CNY',
              'marked_equity': '1000', 'projected_cash': '9.01',
              'orders': [{'id': 'buy-AAA', 'symbol': 'AAA', 'side': 'buy',
                          'information_ts_ns': 1735689600000000000, 'quantity': value}],
              'targets': [{'symbol': 'AAA', 'desired_quantity': '100', 'planned_quantity': '99'}]}
    with pytest.raises(EngineProtocolError):
        executable(tmp_path, result).size(request('sizing'))


def test_request_nonfinite_rejected(tmp_path):
    payload = request('sizing')
    payload['cash'] = float('nan')
    with pytest.raises(EngineProtocolError):
        executable(tmp_path, {}).size(payload)


def test_real_binary():
    binary = os.environ.get('SESSION_ENGINE_BINARY')
    if not binary:
        pytest.skip('set SESSION_ENGINE_BINARY and SESSION_ENGINE_SHA256 for integration')
    client = EngineClient(Path(binary), os.environ['SESSION_ENGINE_SHA256'])
    sized = client.size(request('sizing'))
    assert sized['targets'][0]['planned_quantity'] == '99'
    result = client.run_sessions(request())
    result.validate()
    assert len(result.daily_ledger) == 2
    assert len(result.fills) == 2
    assert result.metadata['engine_result']['rejections']
    assert result.unified_ledger is None
    assert result.daily_ledger.iloc[-1]['nav'] == pytest.approx(10197.8)
    # Fixed-point Money uses half-even cents; marks retain raw precision.
    for price, cash in [('10.0050', 9990.0), ('10.0150', 9989.98)]:
        payload = request()
        payload.update(currency='USD', fee_bps='0', enforce_t1=False)
        payload['instruments'][0].update(price_precision=4, buy_lot=1)
        payload['sessions'] = payload['sessions'][:1]
        session = payload['sessions'][0]
        session['orders'] = session['orders'][:1]
        session['orders'][0]['quantity'] = '1'
        for quote in session['quotes']:
            quote.update(bid=price, ask=price)
        replay = client.run_sessions(payload)
        assert replay.daily_ledger.iloc[0]['cash'] == cash
        assert 'configured_t_plus_one' not in replay.capabilities.market_rules


def test_subprocess_timeout(tmp_path):
    path = tmp_path / 'sleep-engine'
    path.write_text('#!/usr/bin/env python3\nimport time\ntime.sleep(2)\n')
    path.chmod(0o700)
    client = EngineClient(path, hashlib.sha256(path.read_bytes()).hexdigest(), timeout=0.01)
    with pytest.raises(EngineProtocolError, match='timed out'):
        client.size(request('sizing'))


def test_buy_lot_and_missing_order(tmp_path):
    result = {'schema_version': 'sizing_result.v1', 'currency': 'CNY',
              'marked_equity': '1000', 'projected_cash': '9.01',
              'orders': [{'id': 'buy-AAA', 'symbol': 'AAA', 'side': 'buy',
                          'information_ts_ns': 1735689600000000000, 'quantity': '99'}],
              'targets': [{'symbol': 'AAA', 'desired_quantity': '100', 'planned_quantity': '99'}]}
    payload = request('sizing')
    payload['assets'][0]['buy_lot'] = 100
    with pytest.raises(EngineProtocolError, match='lot'):
        executable(tmp_path, result).size(payload)
    result['orders'] = []
    with pytest.raises(EngineProtocolError, match='missing sizing orders'):
        executable(tmp_path, result).size(payload)


@pytest.mark.parametrize('mutation', ['cash', 'fills', 'positions', 'rejections', 'timezone'])
def test_malformed_session_evidence(tmp_path, mutation):
    result = json.loads((FIXTURES / 'result.json').read_text())
    if mutation == 'cash':
        result['daily_ledger'][0]['cash'] = '9000'
    elif mutation == 'fills':
        result['fills'][0]['quantity'] = 'NaN'
    elif mutation == 'positions':
        result['daily_positions'][0]['quantity'] = '101'
    elif mutation == 'rejections':
        result['rejections'] = []
    else:
        result['valuation_timezone'] = 'UTC'
    with pytest.raises(EngineProtocolError):
        executable(tmp_path, result).run_sessions(request())


def test_canonical_mapping_preserves_denial_and_metadata(tmp_path):
    result = json.loads((FIXTURES / 'result.json').read_text())
    canonical = executable(tmp_path, result).run_sessions(request())
    assert canonical.metadata['engine_result'] == result
    assert canonical.orders.iloc[1]['rejection']['reason'] == 'SELLABLE_QUANTITY'
    assert canonical.positions.iloc[0]['weight'] == pytest.approx(1100 / 10099)
    assert canonical.describe()['row_counts']['orders'] == 3


def test_no_implicit_schema_upgrade(tmp_path):
    payload = request()
    payload['schema_version'] = 'engine_request.v1'
    with pytest.raises(EngineProtocolError, match='request schema'):
        executable(tmp_path, {}).run_sessions(payload)


def test_usd_and_empty_order_sessions(tmp_path):
    payload = request()
    payload['currency'] = 'USD'
    result = json.loads((FIXTURES / 'result.json').read_text())
    result['currency'] = 'USD'
    result['valuation_timezone'] = 'UTC'
    for session in payload['sessions']:
        session['orders'] = []
    for key in ('orders', 'fills', 'rejections', 'daily_positions'):
        result[key] = []
    result['final_cash'] = result['final_nav'] = '10000'
    result['total_commission'] = '0'
    for row in result['daily_ledger']:
        row.update(cash='10000', nav='10000', positions_value='0', commission='0')
    canonical = executable(tmp_path, result).run_sessions(payload)
    canonical.validate()
    assert canonical.fills.empty and canonical.orders.empty and canonical.positions.empty
    assert canonical.metadata['engine_result']['valuation_timezone'] == 'UTC'


def test_one_cent_wire_discrepancy_is_rejected(tmp_path):
    result = json.loads((FIXTURES / 'result.json').read_text())
    result['daily_ledger'][0]['cash'] = '8999.01'
    result['daily_ledger'][0]['nav'] = '10099.01'
    with pytest.raises(EngineProtocolError):
        executable(tmp_path, result).run_sessions(request())


@pytest.mark.parametrize('status', ['NOT_SUBMITTED', 'EXPIRED'])
def test_terminal_unfilled_status(tmp_path, status):
    result = json.loads((FIXTURES / 'result.json').read_text())
    result['orders'][1]['status'] = status
    result['rejections'] = []
    executable(tmp_path, result).run_sessions(request()).validate()


@pytest.mark.parametrize('mutation', ['backend', 'extra', 'event', 'partial'])
def test_strict_wire_schema(tmp_path, mutation):
    result = json.loads((FIXTURES / 'result.json').read_text())
    if mutation == 'backend':
        result['backend_version'] = 'unknown'
    elif mutation == 'extra':
        result['fills'][0]['extra'] = 'unknown'
    elif mutation == 'event':
        result['rejections'][0]['event_type'] = 'rejected'
    else:
        result['orders'][0]['status'] = 'PARTIALLY_FILLED'
    with pytest.raises(EngineProtocolError):
        executable(tmp_path, result).run_sessions(request())


def test_verified_snapshot_survives_path_replacement(tmp_path, monkeypatch):
    import subprocess
    result = json.loads((FIXTURES / 'result.json').read_text())
    client = executable(tmp_path, result)
    run = subprocess.run

    def replace_then_run(*args, **kwargs):
        replacement = tmp_path / 'replacement'
        replacement.write_text('#!/bin/sh\necho malicious\n')
        replacement.chmod(0o700)
        replacement.replace(client.executable)
        return run(*args, **kwargs)

    monkeypatch.setattr(subprocess, 'run', replace_then_run)
    client.run_sessions(request()).validate()
