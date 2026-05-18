from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class AccessPasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        login_url = reverse("login")
        allowed_prefixes = (
            login_url,
            settings.STATIC_URL,
            "/admin/",
        )

        if not request.session.get("access_authenticated") and not request.path.startswith(allowed_prefixes):
            return redirect("login")

        return self.get_response(request)
