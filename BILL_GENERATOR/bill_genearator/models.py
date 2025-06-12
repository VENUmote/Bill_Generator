"""from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
class Invoice(models.Model):
    # From Company
    name_of_supplier = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    gstn = models.CharField(max_length=15)
    pan = models.CharField(max_length=10)
    address = models.TextField()

    # To Company
    name_of_buyer = models.CharField(max_length=255)
    buyer_state = models.CharField(max_length=255)
    buyer_gstn = models.CharField(max_length=15)
    buyer_pan = models.CharField(max_length=10)
    buyer_address = models.TextField()

    # Invoice Details
    invoice_date = models.DateField()
    delivery_note_no = models.CharField(max_length=255)
    buyer_order_no = models.CharField(max_length=255)
    despatch_document_no = models.CharField(max_length=255)
    despatch_mode = models.CharField(max_length=255)
    date_of_despatch = models.DateField()
    vehicle_no = models.CharField(max_length=255)
    shipping_address = models.TextField()

    # Invoice Items
    item_name = models.CharField(max_length=255)
    hsn_code = models.CharField(max_length=255)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    uom = models.CharField(max_length=255)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    code = models.CharField(max_length=10, blank=True)
    def __str__(self):
        return f"Invoice for {self.name_of_supplier} to {self.name_of_buyer}"""

"""class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="invoice_items")
    item_name = models.CharField(max_length=255)
    hsn_code = models.CharField(max_length=255)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    uom = models.CharField(max_length=255)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    taxable_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ugst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    def __str__(self):
        return f"{self.item_name} for Invoice {self.invoice.code}"
    
@receiver(post_save, sender=Invoice)
def set_employer_code(sender, instance, created, **kwargs):
    if created and not instance.code:
        instance.code = f'IN{instance.id}'
        instance.save()"""
import random
import string
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from decimal import Decimal
from django.core.validators import MinLengthValidator

class Invoice(models.Model):
    invoice_no = models.CharField(max_length=100)

    # From Company
    name_of_supplier = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    gstn = models.CharField(max_length=15, validators=[MinLengthValidator(15)])
    pan = models.CharField(max_length=10, validators=[MinLengthValidator(10)])
    address = models.TextField()

    # To Company
    name_of_buyer = models.CharField(max_length=255)
    buyer_state = models.CharField(max_length=255)
    buyer_gstn = models.CharField(max_length=15, validators=[MinLengthValidator(15)])
    buyer_pan = models.CharField(max_length=10, validators=[MinLengthValidator(10)])
    buyer_address = models.TextField()

    # Invoice Details
    invoice_date = models.DateField()
    delivery_note_no = models.CharField(max_length=255)
    buyer_order_no = models.CharField(max_length=255)
    despatch_document_no = models.CharField(max_length=255)
    despatch_mode = models.CharField(max_length=255)
    date_of_despatch = models.DateField()
    vehicle_no = models.CharField(max_length=255)
    shipping_address = models.TextField()

    # Invoice Items (Kept in the same model as requested)
    item_name = models.CharField(max_length=255)
    hsn_code = models.CharField(max_length=255)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    uom = models.CharField(max_length=255)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    # Unique Alphanumeric 6-character Code
    code = models.CharField(max_length=6, unique=True, blank=True)


    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    terms_conditions = models.TextField(null=True, blank=True)  # New field added

    def __str__(self):
        return f"Invoice {self.code} - {self.name_of_supplier} to {self.name_of_buyer}"



    def update_total_amount(self):
        total = sum(item.total or Decimal("0.00") for item in self.invoice_items.all())
        self.total_amount = total
        self.save()

    

    def __str__(self):
        return self.invoice_no



from django.db import models
from decimal import Decimal
from decimal import Decimal, ROUND_HALF_UP

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="invoice_items")
    item_name = models.CharField(max_length=255)
    hsn_code = models.CharField(max_length=255)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    uom = models.CharField(max_length=255)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    taxable_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ugst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.quantity and self.rate:
            self.taxable_amount = Decimal(self.quantity) * Decimal(self.rate)
        else:
            self.taxable_amount = Decimal(0)

        # GST calculations
        gst_decimal = Decimal(self.gst_percentage) / Decimal(100) if self.gst_percentage else Decimal(0)
        gst_amount = self.taxable_amount * gst_decimal

        # Assuming CGST and SGST are split equally
        self.cgst = (gst_amount / 2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.sgst = (gst_amount / 2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.ugst = Decimal(0).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Total Amount Calculation
        self.total = (self.taxable_amount + self.cgst + self.sgst + self.ugst).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        super().save(*args, **kwargs)



        if self.invoice:
            self.invoice.update_total_amount()




