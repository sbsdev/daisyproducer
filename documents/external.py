from daisyproducer import settings
from subprocess import call, Popen, PIPE

class DaisyPipeline:

    @staticmethod
    def validate(file_path):
        """Validate a given file_path using the Validator from the Daisy
        Pipeline. Return an empty string if the validation was
        successful. Return a list of error messages as delivered by
        the Daisy Pipeline otherwise."""
        command = (
            "%s/pipeline.sh" % settings.DAISY_PIPELINE_PATH,
            "%s/%s" %  (
                settings.DAISY_PIPELINE_PATH, 
                'scripts/verify/DTBookValidator.taskScript'),
            "--input=%s" % file_path
            )
        return filter(lambda line: line.find('ERROR') != -1, 
                      Popen(command, stdout=PIPE).communicate()[0].splitlines())
        
