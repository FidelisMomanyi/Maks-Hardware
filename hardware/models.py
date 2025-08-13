from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50) #e.g. 'kg', 'piece', 'litre'
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.IntegerField(default=0) # will update automatically later
    reorder_level = models.IntegerField(default=0) # when to trigger low stock alert

    def __str__(self):
        return self.name

    from django.db import models
