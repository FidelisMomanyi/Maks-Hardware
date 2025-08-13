from django.db import models, transaction
from django.utils import timezone


class Product(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)

    def __str__(self):
        return self.name


class StockEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_entries")
    quantity_received = models.IntegerField()
    date_received = models.DateField(default=timezone.now)
    supplier = models.CharField(max_length=100, blank=True, null=True)
    buying_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_buying_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Calculate total buying price
        self.total_buying_price = self.buying_price_per_unit * self.quantity_received

        # Update product stock
        with transaction.atomic():
            product = self.product
            product.current_stock += self.quantity_received
            product.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity_received} units on {self.date_received}"


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales")
    quantity_sold = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_sold = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.total_price = self.product.selling_price * self.quantity_sold

        # Deduct stock on sale
        with transaction.atomic():
            product = self.product
            if product.current_stock >= self.quantity_sold:
                product.current_stock -= self.quantity_sold
                product.save()
            else:
                raise ValueError("Not enough stock to complete sale.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale of {self.product.name} - {self.quantity_sold} units"
