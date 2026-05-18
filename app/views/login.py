from django.shortcuts import redirect, render
from django.views import View

from app.models import AccessPassword


class LoginView(View):
    template_name = "login/html/login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        password = request.POST.get("password", "").strip()

        if not password or not password.isdigit():
            return render(
                request,
                self.template_name,
                {"error": "A senha deve conter apenas numeros."},
            )

        access_password = AccessPassword.objects.filter(is_active=True).order_by("-created_at").first()
        if not access_password or password != access_password.password:
            return render(
                request,
                self.template_name,
                {"error": "Senha incorreta."},
            )

        return redirect("menu")
