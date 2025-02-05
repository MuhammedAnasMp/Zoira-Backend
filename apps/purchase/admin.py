from django.contrib import admin
from .models import BusinessAsset, Material, PurchasedBatch, MaterialPurchase, HennaType, Customer, HennaSale ,Expense ,HennaAppointment
from django import forms
# Register Material model
@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')  # Show name and unit in the list
    search_fields = ('name',)  # Enable search by material name
# Register PurchasedBatch model
@admin.register(PurchasedBatch)
class PurchasedBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_code', 'purchase_date', 'total_cost')  # Columns to display
    search_fields = ('batch_code',)
    readonly_fields = ('total_cost',)  # Make total_cost read-only since it's calculated dynamically


# Register MaterialPurchase model
@admin.register(MaterialPurchase)
class MaterialPurchaseAdmin(admin.ModelAdmin):
    list_display = ('material', 'purchased_batch', 'quantity_purchased', 'cost')  # Columns to display
    search_fields = ('material__name', 'purchased_batch__batch_code')  # Search by material name and batch code


# Register HennaType model
@admin.register(HennaType)
class HennaTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Columns to display
    search_fields = ('name',)


# Register Customer model
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_info')  # Columns to display
    search_fields = ('name',)


class HennaSaleAdminForm(forms.ModelForm):
    class Meta:
        model = HennaSale
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        sale_price_per_unit = cleaned_data.get('sale_price_per_unit')
        quantity_sold = cleaned_data.get('quantity_sold')

        if sale_price_per_unit is None or quantity_sold is None:
            raise forms.ValidationError("Both sale price per unit and quantity sold must be provided.")
        
        return cleaned_data

@admin.register(HennaSale)
class HennaSaleAdmin(admin.ModelAdmin):
    list_display = (
        'henna_type', 'customer', 'quantity_sold', 'sale_price_per_unit', 
        'actual_calculated_price', 'payment_received', 'remaining_balance', 
        'is_settled', 'total_sale_revenue', 'profit_after_expenditure', 'sale_date'
    )
    readonly_fields = ('actual_calculated_price', 'total_sale_revenue', 'remaining_balance', 'profit_after_expenditure')
    search_fields = ('henna_type__name', 'customer__name')
    # list_filter = ('sale_date', 'is_settled')




@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('sale', 'expense_type', 'value')
    search_fields = ('sale__id', 'expense_type')
    list_filter = ('expense_type',)
    
    
    
    
    
    
    
    
    
    
    


@admin.register(BusinessAsset)
class BusinessAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'purchased_batch', 'purchase_date')
    search_fields = ('name', 'purchased_batch__id')
    list_filter = ('purchase_date', 'purchased_batch')





@admin.register(HennaAppointment)
class HennaAppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'place', 'appointment_date', 'price_charged', 'expenses', 'profit')
    search_fields = ('customer_name', 'contact_info', 'place')
    list_filter = ('appointment_date',)
    readonly_fields = ('profit',)