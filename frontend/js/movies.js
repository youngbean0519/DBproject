import { api, showError, redirectTo } from './utils.js';
import { checkAuth } from './auth.js';

document.addEventListener('DOMContentLoaded', async () => {
    if (!await checkAuth()) return;

    const moviesContainer = document.getElementById('movies-container');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const searchResults = document.getElementById('searchResults');
    const nowShowing = document.getElementById('nowShowing');
    const upcoming = document.getElementById('upcoming');
    const logoutBtn = document.getElementById('logoutBtn');

    // 탭 시스템 구현
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            
            // 탭 버튼 활성화
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // 탭 컨텐츠 활성화
            tabPanes.forEach(pane => pane.classList.remove('active'));
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });

    // 검색 기능
    async function searchMovies() {
        const query = searchInput.value.trim();
        if (!query) return;

        try {
            const movies = await api.get(`/movies/search?q=${encodeURIComponent(query)}`);
            searchResults.innerHTML = '';
            movies.forEach(movie => {
                searchResults.appendChild(createMovieCard(movie, false));
            });
        } catch (error) {
            showError(searchResults, '영화 검색 중 오류가 발생했습니다.');
        }
    }

    // 현재 상영작 (박스오피스 Top 10)
    async function loadNowShowing() {
        try {
            const movies = await api.get('/movies/now_showing');
            nowShowing.innerHTML = '';
            movies.forEach(movie => {
                nowShowing.appendChild(createMovieCard(movie, false));
            });
        } catch (error) {
            showError(nowShowing, '현재 상영작을 불러오는 중 오류가 발생했습니다.');
        }
    }

    // 개봉 예정작
    async function loadUpcoming() {
        try {
            const movies = await api.get('/movies/upcoming');
            upcoming.innerHTML = '';
            movies.forEach(movie => {
                upcoming.appendChild(createMovieCard(movie, true));
            });
        } catch (error) {
            showError(upcoming, '개봉 예정작을 불러오는 중 오류가 발생했습니다.');
        }
    }

    // 영화 카드 생성
    function createMovieCard(movie, isUpcoming) {
        const card = document.createElement('div');
        card.className = 'movie-card';
        
        let cardHTML = '';
        
        // 박스오피스 순위 표시
        if (movie.rank) {
            cardHTML += `<div class="rank">${movie.rank}위</div>`;
        }
        
        cardHTML += `
            <img src="${movie.poster_url}" alt="${movie.title}">
            <div class="movie-info">
                <h3>${movie.title}</h3>
                <p class="movie-detail">감독: ${movie.director}</p>
                <p class="movie-detail">장르: ${movie.genre}</p>
                <p class="movie-detail">개봉일: ${movie.open_date}</p>
                <div class="movie-actions">
                    ${isUpcoming ? 
                        `<button class="btn-watchlist" data-movie-id="${movie.movie_code}" title="찜하기">
                            <i class="fas fa-bookmark"></i>
                        </button>` :
                        `<button class="btn-like" data-movie-id="${movie.movie_code}" title="좋아요">
                            <i class="fas fa-heart"></i>
                        </button>`
                    }
                </div>
            </div>
        `;
        
        card.innerHTML = cardHTML;

        // 버튼 이벤트 리스너
        const actionBtn = card.querySelector('.movie-actions button');
        if (actionBtn) {
            actionBtn.addEventListener('click', async () => {
                const movieId = actionBtn.dataset.movieId;
                if (isUpcoming) {
                    await toggleWatchlist(movieId, actionBtn);
                } else {
                    await toggleLike(movieId, actionBtn);
                }
            });
        }

        return card;
    }

    // 좋아요 토글
    async function toggleLike(movieId, button) {
        try {
            await api.post('/likes', { movie_id: movieId });
            button.classList.toggle('active');
            showToast(button.classList.contains('active') ? '좋아요가 등록되었습니다.' : '좋아요가 취소되었습니다.');
        } catch (error) {
            showToast(error.message);
        }
    }

    // 찜하기 토글
    async function toggleWatchlist(movieId, button) {
        try {
            await api.post('/watchlist', { movie_id: movieId });
            button.classList.toggle('active');
            showToast(button.classList.contains('active') ? '찜 목록에 추가되었습니다.' : '찜 목록에서 제거되었습니다.');
        } catch (error) {
            showToast(error.message);
        }
    }

    // 토스트 메시지
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // 이벤트 리스너
    searchBtn.addEventListener('click', searchMovies);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchMovies();
    });

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        redirectTo('login.html');
    });

    // 초기 데이터 로드
    loadNowShowing();
    loadUpcoming();
}); 