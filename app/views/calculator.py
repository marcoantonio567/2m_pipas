from django.views.generic import TemplateView


class CalculatorView(TemplateView):
    """Exibe a calculadora de conversao entre metros e jardas."""

    template_name = "calculadora/html/calculadora.html"
