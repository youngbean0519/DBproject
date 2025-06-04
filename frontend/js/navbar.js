import { getCurrentUser, logout } from './auth.js';

document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.createElement('nav');
    navbar.className = 'navbar';
    
    const user = getCurrentUser();
    
    navbar.innerHTML = `
        <div class="nav-brand">
            <a href="/movies.html">KinoLetter</a>
        </div>
        <div class="nav-links">
            ${user ? `
                <a href="/movies.html">영화</a>
                <a href="/recommend.html">추천</a>
                <a href="/watchlist.html">시청목록</a>
                <a href="/likes.html">좋아요</a>
                ${user.is_admin ? `<a href="/admin.html">관리자</a>` : ''}
                <div class="user-menu">
                    <span class="user-name">${user.name}</span>
                    <button class="logout-btn">로그아웃</button>
                </div>
            ` : `
                <a href="/login.html">로그인</a>
                <a href="/register.html">회원가입</a>
            `}
        </div>
    `;

    // 로그아웃 버튼 이벤트 처리
    const logoutBtn = navbar.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await logout();
        });
    }

    // 현재 페이지 링크 활성화
    const currentPath = window.location.pathname;
    navbar.querySelectorAll('a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // 네비게이션 바를 body 시작 부분에 삽입
    document.body.insertBefore(navbar, document.body.firstChild);
});