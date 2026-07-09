"""
Middleware for cache control headers.
"""

from django.utils.deprecation import MiddlewareMixin
from django.utils.cache import patch_cache_control, get_max_age
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class CacheControlMiddleware(MiddlewareMixin):
    """
    Middleware for setting cache control headers.
    """

    def process_response(self, request, response):
        """
        Add cache control headers to responses.
        """
        # Skip for authenticated requests (private)
        if request.user.is_authenticated:
            patch_cache_control(response, private=True, max_age=60)
            return response

        # Public caching for static-like endpoints
        if request.path.startswith("/api/content/"):
            patch_cache_control(response, public=True, max_age=300)
        elif request.path.startswith("/api/progress/"):
            patch_cache_control(response, private=True, max_age=60)
        elif request.path.startswith("/api/leaderboard/"):
            patch_cache_control(response, public=True, max_age=120)

        return response
class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware with Redis."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.limiter = RateLimiter()

    def __call__(self, request):
        # Skip for admin, static, health
        skip_paths = ['/admin/', '/static/', '/health/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)

        # Get client identifier
        ip = request.META.get('REMOTE_ADDR')
        if request.user.is_authenticated:
            key = f"{ip}:{request.user.id}"
        else:
            key = ip

        # Check rate limit
        if not self.limiter.is_allowed(key):
            remaining = self.limiter.get_remaining(key)
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'remaining': remaining
            }, status=429)

        response = self.get_response(request)
        response['X-RateLimit-Remaining'] = str(self.limiter.get_remaining(key))
        return response
