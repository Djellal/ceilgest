document.addEventListener('DOMContentLoaded', function() {
    // Image preview functionality
    const imageInput = document.querySelector('input[name="image"]');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const previewContainer = document.querySelector('.image-preview');
            if (!previewContainer) return;
            
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = `
                        <img src="${e.target.result}" 
                             alt="Preview" 
                             style="max-height: 150px; max-width: 100%; border: 1px solid #ddd; border-radius: 4px; padding: 5px;">
                    `;
                }
                reader.readAsDataURL(file);
            }
        });
    }
});