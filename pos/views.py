from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, StockIn, Sale
from django.db.models import Sum, F

# Create your views here.

ADMIN_PIN = "1234"

# ---------- Product List ----------
def product_list(request):
    products = Product.objects.all()

    # Calculate real stock
    product_data = []
    for p in products:
        total_stock_in = StockIn.objects.filter(product=p).aggregate(
            total_in=Sum('quantity')
        )['total_in'] or 0

        total_sold = Sale.objects.filter(
            product=p, status='COMPLETED'
        ).aggregate(
            total_out=Sum('quantity')
        )['total_out'] or 0

        current_stock = total_stock_in - total_sold

        product_data.append({
            'id': p.id,
            'name': p.name,
            'buying_price': p.buying_price,
            'selling_price': p.selling_price,
            'stock': current_stock,
            'reorder_level': p.reorder_level,
        })

    return render(request, 'pos/product_list.html', {'products': product_data})

def product_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        buying_price = float(request.POST.get('buying_price'))
        selling_price = float(request.POST.get('selling_price'))
        reorder_level = int(request.POST.get('reorder_level', 5))

        Product.objects.create(
            name=name,
            buying_price=buying_price,
            selling_price=selling_price,
            stock_quantity=0,
            reorder_level=reorder_level
        )

        messages.success(request, "Product added successfully")
        return redirect('product_list')

    return render(request, 'pos/product_create.html')

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

    if request.method == "POST":
        product = get_object_or_404(Product, id=request.POST['product'])
        qty = int(request.POST['quantity'])
        sp = float(request.POST.get('selling_price', product.selling_price))
        payment = request.POST['payment_mode']
        paid = float(request.POST.get('paid_amount', 0))
        pin = request.POST.get('pin')

        # Stock check
        if qty > product.stock_quantity and pin != ADMIN_PIN:
            messages.error(request, "Insufficient stock. Admin PIN required.")
            return redirect('sale_create')

        # Selling below buying price check
        if sp < product.buying_price and pin != ADMIN_PIN:
            messages.error(request, "Selling below buying price requires Admin PIN.")
            return redirect('sale_create')

        # Calculate totals
        total_price = sp * qty
        remaining = max(total_price - paid, 0)
        profit = (sp - product.buying_price) * qty

        # Determine status
        if remaining > 0:
            status = 'PENDING_PAYMENT'
        else:
            status = 'COMPLETED'

        # Save Sale
        sale = Sale.objects.create(
            product=product,
            quantity=qty,
            selling_price=sp,
            total_price=total_price,
            paid_amount=paid,
            remaining_amount=remaining,
            profit=profit,
            payment_mode=payment,
            status=status,
            approved_by_pin=True if pin == ADMIN_PIN else False
        )

        # Deduct stock only for completed or partial stock sale
        if qty <= product.stock_quantity:
            product.stock_quantity -= qty
            product.save()

        messages.success(request, f"Sale recorded! Status: {status}")
        return redirect('sales_list')

    return render(request, 'pos/sale_form.html', {'products': products})

# ---------- Sales List ----------
def sales_list(request):
    sales = Sale.objects.select_related('product').order_by('-date')
    return render(request, 'pos/sales_list.html', {'sales': sales})

def analytics(request):
    return render(request, 'pos/analytics.html')

