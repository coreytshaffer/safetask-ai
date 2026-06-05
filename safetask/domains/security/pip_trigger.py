def trigger_camera_spawn(asset_id: str, location: str) -> dict:
    return {
        'action': 'spawn_pip',
        'camera_feed': f'{location}_cam',
        'focus_asset': asset_id
    }