import { api, showError } from './utils.js';
import { checkAuth } from './auth.js';

document.addEventListener('DOMContentLoaded', async () => {
    if (!await checkAuth()) return;

    const likesContainer = document.getElementById('likes-container');

    async function loadLikes() {
        try {
            const likes = await api.get('/likes');
            displayLikes(likes);
        } catch (error) {
            showError(document.querySelector('.error'), error.message);
        }
    }

    function displayLikes(likes) {
        likesContainer.innerHTML = likes.map(like => `
            <div class="like-item">
                <img src="${like.movie.poster_url}" alt="${like.movie.title}">
                <div class="item-details">
                    <h3>${like.movie.title}</h3>
                    <p>${like.movie.release_year}</p>
                    <p>좋아요한 날짜: ${new Date(like.created_at).toLocaleDateString()}</p>
                </div>
                <div class="item-actions">
                    <button onclick="removeLike(${like.movie.id})">좋아요 취소</button>
                    <button onclick="addToWatchlist(${like.movie.id})">시청목록 추가</button>
                </div>
            </div>
        `).join('');
    }

    // 초기 좋아요 목록 로드
    loadLikes();
});

// 좋아요 취소
async function removeLike(movieId) {
    try {
        await api.delete(`/likes/${movieId}`);
        alert('좋아요가 취소되었습니다.');
        location.reload();
    } catch (error) {
        alert(error.message);
    }
}

// 시청목록에 추가
async function addToWatchlist(movieId) {
    try {
        await api.post('/watchlist', { movie_id: movieId });
        alert('시청목록에 추가되었습니다.');
    } catch (error) {
        alert(error.message);
    }
} 