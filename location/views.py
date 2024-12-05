from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User
from .serializers import UserSerializer
from .forms import SignUpForm

class UserSignUpView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle form submission and create a user via API.
        """
        form = SignUpForm(request.POST)
        if form.is_valid():
            data = {
                'username': request.POST.get('username'),
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
            }
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return render(request, "sign_up_success.html")
            return render(request, "400.html", {'errors': serializer.errors})
        context = {'form': form}
        return render(request, "sign_up.html", context)

    def get(self, request, *args, **kwargs):
        """
        Render the HTML template for sign-up.
        """
        context = {"form": SignUpForm()}
        return render(request, "sign_up.html", context)
