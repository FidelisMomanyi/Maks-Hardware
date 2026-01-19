from django.db import models

# Create your models here.
# pos/models.py

class Product(models.Model):
    name = models.CharField(max_length=255)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.name

class StockIn(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class Sale(models.Model):
    STATUS_CHOICES = [
        ('COMPLETED', 'Completed'),
        ('PENDING_STOCK', 'Pending Stock'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='COMPLETED')
    approved_by_pin = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
