import math


def calculate_pagination_meta(page: int, limit: int, total_items: int) -> dict:
    """Calculate pagination metadata"""
    total_pages = math.ceil(total_items / limit) if limit > 0 else 0
    has_prev_page = page > 1
    has_next_page = page < total_pages

    return {
        "page": page,
        "limit": limit,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_prev_page": has_prev_page,
        "has_next_page": has_next_page
    }
