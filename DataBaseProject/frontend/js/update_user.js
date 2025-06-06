// File: /DataBaseProject/DataBaseProject/frontend/js/update_user.js

document.addEventListener('DOMContentLoaded', function() {
    const updateForm = document.getElementById('updateForm');
    const withdrawButton = document.getElementById('withdrawButton');

    updateForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(updateForm);
        const data = {
            email: formData.get('email'),
            password: formData.get('password'),
            notify_by_email: formData.get('notify_by_email') === 'on'
        };

        fetch('/auth/update', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating user information.');
        });
    });

    withdrawButton.addEventListener('click', function() {
        if (confirm('Are you sure you want to withdraw your account? This action cannot be undone.')) {
            fetch('/auth/withdraw', {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    // Redirect to home or login page
                    window.location.href = '/';
                } else {
                    alert(data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while withdrawing your account.');
            });
        }
    });
});