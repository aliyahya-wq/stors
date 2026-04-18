// دوال JavaScript لإدارة المنتجات
document.addEventListener('DOMContentLoaded', function () {
    // البحث في الوقت الحقيقي
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase();
            const productRows = document.querySelectorAll('.product-row');

            productRows.forEach(row => {
                const productName = row.querySelector('.product-name').textContent.toLowerCase();
                const productSku = row.querySelector('.product-sku').textContent.toLowerCase();

                if (productName.includes(searchTerm) || productSku.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // توليد الباركود
    const generateBarcodeBtn = document.getElementById('generate-barcode');
    if (generateBarcodeBtn) {
        generateBarcodeBtn.addEventListener('click', function () {
            const sku = document.getElementById('id_sku').value;
            if (sku) {
                // في الواقع، يمكن استخدام مكتبة مثل JsBarcode
                document.getElementById('barcode-preview').innerHTML =
                    `<div class="text-center">
                        <svg id="barcode"></svg>
                        <p class="mt-2">${sku}</p>
                     </div>`;
            }
        });
    }

    // حساب هامش الربح
    const purchasePriceInput = document.getElementById('id_purchase_price');
    const sellingPriceInput = document.getElementById('id_selling_price');
    const profitMarginElement = document.getElementById('profit-margin');

    if (purchasePriceInput && sellingPriceInput && profitMarginElement) {
        function calculateProfitMargin() {
            const purchasePrice = parseFloat(purchasePriceInput.value) || 0;
            const sellingPrice = parseFloat(sellingPriceInput.value) || 0;

            if (purchasePrice > 0 && sellingPrice > 0) {
                const profit = sellingPrice - purchasePrice;
                const margin = ((profit / purchasePrice) * 100).toFixed(2);
                profitMarginElement.textContent = `${margin}%`;

                // تلوين النتيجة
                if (margin > 50) {
                    profitMarginElement.className = 'text-success fw-bold';
                } else if (margin > 20) {
                    profitMarginElement.className = 'text-warning fw-bold';
                } else {
                    profitMarginElement.className = 'text-danger fw-bold';
                }
            } else {
                profitMarginElement.textContent = '0%';
                profitMarginElement.className = 'text-muted';
            }
        }

        purchasePriceInput.addEventListener('input', calculateProfitMargin);
        sellingPriceInput.addEventListener('input', calculateProfitMargin);
    }
});

// دالة لتحميل الصور مع معاينة
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    const file = input.files[0];
    const reader = new FileReader();

    reader.onloadend = function () {
        preview.innerHTML = `<img src="${reader.result}" class="img-thumbnail" style="max-height: 200px;">`;
    }

    if (file) {
        reader.readAsDataURL(file);
    } else {
        preview.innerHTML = '<div class="text-muted">لم يتم اختيار صورة</div>';
    }
}

// دالة للتحقق من صحة البيانات قبل الإرسال
function validateProductForm() {
    const purchasePrice = parseFloat(document.getElementById('id_purchase_price').value);
    const sellingPrice = parseFloat(document.getElementById('id_selling_price').value);

    if (sellingPrice <= purchasePrice) {
        alert('سعر البيع يجب أن يكون أكبر من سعر الشراء');
        return false;
    }

    return true;
}