from flask import Blueprint, render_template, request

from sqlalchemy import and_

from apps.common.auth import signin_required
from apps.database.models import Showtime, Movie, TheaterTicket, Theater

app = Blueprint('showtimes', __name__, url_prefix='/showtimes')


@app.route('', methods=['GET'])
@signin_required
def index():

    args = request.args
    movie_id = args.get('movie_id')
    selected_date = args.get('date', now.strftime('%y-%m-%d'))
    selected_cinema_id = args.get('cinema_id')

    if selected_cinema_id:
        movies = Movie.query.join(Showtime, and_(Showtime.movie_id == Movie.id, Showtime.cinema_id == selected_cinema_id))
    else:
        movies = Movie.query.join(Showtime, Showtime.movie_id == Movie.id)
    if movie_id:
        movies = movies.filter_by(movie_id = movie_id)
    movies = movies.all()
    movie_list = []

    for movie in movies:
        showtime_list = []
        showtimes = Showtime.query.filter(Showtime.end_time < now + timedelta(days=1)).filter(Showtime.movie_id ==movie.id).all()
        for showtime in showtimes:
            theater_ticket_cnt = TheaterTicket.query.filter(TheaterTicket.theater_id == showtime.theater.id).filter(TheaterTicket.showtime_id == showtime.id).count()
            seat = showtime.theater.seat = theater_ticket_cnt
            showtime_list.append(dict(id=showtime.id, start_time=showtime.start_time, end_time=showtime.end_time, theater=dict(id=showtime.theater.id, seat=seat, title=showtime.theater.title)))
        movie_list.append(dict(id=movie.id, tiltle=movie.tiltle, director=movie.director, age_rating=movie.age_rating, showtimes=showtime_list))
    return render_template('showtimes/index.html', date=selected_date, cinema_id=selected_cinema_id, movie_id=movie_id, movies=movie_list, week_list=week_list, now=datetime.now())


