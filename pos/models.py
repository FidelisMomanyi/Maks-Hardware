from django.db import models

# Create your models here.
# -------------------------
# PRODUCT
# -------------------------
class Product(models.Model):
    name = models.CharField(max_length=255)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.name

# -------------------------
# STOCK IN
# -------------------------
class StockIn(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

# -------------------------
# CUSTOMER
# -------------------------
class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

# -------------------------
# SALE
# -------------------------
class Sale(models.Model):
    STATUS_CHOICES = [
        ('COMPLETED', 'Completed'),
        ('PENDING_STOCK', 'Pending Stock'),
        ('PENDING_PAYMENT', 'Pending Payment'),
    ]
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('MPESA', 'M-Pesa'),
        ('LOOP', 'Loop'),
        ('BANK', 'Bank'),
        ('CREDIT', 'Credit'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='COMPLETED')
    approved_by_pin = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-calc total and profit
        self.total_price = self.selling_price * self.quantity
        self.profit = (self.selling_price - self.product.buying_price) * self.quantity

        # Handle credit payments
        if self.payment_mode == 'CREDIT':
            self.remaining_amount = self.total_price - self.paid_amount
            self.status = 'PENDING_PAYMENT' if self.remaining_amount > 0 else 'COMPLETED'
        else:
            self.remaining_amount = 0
            self.status = 'COMPLETED'

        super().save(*args, **kwargs)

# -------------------------
# PAYMENT (for partial payments / installments)
# -------------------------
class Payment(models.Model):
    PAYMENT_CHOICES = [
        ('CASH', 'Cash'),
        ('MPESA', 'M-Pesa'),
        ('BANK', 'Bank'),
        ('LOOP', 'Loop'),
    ]

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update remaining_amount in Sale
        self.sale.paid_amount += self.amount
        self.sale.remaining_amount = max(self.sale.total_price - self.sale.paid_amount, 0)
        if self.sale.remaining_amount == 0:
            self.sale.status = 'COMPLETED'
        self.sale.save()
