from django.conf import settings

class AdminSeparateSessionMiddleware:
    """
    Middleware that ensures requests to the admin site use a separate session cookie.
    This prevents admin logins from overriding or destroying frontend sessions.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.frontend_cookie_name = settings.SESSION_COOKIE_NAME
        self.admin_cookie_name = f"admin_{self.frontend_cookie_name}"

    def __call__(self, request):
        is_admin = request.path.startswith('/admin')

        if is_admin:
            # We are in the admin site. We want SessionMiddleware to use the admin cookie.
            # Temporarily swap the admin cookie into the frontend cookie's place in request.COOKIES.
            admin_session_key = request.COOKIES.get(self.admin_cookie_name)
            if admin_session_key:
                request.COOKIES[self.frontend_cookie_name] = admin_session_key
            elif self.frontend_cookie_name in request.COOKIES:
                # If no admin session exists, hide the frontend session from the admin site
                del request.COOKIES[self.frontend_cookie_name]
        
        response = self.get_response(request)

        if is_admin:
            # Check if SessionMiddleware set or deleted a session cookie
            if self.frontend_cookie_name in response.cookies:
                # Move the cookie to our admin cookie name
                cookie_data = response.cookies[self.frontend_cookie_name]
                response.cookies[self.admin_cookie_name] = cookie_data.value
                for attr, val in cookie_data.items():
                    if val:
                        response.cookies[self.admin_cookie_name][attr] = val
                
                # Remove the frontend cookie from the response so we don't accidentally 
                # overwrite or delete the frontend session in the browser.
                del response.cookies[self.frontend_cookie_name]

        return response
