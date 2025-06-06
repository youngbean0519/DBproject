import { api, showError } from './utils.js';
import { checkAuth } from './auth.js';

document.addEventListener('DOMContentLoaded', async () => {
    if (!await checkAuth()) return;

    const likesContainer = document.getElementById('likes-container');

    async function loadLikes() {
        try {
            const res = await api.get('/likes');
            const likes = res.liked_items || [];
            displayLikes(likes);
        } catch (error) {
            showError(document.querySelector('.error'), error.message);
        }
    }

    function displayLikes(likes) {
        if (!likes.length) {
            likesContainer.innerHTML = '<p>좋아요한 영화가 없습니다.</p>';
            return;
        }
        likesContainer.innerHTML = likes.map(like => {
            // 이유를 <ul>로 예쁘게 출력
            let reasonsHTML = '';
            if (like.reasons && Array.isArray(like.reasons) && like.reasons.length > 0) {
                reasonsHTML = `
                    <ul class="like-reasons">
                        ${like.reasons.map(r => `<li><strong>${r.type}</strong>: ${r.value}</li>`).join('')}
                    </ul>
                `;
            }
            
            return `
                <div class="like-item">
                    <div class="item-details">
                        <h3>${like.title || '제목 없음'}</h3>
                        ${reasonsHTML}
                    </div>
                    <div class="item-actions">
                        <button onclick="removeLike('${like.movie_id}')">좋아요 취소</button>
                    </div>
                </div>
            `;
        }).join('');
    }

    window.removeLike = async function(movieId) {
        try {
            await api.post('/likes/delete', {
                movie_id: movieId,
                _method: 'DELETE'
            });
            alert('좋아요가 취소되었습니다.');
            loadLikes();
        } catch (error) {
            alert(error.message);
        }
    };

    // 좋아요 버튼 클릭 시
    window.addLike = async function(movieId, reasonsArray) {
        try {
            await api.post('/likes', {
                movie_id: movieId,
                reasons: reasonsArray // 예: [{type: "actor", value: "톰 행크스"}]
            });
            alert('좋아요가 추가되었습니다.');
            loadLikes();
        } catch (error) {
            alert(error.message);
        }
    };

    loadLikes();
});