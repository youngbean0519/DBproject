import { api, showError } from './utils.js';
import { checkAuth } from './auth.js';

document.addEventListener('DOMContentLoaded', async () => {
    if (!await checkAuth()) return;

    const watchlistContainer = document.getElementById('watchlist-container');

    async function loadWatchlist() {
        try {
            const watchlist = await api.get('/watchlist');
            displayWatchlist(watchlist);
        } catch (error) {
            showError(document.querySelector('.error'), error.message);
        }
    }

    function displayWatchlist(watchlist) {
        watchlistContainer.innerHTML = watchlist.map(item => `
            <div class="watchlist-item">
                <img src="${item.movie.poster_url}" alt="${item.movie.title}">
                <div class="item-details">
                    <h3>${item.movie.title}</h3>
                    <p>${item.movie.release_year}</p>
                    <p>추가일: ${new Date(item.added_at).toLocaleDateString()}</p>
                </div>
                <div class="item-actions">
                    <button onclick="removeFromWatchlist(${item.movie.id})">삭제</button>
                    <button onclick="markAsWatched(${item.movie.id})">시청완료</button>
                </div>
            </div>
        `).join('');
    }

    // 초기 시청목록 로드
    loadWatchlist();
});

// 시청목록에서 삭제
async function removeFromWatchlist(movieId) {
    try {
        await api.delete(`/watchlist/${movieId}`);
        alert('시청목록에서 삭제되었습니다.');
        location.reload();
    } catch (error) {
        alert(error.message);
    }
}

// 시청완료로 표시
async function markAsWatched(movieId) {
    try {
        await api.put(`/watchlist/${movieId}`, { watched: true });
        alert('시청완료로 표시되었습니다.');
        location.reload();
    } catch (error) {
        alert(error.message);
    }
} 