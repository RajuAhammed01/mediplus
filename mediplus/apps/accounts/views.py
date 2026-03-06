from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import User, VerificationToken
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
import logging

logger = logging.getLogger(__name__)

class RegisterView(generics.CreateAPIView):
    """User Registration API"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Send verification email
            token = VerificationToken.objects.filter(user=user).first()
            if token:
                verification_link = f"{request.scheme}://{request.get_host()}/api/accounts/verify-email/{token.token}/"
                
                send_mail(
                    subject='Verify Your Email - MediPlus',
                    message=f'Click the link to verify your email: {verification_link}',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            
            return Response({
                'message': 'User registered successfully. Please check your email to verify your account.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """User Login API"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class VerifyEmailView(APIView):
    """Email Verification API"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, token):
        try:
            verification_token = VerificationToken.objects.get(token=token)
            if verification_token.is_valid():
                user = verification_token.user
                user.email_verified = True
                user.is_verified = True
                user.save()
                verification_token.delete()
                
                return Response({'message': 'Email verified successfully!'})
            else:
                return Response({'error': 'Token has expired.'}, status=status.HTTP_400_BAD_REQUEST)
        except VerificationToken.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user