// This file contains the main functionalities of the frontend application, including navigation and common scripts.

document.addEventListener('DOMContentLoaded', function() {
    // Navigation functionality
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            const targetPage = this.getAttribute('href');
            fetch(targetPage)
                .then(response => response.text())
                .then(html => {
                    document.getElementById('content').innerHTML = html;
                })
                .catch(error => console.error('Error loading page:', error));
            event.preventDefault();
        });
    });
});