from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Setup Google OAuth credentials'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, help='Google OAuth Client ID')
        parser.add_argument('--client-secret', type=str, help='Google OAuth Client Secret')
        parser.add_argument('--domain', type=str, default='localhost:3000', help='Site domain')

    def handle(self, *args, **options):
        # Get or create site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': options['domain'],
                'name': 'Checkin Project'
            }
        )
        if not created:
            site.domain = options['domain']
            site.name = 'Checkin Project'
            site.save()
        
        self.stdout.write(f'Site: {site.domain}')

        # Get or create Google app
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            name='Google',
            defaults={
                'client_id': options.get('client_id', 'your-google-client-id-here'),
                'secret': options.get('client_secret', 'your-google-client-secret-here'),
            }
        )

        # Update credentials if provided
        if options.get('client_id'):
            google_app.client_id = options['client_id']
        if options.get('client_secret'):
            google_app.secret = options['client_secret']
        google_app.save()

        # Add site to app
        google_app.sites.add(site)

        self.stdout.write(
            self.style.SUCCESS(
                f'Google OAuth app configured successfully!\n'
                f'Client ID: {google_app.client_id}\n'
                f'Sites: {list(google_app.sites.all())}'
            )
        )
