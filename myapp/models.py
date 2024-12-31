from django.db import models

class EmployeeCertifications(models.Model):
    employee_name = models.CharField(max_length=100)
    employee_ps_no = models.IntegerField()
    # employee_photo=models.ImageField(upload_to='image/')
    employee_designation=models.CharField(max_length=50)
    certification_details=models.CharField(max_length=50)
    update_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'employeecertifications'

class Voucher(models.Model):
    certification_name = models.CharField(max_length=255)
    voucher_code = models.CharField(max_length=100)
    expiration_date = models.DateField()


    class Meta:
        db_table = 'vouchers'