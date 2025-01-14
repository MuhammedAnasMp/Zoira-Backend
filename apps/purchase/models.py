from django.db import models
from django.db.models import Sum
# Material: Tracks individual materials
class Material(models.Model):
    # Define choices for units
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
        related_name="henna_sales"
    )

    @property
    def total_sale_revenue(self):
        # Ensure that sale_price_per_unit and quantity_sold are not None
        if self.sale_price_per_unit is not None and self.quantity_sold is not None:
            return self.sale_price_per_unit * self.quantity_sold
        return 0  # Return 0 if any of the values are None

    def __str__(self):
        return f"{self.quantity_sold} of {self.henna_type.name} sold to {self.customer.name} on {self.sale_date}"

    @property
    def production_cost(self):
        if self.purchased_batch:
            total_cost = self.purchased_batch.total_cost
            total_units_produced = self.purchased_batch.materialpurchases.aggregate(Sum('quantity_purchased'))['quantity_purchased__sum']
            if total_units_produced:
                return total_cost * (self.quantity_sold / total_units_produced)
        return 0  # If no batch is associated or data is missing
