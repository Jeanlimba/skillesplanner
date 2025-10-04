# clients/middleware.py
from django.utils.deprecation import MiddlewareMixin
from .models import ProfilUtilisateur

class ClientMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                request.profil = ProfilUtilisateur.objects.get(user=request.user)
                request.client = request.profil.client
            except ProfilUtilisateur.DoesNotExist:
                request.profil = None
                request.client = None
        else:
            request.profil = None
            request.client = None