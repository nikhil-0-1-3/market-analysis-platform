from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'ok'


def test_overview() -> None:
    res = client.get('/api/v1/intelligence/overview')
    assert res.status_code == 200
    assert res.json()['platform'] == 'AI Market-Intelligence Platform'


def test_connector_sources_and_status() -> None:
    sources = client.get('/api/v1/intelligence/connectors/sources')
    assert sources.status_code == 200
    data = sources.json()
    assert 'news' in data and 'social' in data

    status = client.get('/api/v1/intelligence/connectors/status')
    assert status.status_code == 200
    st = status.json()
    assert 'cached_events' in st
    assert 'provider_counts' in st


def test_sample_events_connector() -> None:
    res = client.get('/api/v1/intelligence/connectors/sample-events?limit=3&region=IN')
    assert res.status_code == 200
    events = res.json()
    assert len(events) <= 3
    assert all(item['region'] == 'IN' for item in events)


def test_live_events_include_provider_metadata() -> None:
    events = client.get('/api/v1/intelligence/connectors/live-events?limit=5&region=IN')
    assert events.status_code == 200
    rows = events.json()
    assert len(rows) <= 5
    if rows:
        assert 'provider' in rows[0]
        assert 'engagement_score' in rows[0]


def test_live_signals() -> None:
    res = client.get('/api/v1/intelligence/live-signals?region=IN')
    assert res.status_code == 200
    body = res.json()
    assert body['region'] == 'IN'
    assert len(body['signals']) >= 1


def test_analyze_event_and_signal_flow() -> None:
    event = {
        'source': 'news',
        'provider': 'economic_times_markets',
        'headline': 'Reliance reports strong growth in refining margins',
        'body': 'Company beat consensus and guided stronger quarter.',
        'symbols': ['NSE:RELIANCE'],
        'sectors': ['Energy'],
        'region': 'IN',
    }

    analysis = client.post('/api/v1/intelligence/analyze-event', json=event)
    assert analysis.status_code == 200

    signal_payload = {
        'event': event,
        'price_action': {
            'symbol': 'NSE:RELIANCE',
            'volume_spike': 2.4,
            'volatility': 1.8,
            'trend_score': 0.6,
        },
    }
    signal = client.post('/api/v1/intelligence/generate-signal', json=signal_payload)
    assert signal.status_code == 200
    assert 0 <= signal.json()['confidence_score'] <= 1


def test_ingest_batch_and_watchlist() -> None:
    batch_payload = {
        'events': [
            {
                'source': 'news',
                'provider': 'business_standard_markets',
                'headline': 'Large private bank updates growth guidance',
                'body': 'Expectations revised upward.',
                'symbols': ['NSE:HDFCBANK'],
                'sectors': ['Banking'],
                'region': 'IN',
            },
            {
                'source': 'social',
                'provider': 'reddit_indianstreetbets',
                'headline': 'IT companies trend with rising project wins',
                'body': 'Channel checks show stronger pipeline.',
                'symbols': ['NSE:TCS'],
                'sectors': ['IT'],
                'region': 'IN',
            },
        ]
    }
    batch = client.post('/api/v1/intelligence/ingest-batch', json=batch_payload)
    assert batch.status_code == 200
    assert batch.json()['count'] == 2

    watchlist_payload = {
        'symbols': ['NSE:INFY', 'NSE:ICICIBANK'],
        'region': 'IN',
        'source': 'market',
    }
    scan = client.post('/api/v1/intelligence/scan-watchlist', json=watchlist_payload)
    assert scan.status_code == 200
    assert scan.json()['count'] == 2


def test_send_alert() -> None:
    payload = {
        'channel': 'telegram',
        'recipient': '@demo_channel',
        'title': 'Signal Alert',
        'message': 'Potential intraday move on NSE:RELIANCE',
    }
    res = client.post('/api/v1/intelligence/send-alert', json=payload)
    assert res.status_code == 200
    assert res.json()['delivered'] is True
