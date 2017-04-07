"""
A storage implementation that overwrites exiting files in the storage

See "Writing a custom storage system"
(https://docs.djangoproject.com/en/1.3/howto/custom-file-storage/) and
the discussion on stackoverflow on "ImageField overwrite image file"
(http://stackoverflow.com/questions/9522759/imagefield-overwrite-image-file)
"""

import os.path
from django.core.files.storage import FileSystemStorage

class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length=None):
        return name

    def _save(self, name, content):
        full_path = self.path(name)
        # make sure an existing file is replaced by removing the
        # original file first
        if os.path.exists(full_path):
            os.remove(full_path)
        return super(OverwriteStorage, self)._save(name, content)

