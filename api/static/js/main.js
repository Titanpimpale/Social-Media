// Main JavaScript file for SocialConnect

// Handle dropdown menus
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const parent = this.parentElement;
            
            // Close all other open dropdowns
            document.querySelectorAll('.nav-item.dropdown').forEach(item => {
                if (item !== parent) {
                    item.classList.remove('show');
                }
            });
            
            // Toggle current dropdown
            parent.classList.toggle('show');
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.nav-item.dropdown').forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    });
    
    // File input preview for profile picture
    const fileInput = document.getElementById('profile_picture');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.querySelector('.profile-picture-preview').src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Like/unlike post functionality
    const likeButtons = document.querySelectorAll('.post-action');
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!button.closest('form')) {
                e.preventDefault();
                button.closest('form').submit();
            }
        });
    });
});

// Handle logout form submission
document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    }
});

