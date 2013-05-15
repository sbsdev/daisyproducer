"""
A storage implementation that overwrites exiting files in the storage

See "Writing a custom storage system"
(https://docs.djangoproject.com/en/1.3/howto/custom-file-storage/) and
the discussion on stackoverflow on "ImageField overwrite image file"
(http://stackoverflow.com/questions/9522759/imagefield-overwrite-image-file)
"""

from django.core.files.storage import FileSystemStorage

class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name):
        return name
