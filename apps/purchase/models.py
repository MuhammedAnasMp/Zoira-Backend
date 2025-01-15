from django.db import models
from django.db.models import Sum
# Material: Tracks individual materials
class Material(models.Model):
    # Define choices for units, including gram and ml
    UNIT_CHOICES = [
     
        ('gram', 'Gram'),
     
        ('ml', 'Milliliter'),
        ('count', 'Count'),
    ]
    
    name = models.CharField(max_length=100)
    unit = models.CharField(
        max_length=10, 
        choices=UNIT_CHOICES,  # Use the choices here
        default='kg',  # Optional: Set a default unit if necessary
    )
    
    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"
# PurchasedBatch: Tracks a batch of materials purchased at once
class PurchasedBatch(models.Model):
    batch_code = models.CharField(max_length=50, unique=True)  # Unique batch code, e.g., "Batch-001"
    purchase_date = models.DateField(auto_now_add=True)  # Date of purchase batch

    def __str__(self):
        return f"Batch {self.batch_code} purchased on {self.purchase_date}"

    @property
    def total_cost(self):
        # Calculate the total cost of the batch by summing the cost of all related material purchases
        return sum(material_purchase.cost for material_purchase in self.materialpurchases.all())


# MaterialPurchase: Tracks each material in a purchased batch
class MaterialPurchase(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)  # The material purchased
    purchased_batch = models.ForeignKey(PurchasedBatch, related_name='materialpurchases', on_delete=models.CASCADE)  # Link to batch
    quantity_purchased = models.DecimalField(max_digits=10, decimal_places=2)  # Quantity purchased
    cost = models.DecimalField(max_digits=10, decimal_places=2)  # Total cost of the material in the batch

    @property
    def cost_per_unit(self):
        return self.cost / self.quantity_purchased

    def __str__(self):
        return f"{self.material.name} in Batch {self.purchased_batch.batch_code}"


# HennaType: Tracks types of henna products
class HennaType(models.Model):
    name = models.CharField(max_length=100)  # Name of the henna type, e.g., "Natural Henna"
    
    def __str__(self):
        return self.name


# Customer: Tracks customer information
class Customer(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=255, blank=True, null=True)  # Optional contact info

    def __str__(self):
        return self.name




# HennaSale: Tracks sales of henna products

class HennaSale(models.Model):
    henna_type = models.ForeignKey(HennaType, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    sale_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateField(auto_now_add=True)

    purchased_batch = models.ForeignKey(
        PurchasedBatch,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="henna_sales",
    )

    payment_received = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Amount received from customer for this sale",
    )
    is_settled = models.BooleanField(
        default=False,
        help_text="Mark as True if the sale is settled (even with losses)",
    )
    total_sale_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=0.00,
        help_text="The total revenue for this sale after adjustments.",
    )

    @property
    def actual_calculated_price(self):
        """The actual calculated price (quantity * price per unit) without adjustments."""
        if self.quantity_sold and self.sale_price_per_unit:
            return self.quantity_sold * self.sale_price_per_unit
        return 0.00

    @property
    def remaining_balance(self):
        # Calculate the remaining balance
        return self.total_sale_revenue - self.payment_received

    @property
    def total_expenditure(self):
        # Sum all related expenses
        return self.expenses.aggregate(total=models.Sum('value'))['total'] or 0

    @property
    def profit_after_expenditure(self):
        # Calculate profit after deducting expenses
        return self.total_sale_revenue - self.total_expenditure

    def save(self, *args, **kwargs):
        # Automatically calculate total revenue based on quantity and unit price
        if self.sale_price_per_unit and self.quantity_sold:
            self.total_sale_revenue = self.sale_price_per_unit * self.quantity_sold

        # If manually marked as settled, consider the remaining balance as lost
        if self.is_settled and self.remaining_balance > 0:
            self.total_sale_revenue = self.payment_received

        # Automatically set 'is_settled' to True if payment_received >= total_sale_revenue
        if self.payment_received >= self.total_sale_revenue:
            self.is_settled = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity_sold} of {self.henna_type.name} sold to {self.customer.name} on {self.sale_date}"



class Expense(models.Model):
    EXPENSE_TYPE_CHOICES = [
        ('commission', 'Commission'),
        ('travel', 'Travel Expense'),
        ('misc', 'Miscellaneous'),
    ]
    
    sale = models.ForeignKey(HennaSale, on_delete=models.CASCADE, related_name='expenses')
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.get_expense_type_display()} - {self.value} for Sale ID {self.sale.id}"



class BusinessAsset(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the asset, e.g., Mixer, Gloves, Spoon")
    description = models.TextField(blank=True, null=True, help_text="Additional details about the asset.")
    purchase_date = models.DateField(auto_now_add=True, help_text="Date of purchase.")
    cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total cost of the asset.")
    purchased_batch = models.ForeignKey(
        PurchasedBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assets",
        help_text="The henna batch associated with this asset purchase."
    )

    def __str__(self):
        batch_info = f" (Batch: {self.purchased_batch.id})" if self.purchased_batch else ""
        return f"{self.name} - ${self.cost}{batch_info}"
    
    
    
    

class HennaAppointment(models.Model):
    customer_name = models.CharField(max_length=255, help_text="Name of the customer.")
    contact_info = models.CharField(max_length=255, help_text="Contact details of the customer (phone or email).")
    place = models.CharField(max_length=255, help_text="Location where the henna service will be provided.")
    appointment_date = models.DateTimeField(help_text="Date and time when the service is required.")
    price_charged = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price charged for the service.")
    expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Total expenses incurred for this appointment (e.g., travel or materials).")
    profit = models.DecimalField(max_digits=10, decimal_places=2, editable=False, help_text="Profit after deducting expenses from the price charged.")

    def save(self, *args, **kwargs):
        # Automatically calculate profit
        self.profit = self.price_charged - self.expenses
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Appointment with {self.customer_name} at {self.place} on {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"