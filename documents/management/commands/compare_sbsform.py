# coding=utf-8
from codecs import open 
from daisyproducer.documents.external import SBSForm, Pipeline2
from django.core.management.base import BaseCommand
from tempfile import NamedTemporaryFile

class Command(BaseCommand):
    args = 'DTBook'
    help = 'Compare results from old and new dtbook2sbsform'
    
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Incorrect number of arguments')
        try:
            f = open(args[0], "r", "utf-8" )
        except IndexError:
            raise CommandError('No DTBbook file specified')
        except IOError:
            raise CommandError('DTBook file "%s" not found' % args[0])

        f = f.name
        
        a = NamedTemporaryFile(prefix="daisyproducer-", suffix=".sbsform", delete=False)
        a.close()
        a = a.name

        self.log("Running old dtbook2sbsform...")

        SBSForm.dtbook2sbsform(f, a)

        self.log("Running new dtbook2sbsform...")
        
        b = Pipeline2.dtbook2sbsform(f, [])

        if isinstance(b, tuple):
            errorMessages = b
            print errorMessages
            return
        
        self.log("diff %s %s" % (a,b))


    def log(self, message):
        self.stdout.write("%s\n" % message)