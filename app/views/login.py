from django.shortcuts import redirect, render
from django.views import View


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

        return redirect("menu")
