from django.db import models

# Create your models here.

# ---------- Global Choices ----------
PAYMENT_CHOICES = [
    ('CASH', 'Cash'),
    ('MPESA', 'M-Pesa'),
    ('BANK', 'Bank Transfer'),
    ('LOOP', 'Loop'),
    ('CREDIT', 'Credit'),
]

STATUS_CHOICES = [
    ('COMPLETED', 'Completed'),
    ('PENDING_PAYMENT', 'Pending Payment'),
]

# ---------- Product ----------
class Product(models.Model):
    name = models.CharField(max_length=255)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.name

# ---------- Stock In ----------
class StockIn(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

# ---------- Customer ----------
class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

# ---------- Sale ----------
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='COMPLETED')
    approved_by_pin = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

# ---------- Payment ----------
class Payment(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='CASH')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sale.product.name} - {self.amount_paid}"
