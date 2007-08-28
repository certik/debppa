from django.db import models

class SourcePackage(models.Model):
    name = models.CharField(maxlength=40)
    upload_date = models.DateTimeField('date uploaded',auto_now_add=True)
    file_dsc = models.FilePathField()
    file_tar_gz = models.FilePathField()
    version = models.CharField(maxlength=20)
    status = models.CharField(maxlength=20)
    build_log = models.TextField()

    def __str__(self):
        return self.name

    class Admin:
        pass

class BinaryPackage(models.Model):
    source_package = models.ForeignKey(SourcePackage)
    name = models.CharField(maxlength=40)
    arch = models.CharField(maxlength=20)
    file_deb = models.FilePathField()
    short_description = models.CharField(maxlength=100)
    long_description = models.CharField(maxlength=1000)

    def __str__(self):
        return self.name

    class Admin:
        pass
