"""Analytics middleware — tracks page views automatically."""
from .models import PageView


class PageViewMiddleware:
    """Logs every page view (except static/media/admin)."""

    EXCLUDE_PREFIXES = ['/static/', '/media/', '/admin/', '/api-auth/', '/swagger/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Skip if not a GET or excluded path
        if request.method != 'GET':
            return response
        
        path = request.path
        if any(path.startswith(p) for p in self.EXCLUDE_PREFIXES):
            return response

        # Log the page view
        try:
            user = request.user if request.user.is_authenticated else None
            PageView.objects.create(user=user, url=path)
        except Exception:
            pass  # Never break the request for analytics

        return response
