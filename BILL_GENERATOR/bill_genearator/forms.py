from django import forms
from .models import Invoice
from datetime import date

from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem



class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'invoice_no', 'terms_conditions',
            # From Company
            'name_of_supplier', 'state', 'gstn', 'pan', 'address',
            
            # To Company
            'name_of_buyer', 'buyer_state', 'buyer_gstn', 'buyer_pan', 'buyer_address',
            
            # Invoice Details
            'invoice_date', 'delivery_note_no', 'buyer_order_no', 'despatch_document_no', 'despatch_mode',
            'date_of_despatch', 'vehicle_no', 'shipping_address',
            
            # Invoice Items
            'item_name', 'hsn_code', 'gst_percentage', 'uom', 'quantity', 'rate'
        ]
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'date_of_despatch': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):  # ✅ correct method name is __init__, not _init_
        super().__init__(*args, **kwargs)
        self.fields['invoice_date'].initial = date.today()
        self.fields['date_of_despatch'].initial = date.today()



class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['item_name', 'hsn_code', 'gst_percentage', 'uom', 'quantity', 'rate', 'taxable_amount', 'cgst', 'sgst', 'ugst', 'total']

# Formset for handling multiple invoice items
InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItem, form=InvoiceItemForm, extra=0)




