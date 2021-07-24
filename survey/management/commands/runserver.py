from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand
from django_sass import compile_sass

class Command(RunserverCommand):
    help = 'Starts a lightweight Web server for development. Compiles SCSS files and collects static files beforehand.'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        
        parser.add_argument(
            '--sassin',
            type=str,
            default='./survey/static/survey/scss/',
            help='An SCSS file or a directory containing SCSS files.',
            dest='sassin',
        )
        parser.add_argument(
            '--sassout',
            type=str,
            default='./survey/static/survey/css/',
            help='A file or a directory in which to output transpiled CSS.',
            dest='sassout',
        )
        parser.add_argument(
            "--sassstyle",
            type=str,
            default='compressed',
            help='Output type. One of "expanded", "nested", "compact", or "compressed"',
            dest='sassstyle',
        )

    def handle(self, *args, **options):
        sassin = options['sassin']
        sassout = options['sassout']
        sassstyle = options['sassstyle']

        self.stdout.write('Transpiling SCSS files (in: "%s"; out: "%s")' % (sassin, sassout))
        compile_sass(
            inpath=sassin,
            outpath=sassout,
            output_style=sassstyle,
            precision=8,
            source_map=False,
        )
        super().handle(*args, **options)
