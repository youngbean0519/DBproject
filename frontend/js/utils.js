// 배포용
//const API_BASE_URL = 'http://129.154.48.98';
// 개발용
const API_BASE_URL = 'http://localhost:5000';

async function fetchAPI(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'API 요청 실패');
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

export const api = {
    get: (endpoint) => fetchAPI(endpoint),
    post: (endpoint, data) => fetchAPI(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    put: (endpoint, data) => fetchAPI(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    delete: (endpoint, data) => fetchAPI(endpoint, {
        method: 'DELETE',
        body: data ? JSON.stringify(data) : undefined
    })
};

export function showError(element, message) {
    element.textContent = message;
    element.style.display = 'block';
    setTimeout(() => {
        element.style.display = 'none';
    }, 3000);
}

export function redirectTo(url) {
    window.location.href = url;
}
