from daisyproducer import settings
from subprocess import call

class DaisyPipeline:

    @staticmethod
    def validate(file_path):
        command = (
            "%s/pipeline.sh" % settings.DAISY_PIPELINE_PATH,
            "%s/%s" %  (
                settings.DAISY_PIPELINE_PATH, 
                'scripts/verify/DTBookValidator.taskScript'),
            "--input=%s" % file_path
            )
        exitStatus = call(command)
        return exitStatus
        
