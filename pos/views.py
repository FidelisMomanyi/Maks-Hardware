from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, StockIn, Sale

# Create your views here.

ADMIN_PIN = "1234"

# ---------- Product List ----------
def product_list(request):
    products = Product.objects.all()
    return render(request, 'pos/product_list.html', {'products': products})

# ---------- Add Stock ----------
def stock_in(request):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=request.POST.get('product'))
        quantity = int(request.POST.get('quantity'))
        buying_price = float(request.POST.get('buying_price'))
        selling_price = float(request.POST.get('selling_price'))

        StockIn.objects.create(
            product=product,
            quantity=quantity,
            buying_price=buying_price,
            selling_price=selling_price
        )

        product.stock_quantity += quantity
        product.buying_price = buying_price
        product.selling_price = selling_price
        product.save()

        messages.success(request, "Stock added successfully")
        return redirect('stock_in')

    products = Product.objects.all()
    return render(request, 'pos/stock_in.html', {'products': products})

# ---------- Record Sale ----------
def sale_create(request):
    products = Product.objects.all()
    if request.method == 'POST':
        product = get_object_or_404(Product, id=request.POST['product'])
        qty = int(request.POST['quantity'])
        sp = float(request.POST.get('selling_price', product.selling_price))
        payment = request.POST['payment_mode']
        pin = request.POST.get('pin')

        # Rule 1: Cannot sell more than stock
        if qty > product.stock_quantity:
            messages.error(request, "Insufficient stock. Sale not allowed.")
            return redirect('sale_create')

        # Rule 2: Selling below buying price requires PIN
        if sp < product.buying_price and pin != ADMIN_PIN:
            messages.error(request, "Admin PIN required to sell below buying price.")
            return redirect('sale_create')

        # Create sale
        Sale.objects.create(
            product=product,
            quantity=qty,
            selling_price=sp,
            total_price=sp * qty,
            profit=(sp - product.buying_price) * qty,
            payment_mode=payment,
            status='COMPLETED',
            approved_by_pin=(pin == ADMIN_PIN)
        )

        # Deduct stock
        product.stock_quantity -= qty
        product.save()

        messages.success(request, "Sale completed successfully")
        return redirect('sales_list')

    return render(request, 'pos/sale_form.html', {'products': products})

# ---------- Sales List ----------
def sales_list(request):
    sales = Sale.objects.select_related('product').order_by('-date')
    return render(request, 'pos/sales_list.html', {'sales': sales})
