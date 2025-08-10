document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.close-alert').forEach(button => {
        button.addEventListener('click', (e) => {
            const alert = e.target.closest('.alert-resena'); 
            if (alert) {
                alert.remove();
            }
        });
    });
});