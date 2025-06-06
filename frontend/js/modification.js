document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('modification-form');
    const withdrawBtn = document.getElementById('withdraw-btn');
    const resultMsg = document.getElementById('result-message');

    // 토큰 가져오기 (예시: localStorage)
    function getToken() {
        return localStorage.getItem('token');
    }

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();
        const notify = document.getElementById('notify_by_email').checked;

        // 변경할 값만 보냄
        let data = {};
        if (email) data.email = email;
        if (password) data.password = password;
        data.notify_by_email = notify;

        try {
            const res = await fetch('/auth/update', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + getToken()
                },
                body: JSON.stringify(data)
            });
            const result = await res.json();
            resultMsg.textContent = result.message;
            resultMsg.style.color = res.ok ? 'green' : 'red';
            if (res.ok) form.reset();
        } catch (err) {
            resultMsg.textContent = '오류가 발생했습니다.';
            resultMsg.style.color = 'red';
        }
    });

    withdrawBtn.addEventListener('click', async function () {
        if (!confirm('정말로 회원 탈퇴하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) return;
        try {
            const res = await fetch('/auth/withdraw', {
                method: 'DELETE',
                headers: {
                    'Authorization': 'Bearer ' + getToken()
                }
            });
            const result = await res.json();
            resultMsg.textContent = result.message;
            resultMsg.style.color = res.ok ? 'green' : 'red';
            if (res.ok) {
                // 로그아웃 처리 및 메인으로 이동
                localStorage.removeItem('token');
                setTimeout(() => window.location.href = 'index.html', 1500);
            }
        } catch (err) {
            resultMsg.textContent = '오류가 발생했습니다.';
            resultMsg.style.color = 'red';
        }
    });
});