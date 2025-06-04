import { api, showError } from './utils.js';
import { checkAuth } from './auth.js';

document.addEventListener('DOMContentLoaded', async () => {
    if (!await checkAuth()) return;

    const recommendationsContainer = document.getElementById('recommendations-container');
    const genreFilter = document.getElementById('genre-filter');

    async function loadRecommendations(genre = '') {
        try {
            const endpoint = genre ? `/recommend?genre=${encodeURIComponent(genre)}` : '/recommend';
            const recommendations = await api.get(endpoint);
            displayRecommendations(recommendations);
        } catch (error) {
            showError(document.querySelector('.error'), error.message);
        }
    }

    function displayRecommendations(recommendations) {
        recommendationsContainer.innerHTML = recommendations.map(movie => `
            <div class="recommendation-card">
                <img src="${movie.poster_url}" alt="${movie.title}">
                <div class="recommendation-details">
                    <h3>${movie.title}</h3>
                    <p>${movie.release_year}</p>
                    <p>장르: ${movie.genres.join(', ')}</p>
                    <p>추천 이유: ${movie.recommendation_reason}</p>
                </div>
                <div class="recommendation-actions">
                    <button onclick="addToWatchlist(${movie.id})">시청목록 추가</button>
                    <button onclick="toggleLike(${movie.id})">좋아요</button>
                </div>
            </div>
        `).join('');
    }

    if (genreFilter) {
        genreFilter.addEventListener('change', (e) => {
            loadRecommendations(e.target.value);
        });
    }

    // 초기 추천 영화 로드
    loadRecommendations();
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