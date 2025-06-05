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

    async function loadMovies(query = '') {
        try {
            const endpoint = query ? `/movies/search?q=${encodeURIComponent(query)}` : '/movies';
            const movies = await api.get(endpoint);
            displayMovies(movies);
        } catch (error) {
            showError(document.querySelector('.error'), error.message);
        }
    }

    function displayMovies(movies) {
        moviesContainer.innerHTML = movies.map(movie => `
            <div class="movie-card">
                <img src="${movie.poster_url}" alt="${movie.title}">
                <h3>${movie.title}</h3>
                <p>${movie.release_year}</p>
                <div class="movie-actions">
                    <button onclick="addToWatchlist(${movie.id})">시청목록 추가</button>
                    <button onclick="toggleLike(${movie.id})">좋아요</button>
                </div>
            </div>
        `).join('');
    }

    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            const query = searchInput.value.trim();
            loadMovies(query);
        });
    }

    // 초기 영화 목록 로드
    loadMovies();

    // 현재 상영작 가져오기
    loadNowShowing();

    // 개봉 예정작 가져오기
    loadUpcoming();

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        redirectTo('login.html');
    });
});

// 시청목록에 추가
async function addToWatchlist(movieId) {
    try {
        await api.post('/watchlist', { movie_id: movieId });
        alert('시청목록에 추가되었습니다.');
    } catch (error) {
        alert(error.message);
    }
}

// 좋아요 토글
async function toggleLike(movieId) {
    try {
        await api.post('/likes', { movie_id: movieId });
        alert('좋아요 상태가 변경되었습니다.');
    } catch (error) {
        alert(error.message);
    }
}

// 영화 카드 생성 함수
function createMovieCard(movie) {
    const card = document.createElement('div');
    card.className = 'movie-card';
    card.innerHTML = `
        <div class="movie-info">
            <h3>${movie.title}</h3>
            <p class="movie-detail">감독: ${movie.director}</p>
            <p class="movie-detail">장르: ${movie.genre}</p>
            <p class="movie-detail">개봉일: ${movie.open_date}</p>
            <p class="movie-detail">배우: ${movie.actors.join(', ')}</p>
            <div class="movie-actions">
                <button class="btn-like" data-movie-id="${movie.movie_code}" title="좋아요">
                    <i class="fas fa-heart"></i>
                </button>
                <button class="btn-watchlist" data-movie-id="${movie.movie_code}" title="찜하기">
                    <i class="fas fa-bookmark"></i>
                </button>
            </div>
        </div>
    `;

    // 좋아요 버튼 이벤트
    const likeBtn = card.querySelector('.btn-like');
    likeBtn.addEventListener('click', async () => {
        try {
            await api.post('/likes', {
                target_type: 'movie',
                target_value: movie.movie_code
            });
            likeBtn.classList.add('active');
            showToast('좋아요가 등록되었습니다.');
        } catch (error) {
            if (error.message.includes('already liked')) {
                await api.delete('/likes', {
                    target_type: 'movie',
                    target_value: movie.movie_code
                });
                likeBtn.classList.remove('active');
                showToast('좋아요가 취소되었습니다.');
            } else {
                showToast(error.message);
            }
        }
    });

    // 찜하기 버튼 이벤트
    const watchlistBtn = card.querySelector('.btn-watchlist');
    watchlistBtn.addEventListener('click', async () => {
        try {
            await api.post('/watchlist', {
                movie_id: movie.movie_code
            });
            watchlistBtn.classList.add('active');
            showToast('찜 목록에 추가되었습니다.');
        } catch (error) {
            if (error.message.includes('already in watchlist')) {
                await api.delete(`/watchlist/${movie.movie_code}`);
                watchlistBtn.classList.remove('active');
                showToast('찜 목록에서 제거되었습니다.');
            } else {
                showToast(error.message);
            }
        }
    });

    return card;
}

// 토스트 메시지 표시
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// 영화 검색
async function searchMovies() {
    const query = searchInput.value.trim();
    if (!query) return;

    try {
        const response = await api.get(`/movies/search?title=${encodeURIComponent(query)}`);
        searchResults.innerHTML = '';
        response.results.forEach(movie => {
            searchResults.appendChild(createMovieCard(movie));
        });
    } catch (error) {
        showError(searchResults, '영화 검색 중 오류가 발생했습니다.');
    }
}

// 현재 상영작 가져오기
async function loadNowShowing() {
    try {
        const response = await api.get('/movies/now_showing');
        nowShowing.innerHTML = '';
        response.now_showing.forEach(movie => {
            nowShowing.appendChild(createMovieCard(movie));
        });
    } catch (error) {
        showError(nowShowing, '현재 상영작을 불러오는 중 오류가 발생했습니다.');
    }
}

// 개봉 예정작 가져오기
async function loadUpcoming() {
    try {
        const response = await api.get('/movies/upcoming');
        upcoming.innerHTML = '';
        response.upcoming_movies.forEach(movie => {
            upcoming.appendChild(createMovieCard(movie));
        });
    } catch (error) {
        showError(upcoming, '개봉 예정작을 불러오는 중 오류가 발생했습니다.');
    }
}

// 이벤트 리스너
searchBtn.addEventListener('click', searchMovies);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchMovies();
}); 