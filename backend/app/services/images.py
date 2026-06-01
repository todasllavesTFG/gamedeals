def steam_header_image_url(steam_app_id: str | int | None) -> str | None:
    if not steam_app_id:
        return None
    return f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{steam_app_id}/header.jpg"


def game_image_url(image_url: str | None, steam_app_id: str | int | None) -> str | None:
    return image_url or steam_header_image_url(steam_app_id)
