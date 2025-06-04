import { api, showError } from './utils.js';
import { checkAuth, getCurrentUser } from './auth.js';

document.addEventListener('DOMContentLoaded', async () => {
    if (!await checkAuth()) return;

    const user = getCurrentUser();
    if (!user.is_admin) {
        alert('관리자 권한이 필요합니다.');
        window.location.href = '/movies.html';
        return;
    }

    const moviesContainer = document.getElementById('admin-movies-container');
    const addMovieForm = document.getElementById('add-movie-form');

    async function loadMovies() {
        try {
            const movies = await api.get('/admin/movies');
            displayMovies(movies);
        } catch (error) {
            showError(document.querySelector('.error'), error.message);
        }
    }

    function displayMovies(movies) {
        moviesContainer.innerHTML = movies.map(movie => `
            <div class="admin-movie-item">
                <img src="${movie.poster_url}" alt="${movie.title}">
                <div class="movie-details">
                    <h3>${movie.title}</h3>
                    <p>${movie.release_year}</p>
                    <p>장르: ${movie.genres.join(', ')}</p>
                </div>
                <div class="admin-actions">
                    <button onclick="editMovie(${movie.id})">수정</button>
                    <button onclick="deleteMovie(${movie.id})">삭제</button>
                </div>
            </div>
        `).join('');
    }

    if (addMovieForm) {
        addMovieForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(addMovieForm);
            const movieData = {
                title: formData.get('title'),
                release_year: parseInt(formData.get('release_year')),
                genres: formData.get('genres').split(',').map(g => g.trim()),
                poster_url: formData.get('poster_url'),
                description: formData.get('description')
            };

            try {
                await api.post('/admin/movies', movieData);
                alert('영화가 추가되었습니다.');
                addMovieForm.reset();
                loadMovies();
            } catch (error) {
                showError(document.querySelector('.error'), error.message);
            }
        });
    }

    // 초기 영화 목록 로드
    loadMovies();
});

// 영화 수정
async function editMovie(movieId) {
    const newTitle = prompt('새로운 제목을 입력하세요:');
    if (!newTitle) return;

    try {
        await api.put(`/admin/movies/${movieId}`, { title: newTitle });
        alert('영화 정보가 수정되었습니다.');
        location.reload();
    } catch (error) {
        alert(error.message);
    }
}

// 영화 삭제
async function deleteMovie(movieId) {
    if (!confirm('정말로 이 영화를 삭제하시겠습니까?')) return;

    try {
        await api.delete(`/admin/movies/${movieId}`);
        alert('영화가 삭제되었습니다.');
        location.reload();
    } catch (error) {
        alert(error.message);
    }
} 