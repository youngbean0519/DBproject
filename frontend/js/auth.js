import { api, showError, redirectTo } from './utils.js';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const errorDiv = document.querySelector('.error');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = {
                email: formData.get('email'),
                password: formData.get('password'),
                notify_by_email: formData.get('notify_by_email') === 'on'
            };

            // 회원가입 페이지인 경우 추가 필드 처리
            if (location.pathname.endsWith('register.html')) {
                const passwordConfirm = formData.get('password_confirm');
                if (data.password !== passwordConfirm) {
                    showError(errorDiv, '비밀번호가 일치하지 않습니다.');
                    return;
                }
                data.name = formData.get('name');
            }

            try {
                const endpoint = location.pathname.endsWith('register.html') ? '/auth/register' : '/auth/login';
                const response = await api.post(endpoint, data);
                
                if (location.pathname.endsWith('register.html')) {
                    // 회원가입 성공 시 로그인 화면으로 이동
                    redirectTo('/login.html');
                } else if (response.token) {
                    localStorage.setItem('token', response.token);
                    localStorage.setItem('user', JSON.stringify(response.user));
                    redirectTo('/movies.html');
                }
            } catch (error) {
                showError(errorDiv, error.message);
            }
        });
    }
});

export async function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        redirectTo('/login.html');
        return false;
    }
    return true;
}

export async function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    redirectTo('/login.html');
}

export function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}