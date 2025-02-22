from django.shortcuts import render
from django.db.models import Sum
from datetime import date
from apps.purchase.models import HennaSale, Expense, MaterialPurchase, HennaAppointment
from django.db.models import F, ExpressionWrapper, FloatField


def dashboard(request):
    # 📊 Total Sales
    today_sales = HennaSale.objects.filter(sale_date=date.today()).aggregate(
        Sum('total_sale_revenue'))['total_sale_revenue__sum'] or 0
    month_sales = HennaSale.objects.filter(sale_date__month=date.today().month).aggregate(
        Sum('total_sale_revenue'))['total_sale_revenue__sum'] or 0
    total_sales = HennaSale.objects.aggregate(Sum('total_sale_revenue'))[
        'total_sale_revenue__sum'] or 0

    # 📉 Expenses Summary
    expenses_summary = Expense.objects.values('expense_type').annotate(total=Sum('value'))

    # 📦 Material Overview
    stock_overview = MaterialPurchase.objects.values(
        'material__name', 'material__unit'  # Include material__unit here
    ).annotate(total_purchased=Sum('quantity_purchased'))

    # 💰 Outstanding Payments
    outstanding_payments = HennaSale.objects.filter(is_settled=False).annotate(
        remaining_balance=ExpressionWrapper(
            F('total_sale_revenue') - F('payment_received'),
            output_field=FloatField()
        )
    ).aggregate(Sum('remaining_balance'))['remaining_balance__sum'] or 0

    # 🗓 Upcoming Appointments
    upcoming_appointments = HennaAppointment.objects.filter(
        appointment_date__gte=date.today()).order_by('appointment_date')[:5]

    context = {
        'today_sales': today_sales,
        'month_sales': month_sales,
        'total_sales': total_sales,
        'expenses_summary': expenses_summary,
        'stock_overview': stock_overview,
        'outstanding_payments': outstanding_payments,
        'upcoming_appointments': upcoming_appointments,
    }
    return render(request, 'ui/dashboard.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from apps.purchase.models import Material, PurchasedBatch, MaterialPurchase

# Materials List View
def materials_list(request):
    materials = Material.objects.all()
    batches = PurchasedBatch.objects.all()
    return render(request, 'ui/purchaseandmaterial.html', {'materials': materials, 'batches': batches})

# Add New Material (AJAX)
def add_material(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        unit = request.POST.get('unit')
        if name and unit:
            material = Material.objects.create(name=name, unit=unit)
            return JsonResponse({'id': material.id, 'name': material.name, 'unit': material.get_unit_display()})
    return JsonResponse({'error': 'Invalid Data'}, status=400)

# Add New Purchased Batch (AJAX)
def add_purchased_batch(request):
    if request.method == 'POST':
        batch_id = request.POST.get('batch_id')  # Get selected batch ID (if any)
        batch_code = request.POST.get('batch_code')  # Get new batch code (if entered)
        material_id = request.POST.get('material_id')
        quantity = request.POST.get('quantity')
        cost = request.POST.get('cost')

        if not material_id or not quantity or not cost:
            return JsonResponse({'error': 'Missing fields'}, status=400)

        # Ensure Material ID is valid
        try:
            material = Material.objects.get(id=material_id)
        except Material.DoesNotExist:
            return JsonResponse({'error': 'Invalid Material ID'}, status=400)

        # Handle batch selection/creation
        if batch_id:  # If user selected an existing batch
            try:
                batch = PurchasedBatch.objects.get(id=batch_id)
            except PurchasedBatch.DoesNotExist:
                return JsonResponse({'error': 'Invalid Batch ID'}, status=400)
        elif batch_code:  # If user entered a new batch code
            batch, created = PurchasedBatch.objects.get_or_create(batch_code=batch_code)
        else:
            return JsonResponse({'error': 'Please select or enter a batch'}, status=400)

        # Create Material Purchase entry
        MaterialPurchase.objects.create(
            material=material,
            purchased_batch=batch,
            quantity_purchased=quantity,
            cost=cost
        )

        return JsonResponse({'success': 'Batch added successfully'})

    # Fetch all batches for the form dropdown
    batches = PurchasedBatch.objects.all().values('id', 'batch_code')

    return JsonResponse({'batches': list(batches)})




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from apps.purchase.models import HennaSale, Customer ,HennaType

from .forms import CustomerForm, HennaSaleForm,HennaTypeForm  # Create these forms

def sales_and_customers(request):
    sales = HennaSale.objects.all()
    customers = Customer.objects.all()
    henna_types = HennaType.objects.all()
    customer_form = CustomerForm()
    sale_form = HennaSaleForm()
    henna_form = HennaTypeForm()

    return render(
        request,
        'ui/salesandcustomer.html',
        {
            'sales': sales,
            'customers': customers,
            'henna_types': henna_types,
            'customer_form': customer_form,
            'sale_form': sale_form,
             'henna_form': henna_form,
        },
    )

def create_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer created successfully!")
    return redirect('sales_and_customers')
def create_henna_type(request):
    if request.method == "POST":
        form = HennaTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Henna type added successfully!")
    return redirect('sales_and_customers')


def create_sale(request):
    if request.method == "POST":
        form = HennaSaleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sale recorded successfully!")
    return redirect('sales_and_customers')

def delete_sale(request, sale_id):
    sale = get_object_or_404(HennaSale, id=sale_id)
    sale.delete()
    messages.success(request, "Sale record deleted successfully.")
    return redirect('sales_and_customers')

def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    messages.success(request, "Customer record deleted successfully.")
    return redirect('sales_and_customers')

def delete_henna_type(request, henna_id):
    henna_type = get_object_or_404(HennaType, id=henna_id)
    henna_type.delete()
    messages.success(request, "Henna type deleted successfully!")
    return redirect('sales_and_customers')
