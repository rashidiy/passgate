from typing import Iterable

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import PROTECT


class UserType(models.Model):
    name = models.CharField("Ism", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Guruh"
        verbose_name_plural = "Guruhlar"


class Employee(models.Model):
    def validate_image_size(value):
        max_size_kb = 200
        if value.size > max_size_kb * 1024:
            raise ValidationError(f"Rasm hajmi {max_size_kb} KB dan oshmasligi kerak.")

    rfid = models.CharField("Karta raqami", max_length=20)
    name = models.CharField("Xodimning ismi", max_length=100)
    face_image = models.ImageField("FaceId uchun rasm",
                                   upload_to='faces/',
                                   max_length=200,
                                   help_text="No larger than 200 KB. JPG, JPEG, PNG allowed.",
                                   validators=[validate_image_size],
                                   default='app1/static/img.png'
                                   )

    user_type = models.ForeignKey(to=UserType, on_delete=PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Xodim "
        verbose_name_plural = "Xodimlar"
    # DEPARTMENT_CHOICES = [
    #     ("Company", "Company"),
    #     ("Admin", "Admin. Dept."),
    #     ("Sales", "Sales Dept."),
    #     ("Financial", "Financial Dept."),
    #     ("Production", "Production Dept."),
    # ]
    #
    # USER_TYPE_CHOICES = [
    #     ("employee", "Normal User"),
    #     ("guest", "Visitor"),
    #
    # ]
    #
    # GENDER_CHOICES = [
    #     ("Male", "Male"),
    #     ("Female", "Female"),
    #     ("Other", "Other"),
    # ]
    #
    #
    # AUTH_TYPE_CHOICES = [
    #     ('same_as_device', 'Same as Device'),
    #     ('custom', 'Custom'),
    # ]
    # department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    # floor_num = models.IntegerField()
    # room_num = models.IntegerField()
    # gender = models.CharField(max_length=7, choices=GENDER_CHOICES)
    # lifetime_user = models.BooleanField()
    # begin_time = models.DateTimeField(auto_now_add=True)
    # end_time = models.DateTimeField(null=True, blank=True)
    # local_ui_right = models.BooleanField()
    # authentication_type = models.CharField(
    #     max_length=15,
    #     choices=AUTH_TYPE_CHOICES,
    #     default='same_as_device'
    # )


class Order(models.Model):
    FOOD_SIZE_CHOICES = [
        ("0.5", "Kichik"),
        ("1.0", "O'rta"),
        ("1.5", "Katta"),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL,
                                 null=True)  # TODO on_delete'ning logikasini o'ylash
    name = models.CharField("Ism", max_length=225)
    food_size = models.CharField("Ovqat hajmi", max_length=3, choices=FOOD_SIZE_CHOICES)
    time = models.DateTimeField("Vaqt", auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.employee.name
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
