from rest_framework_simplejwt.authentication import JWTAuthentication

class QueryParamJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.query_params.get('token')
        if raw_token:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        return super().authenticate(request)

