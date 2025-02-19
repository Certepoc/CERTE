from django.db import models

class EmployeeCertifications(models.Model):
    employee_name = models.CharField(max_length=100)
    employee_ps_no = models.IntegerField()
    provider = models.CharField(max_length=50,null=True)
    certification_name=models.CharField(max_length=50)
    exam_date = models.DateField(null=True)
    update_date = models.DateTimeField(auto_now=True,null=True)
    certification_status = models.CharField(max_length=50)
    uploaded_certificate=models.FileField(null=True)
    voucher_code = models.CharField(max_length=100,null=True)


    class Meta:
        db_table = 'employeecertifications'