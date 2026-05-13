def paginate_query(query, page: int, per_page: int = 20):
    """
    Apply pagination to a SQLAlchemy query.
    Returns a dict with items and pagination metadata.
    """
    per_page = min(per_page, 100)  # cap at 100 per page
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": paginated.items,
        "pagination": {
            "page": paginated.page,
            "per_page": paginated.per_page,
            "total": paginated.total,
            "pages": paginated.pages,
            "has_next": paginated.has_next,
            "has_prev": paginated.has_prev,
        },
    }
