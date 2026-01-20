from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, StockIn, Sale, Customer, Payment
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta

# Create your views here.

ADMIN_PIN = "1234"

# ---------- Product List ----------
def product_list(request):
    products = Product.objects.all()
    return render(request, 'pos/product_list.html', {'products': products})

# ---------- Add Product ----------
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

# ---------- Stock In ----------
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

# ---------- Create Sale ----------
def sale_create(request):
    products = Product.objects.all()
    customers = Customer.objects.all()

    if request.method == "POST":
        product = get_object_or_404(Product, id=request.POST['product'])
        customer_id = request.POST.get('customer')
        customer = get_object_or_404(Customer, id=customer_id) if customer_id else None
        qty = int(request.POST['quantity'])
        sp = float(request.POST.get('selling_price', product.selling_price))
        payment_mode = request.POST['payment_mode']
        paid = float(request.POST.get('paid_amount', 0))
        pin = request.POST.get('pin')

        # ---------- Stock Check ----------
        if qty > product.stock_quantity and pin != ADMIN_PIN:
            messages.error(request, "Insufficient stock. Admin PIN required to proceed.")
            return redirect('sale_create')

        # ---------- Selling Below Buying Price Check ----------
        if sp < product.buying_price and pin != ADMIN_PIN:
            messages.error(request, "Selling below buying price requires Admin PIN.")
            return redirect('sale_create')

        # ---------- Calculate Totals ----------
        total_price = sp * qty
        remaining = max(total_price - paid, 0)
        profit = (sp - product.buying_price) * qty

        # ---------- Determine Status ----------
        status = 'COMPLETED' if remaining == 0 else 'PENDING_PAYMENT'

        # ---------- Record Sale ----------
        sale = Sale.objects.create(
            product=product,
            customer=customer,
            quantity=qty,
            selling_price=sp,
            total_price=total_price,
            paid_amount=paid,
            remaining_amount=remaining,
            profit=profit,
            payment_mode=payment_mode,
            status=status,
            approved_by_pin=True if pin == ADMIN_PIN else False
        )

        # ---------- Deduct Stock ----------
        if qty <= product.stock_quantity:
            product.stock_quantity -= qty
            product.save()

        # ---------- Record Payment ----------
        if paid > 0:
            Payment.objects.create(
                sale=sale,
                amount_paid=paid,
                payment_mode=payment_mode
            )

        messages.success(request, f"Sale recorded! Status: {status}. Remaining: {remaining}")
        return redirect('sales_list')

    return render(request, 'pos/sale_form.html', {
        'products': products,
        'customers': customers
    })

# ---------- Sales List ----------
def sales_list(request):
    sales = Sale.objects.select_related('product', 'customer').order_by('-date')
    return render(request, 'pos/sales_list.html', {'sales': sales})

# ---------- Analytics ----------
def analytics(request):
    today = timezone.now().date()

    # Sales & profits
    daily = Sale.objects.filter(date__date=today).aggregate(
        total_sales=Sum('total_price'), total_profit=Sum('profit')
    )
    weekly = Sale.objects.filter(date__gte=today - timedelta(days=7)).aggregate(
        total_sales=Sum('total_price'), total_profit=Sum('profit')
    )
    monthly = Sale.objects.filter(date__month=today.month, date__year=today.year).aggregate(
        total_sales=Sum('total_price'), total_profit=Sum('profit')
    )
    yearly = Sale.objects.filter(date__year=today.year).aggregate(
        total_sales=Sum('total_price'), total_profit=Sum('profit')
    )

    # Low stock products
    low_stock = Product.objects.filter(stock_quantity__lte=F('reorder_level')).count()

    context = {
        'daily': daily,
        'weekly': weekly,
        'monthly': monthly,
        'yearly': yearly,
        'low_stock': low_stock,
    }

    return render(request, 'pos/analytics.html', context)
