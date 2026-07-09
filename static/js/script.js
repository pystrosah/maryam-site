document.addEventListener('DOMContentLoaded', function() {
    // تایید حذف
    document.querySelectorAll('.delete-confirm').forEach(function(element) {
        element.addEventListener('click', function(e) {
            if (!confirm('آیا از حذف این مورد اطمینان دارید؟')) {
                e.preventDefault();
            }
        });
    });
    
    // بستن خودکار پیام‌ها
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});