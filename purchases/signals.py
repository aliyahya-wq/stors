from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseOrder, PurchaseItem
from inventory.models import InventoryItem, StockMovement

@receiver(post_save, sender=PurchaseOrder)
def process_purchase_order(sender, instance, created, **kwargs):
    if instance.status == 'completed':
        for item in instance.items.all():
            # Increase inventory
            inventory_obj, inv_created = InventoryItem.objects.get_or_create(
                warehouse=instance.warehouse,
                product=item.product,
                defaults={'quantity': 0}
            )
            old_quantity = inventory_obj.quantity
            inventory_obj.quantity += item.quantity
            inventory_obj.save()

            # Record stock movement
            StockMovement.objects.create(
                product=item.product,
                warehouse=instance.warehouse,
                movement_type='purchase',
                quantity=item.quantity,
                quantity_before=old_quantity,
                quantity_after=inventory_obj.quantity,
                reference_number=f"PO-{instance.id}",
                notes=f"مشتريات من المورد {instance.supplier.name}",
                created_by=instance.created_by
            )
