import { api, showError } from './utils.js';
import { checkAuth } from './auth.js';

document.addEventListener('DOMContentLoaded', async () => {
    if (!await checkAuth()) return;

    const watchlistContainer = document.getElementById('watchlist-container');

    async function loadWatchlist() {
        try {
            const res = await api.get('/watchlist');
            // res가 { message: "...", watchlist: [...] } 형태이므로
            displayWatchlist(res.watchlist || []);
        } catch (error) {
            showError(document.querySelector('.error'), error.message);
        }
    }

    function displayWatchlist(watchlist) {
        if (!watchlist.length) {
            watchlistContainer.innerHTML = '<p>찜한 영화가 없습니다.</p>';
            return;
        }
        watchlistContainer.innerHTML = watchlist.map(item => {
            return `
                <div class="watchlist-item">
                    <div class="item-details">
                        <h3>${item.title || '제목 없음'}</h3>
                        <p>${item.director ? `감독: ${item.director}` : ''}</p>
                        <p>${item.release_date ? `개봉일: ${item.release_date}` : ''}</p>
                    </div>
                    <div class="item-actions">
                        <button onclick="removeFromWatchlist('${item.movie_id}')">찜 취소</button>
                    </div>
                </div>
            `;
        }).join('');
    }

    window.removeFromWatchlist = async function(movieId) {
        if (!confirm('정말로 찜을 취소하시겠습니까?')) return;
        try {
            await api.delete(`/watchlist/${movieId}`);
            alert('찜이 취소되었습니다.');
            loadWatchlist();
        } catch (error) {
            alert(error.message);
        }
    };

    loadWatchlist();
});