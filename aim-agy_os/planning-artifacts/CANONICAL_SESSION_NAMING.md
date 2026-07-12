# Canonical Session Naming API

- **File**: `aim-agy_os/.aim_core/session_naming.py`
- **Default Vessel ID**: `agy` (override via environment variable `AIM_VESSEL_CLI`)
- **Format Schema**: `{vessel}_{role}_{project_slug}_{unix_timestamp}`
- **Core Builder**: `build_agent_session_name(role: str, workspace_dir: str | None = None, env: dict | None = None, *, timestamp: int | None = None) -> str`
- **Legacy Wrapper**: `reincarnation_session_name(workspace_dir: str | None = None, env: dict | None = None, *, timestamp: int | None = None) -> str` (resolves to role `"reincarnate"`)
- **Matcher**: `is_agent_session_role(name: str, role: str, env: dict | None = None) -> bool`
