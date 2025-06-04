import { api, showError } from './utils.js';
import { checkAuth } from './auth.js';

document.addEventListener('DOMContentLoaded', async () => {
    if (!await checkAuth()) return;

    const moviesContainer = document.getElementById('movies-container');
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');

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

    if (searchButton) {
        searchButton.addEventListener('click', () => {
            const query = searchInput.value.trim();
            loadMovies(query);
        });
    }

    // 초기 영화 목록 로드
    loadMovies();
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