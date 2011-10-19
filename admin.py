from django.contrib import admin

try:

    from session_csrf import anonymous_csrf


    class CustomAdminSite(admin.AdminSite):
        
        def login(self, request):
            @anonymous_csrf
            def wrapper(request):
                return super(CustomAdminSite, self).login(request)
            return wrapper(request)


    # Monkey patching the admin site
    def monkey_patch_admin():
        import django
        django.contrib.admin.site = CustomAdminSite()


except ImportError:
    pass
