import pytest
import json
from agents.web_ui import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b"KaliGPT" in res.data
    assert b"Dynamic Web View" in res.data

def test_api_status(client):
    res = client.get('/api/status')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "online"
    assert "default_provider" in data
    assert "tools_count" in data

def test_api_config(client):
    res = client.get('/api/config')
    assert res.status_code == 200
    data = res.get_json()
    assert "default_provider" in data

def test_api_tools(client):
    res = client.get('/api/tools')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, dict)
    assert len(data) > 0

def test_api_config_update(client):
    from agents.utils.agent_configs import _load_config, _save_config
    orig_cfg = _load_config()
    try:
        res = client.post('/api/config/update', json={
            "provider": "ollama",
            "model": "qwen3.5-9b-uncensored-hauhaucs-aggressive"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
    finally:
        _save_config(orig_cfg)

def test_chat_empty_prompt(client):
    res = client.post('/api/chat', json={"prompt": ""})
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False

def test_tool_execution(client):
    res = client.post('/api/tools/execute', json={
        "tool": "execute_generic_linux_command",
        "args": {"command": "echo 'kaligpt'"}
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "result" in data
    assert "kaligpt" in str(data["result"])

def test_tool_not_found(client):
    res = client.post('/api/tools/execute', json={"tool": "non_existent_tool"})
    assert res.status_code == 404

