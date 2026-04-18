// دوال JavaScript لإدارة المخزون
document.addEventListener('DOMContentLoaded', function () {
    // تحديث المخزون تلقائياً عند التغيير
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function () {
            const productId = this.dataset.productId;
            const warehouseId = this.dataset.warehouseId;
            const newQuantity = this.value;

            // إرسال طلب AJAX لتحديث المخزون
            updateInventory(productId, warehouseId, newQuantity);
        });
    });

    // فلترة حركات المخزون
    const filterForm = document.getElementById('movement-filters');
    if (filterForm) {
        filterForm.addEventListener('change', function () {
            this.submit();
        });
    }

    // مخطط المخزون
    const inventoryChart = document.getElementById('inventory-chart');
    if (inventoryChart) {
        renderInventoryChart();
    }
});

function updateInventory(productId, warehouseId, quantity) {
    fetch('/inventory/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            warehouse_id: warehouseId,
            quantity: quantity
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('تم تحديث المخزون بنجاح', 'success');
            } else {
                showNotification('حدث خطأ في تحديث المخزون', 'error');
            }
        });
}

function renderInventoryChart() {
    // استخدام Chart.js لعرض مخططات المخزون
    const ctx = document.getElementById('inventory-chart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['المنتجات منخفضة المخزون', 'المنتجات عالية المخزون', 'المنتجات طبيعية'],
            datasets: [{
                label: 'توزيع المخزون',
                data: [12, 19, 3],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(75, 192, 192, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.querySelector('.main-content').prepend(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}