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
            
            // 탭별 데이터 로드
            if (tabId === 'nowShowing') loadNowShowing();
            if (tabId === 'upcoming') loadUpcoming();
        });
    });

    // 검색 기능
    async function searchMovies() {
        const query = searchInput.value.trim();
        if (!query) return;

        try {
            const data = await api.get(`/movies/search?title=${encodeURIComponent(query)}`);
            const movies = data.results || [];
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
            const data = await api.get('/movies/now_showing');
            const movies = data.now_showing || [];
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
            const data = await api.get('/movies/upcoming');
            const movies = data.upcoming_movies || [];
            upcoming.innerHTML = '';
            movies.forEach(movie => {
                upcoming.appendChild(createMovieCard(movie, true));
            });
        } catch (error) {
            showError(upcoming, '개봉 예정작을 불러오는 중 오류가 발생했습니다.');
        }
    }

    // 1. 모달 HTML 추가 (body 맨 아래에 삽입)
    function appendLikeModal() {
        if (document.getElementById('like-modal')) return;
        const modal = document.createElement('div');
        modal.id = 'like-modal';
        modal.style.display = 'none';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <h2>좋아요 이유 선택</h2>
                <form id="like-reason-form">
                    <label><input type="checkbox" name="reason" value="director"> 감독</label>
                    <label><input type="checkbox" name="reason" value="genre"> 장르</label>
                    <label><input type="checkbox" name="reason" value="actor"> 배우</label>
                    <label><input type="checkbox" name="reason" value="country"> 국가</label>
                    <label><input type="checkbox" name="reason" value="type"> 타입</label>
                    <div style="margin-top:1em;">
                        <button type="submit">제출</button>
                        <button type="button" id="like-modal-cancel">취소</button>
                    </div>
                </form>
            </div>
            <style>
                #like-modal { position:fixed; left:0; top:0; width:100vw; height:100vh; z-index:1000; }
                .modal-backdrop { position:absolute; left:0; top:0; width:100vw; height:100vh; background:rgba(0,0,0,0.5);}
                .modal-content { position:relative; background:#fff; width:300px; margin:10vh auto; padding:2em; border-radius:8px; z-index:1001;}
            </style>
        `;
        document.body.appendChild(modal);
    }
    appendLikeModal();

    // 2. 좋아요 버튼 클릭 시 모달 띄우기
    function openLikeModal(movieId) {
        const modal = document.getElementById('like-modal');
        modal.style.display = 'block';
        modal.dataset.movieId = movieId;
    }

    // 3. 모달 닫기
    function closeLikeModal() {
        const modal = document.getElementById('like-modal');
        modal.style.display = 'none';
        modal.dataset.movieId = '';
    }

    // 4. 모달 이벤트 등록
    const modal = document.getElementById('like-modal');
    if (modal) {
        // 제출
        modal.querySelector('#like-reason-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const movieId = modal.dataset.movieId;
            const reasons = Array.from(modal.querySelectorAll('input[name="reason"]:checked')).map(cb => cb.value);
            try {
                await api.post('/likes', {
                    movie_id: movieId,
                    reasons
                });
                alert('좋아요가 등록되었습니다.');
                closeLikeModal();
            } catch (error) {
                alert(error.message);
            }
        });
        // 취소
        modal.querySelector('#like-modal-cancel').addEventListener('click', closeLikeModal);
        // 배경 클릭 시 닫기
        modal.querySelector('.modal-backdrop').addEventListener('click', closeLikeModal);
    }

    // 영화 카드 생성
    function createMovieCard(movie, isUpcoming) {
        const card = document.createElement('div');
        card.className = 'movie-card';

        // movie_id 필드명 호환 처리
        const movieId = movie.movie_id || movie.movie_code || movie.id;

        let cardHTML = '';
        if (movie.rank) {
            cardHTML += `<div class="rank">${movie.rank}위</div>`;
        }
        cardHTML += `
            <div class="movie-info">
                <h3>${movie.title}</h3>
                <p class="movie-detail">감독: ${movie.director}</p>
                <p class="movie-detail">장르: ${movie.genre}</p>
                <p class="movie-detail">개봉일: ${movie.open_date}</p>
                <div class="movie-actions">
                    ${isUpcoming ? 
                        `<button class="btn-watchlist" data-movie-id="${movieId}" title="찜하기">
                            <i class="fas fa-bookmark"></i>
                        </button>` :
                        `<button class="btn-like" data-movie-id="${movieId}" title="좋아요">
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
            if (!isUpcoming) {
                actionBtn.addEventListener('click', () => openLikeModal(movieId));
            } else {
                actionBtn.addEventListener('click', async () => {
                    await toggleWatchlist(movieId, actionBtn);
                });
            }
        }

        return card;
    }

    // 좋아요 토글
    async function toggleLike(movieId, button) {
        try {
            await api.post('/likes', {
                movie_id: movieId,
                reasons
            });
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