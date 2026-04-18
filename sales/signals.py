from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SalesInvoice, SalesItem
from inventory.models import InventoryItem, StockMovement

@receiver(post_save, sender=SalesInvoice)
def process_sales_invoice(sender, instance, created, **kwargs):
    if instance.status == 'paid' and created:
        for item in instance.items.all():
            # Decrease inventory
            inventory_obj, inv_created = InventoryItem.objects.get_or_create(
                warehouse=instance.warehouse,
                product=item.product,
                defaults={'quantity': 0}
            )
            old_quantity = inventory_obj.quantity
            inventory_obj.quantity -= item.quantity
            inventory_obj.save()

            # Record stock movement
            StockMovement.objects.create(
                product=item.product,
                warehouse=instance.warehouse,
                movement_type='sale',
                quantity=-item.quantity,  # Negative quantity to reflect out-going stock
                quantity_before=old_quantity,
                quantity_after=inventory_obj.quantity,
                reference_number=f"INV-{instance.id}",
                notes=f"مبيعات للعميل {instance.customer.name if instance.customer else 'عميل نقدي'}",
                created_by=instance.created_by
            )
