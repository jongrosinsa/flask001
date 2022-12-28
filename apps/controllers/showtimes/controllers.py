from flask import Blueprint, render_template, request
from datetime import datetime, timedelta

from sqlalchemy import and_

from apps.common.auth import signin_required
from apps.database.models import Showtime, Movie, TheaterTicket, Theater

app = Blueprint('showtimes', __name__, url_prefix='/showtimes')


@app.route('', methods=['GET'])
@signin_required
def index():
    week = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
    week_list = []
    now = datetime.now()
    now_weekday = now.weekday()                                                # 3 (= 목요일)

    args = request.args
    movie_id = args.get('movie_id')                                            # movie_id = 1 = 영화
    selected_date = args.get('date', now.strftime('%y-%m-%d'))                 # 요청보낸 시간을 데이터를 바인딩해서 현재시간과 영화시작시간 비교함
    selected_cinema_id =  args.get('cinema_id')                                # selcted_cinema_id = 1 = 용산

    for i in range(now_weekday, now_weekday +7):
        day = i - now_weekday
        date = now + timedelta(days=day)
        i %= 7
        week_list.append({'weekday': week[i], 'date': date.strftime('%y-%m-%d')})  # 결국 리스트에 [weekday:wed, date :2022-11-23] 의 딕셔너리가 바인딩됨 

    if selected_cinema_id:
        movies = Movie.query.join(Showtime, and_(Showtime.movie_id == Movie.id, Showtime.cinema_id == selected_cinema_id))
    else:
        movies = Movie.query.join(Showtime, Showtime.movie_id == Movie.id)
    if movie_id:
        movies = movies.filter_by(movie_id=movie_id)

    movies = movies.all()                                                       # 직접 /showtimes로 접속하면, 모든 MovieModel의 영화가 movies에 바인딩 되고, 영화선택, 상영관선택 하는경우 선택한 영화만 바인딩된다.



    movie_list = []                                          
    for movie in movies:                                                        # MovieModel 1, title, director, description, running_time, age_rating
        showtime_list = []
        showtimes = Showtime.query.filter(Showtime.end_time < now + timedelta(days=1)).\
            filter(Showtime.movie_id == movie.id).all()
        for showtime in showtimes:
            theater_ticket_cnt = TheaterTicket.query.filter(TheaterTicket.theater_id == showtime.theater.id).\
                filter(TheaterTicket.showtime_id == showtime.id).count()
            seat = showtime.theater.seat - theater_ticket_cnt
            showtime_list.append(dict(id=showtime.id, start_time=showtime.start_time, end_time=showtime.end_time, theater=dict(id=showtime.theater.id, seat=seat, title=showtime.theater.title)))

        movie_list.append(dict(id=movie.id, title=movie.title, director=movie.director, age_rating=movie.age_rating, showtimes=showtime_list))
    
    return render_template('showtimes/index.html',  date=selected_date, cinema_id=selected_cinema_id, movie_id=movie_id, movies=movie_list, week_list=week_list, now=datetime.now())