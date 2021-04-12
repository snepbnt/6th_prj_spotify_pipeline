SELECT * FROM btsalbum.features;

select * from tracks;
select * from features;

## bts 노래 전체 가져오기 쿼리문
select T.*
from
	(select a.id, 
			a.name, 
			t.popularity, 
            t.tracks_counts, 
            t.track_id, 
            t.track_name, 
            f.tempo,
            f.valence,
            f.liveness,
            f.acousticness,
            f.speechiness,
            f.danceability,
            f.energy,
            f.loudness,
            f.instrumentalness,
            track_duration_ms,
            date_format(a.release_date, '%Y-%m') as release_date
	from albums a 
	left join tracks t
	on a.id = t.album_id
	left join features f
	on t.track_id = f.id
    order by release_date desc) as T
order by popularity desc;

## bts 연도별 앨범 개수 쿼리문
select 
       date_format(release_date, '%Y') as release_year,
       count(date_format(release_date, '%Y'))
from albums
group by date_format(release_date, '%Y')
order by date_format(release_date, '%Y') asc;

## bts 노래 월별 카운트 및 월별 템포 평균
select t.track_id, 
	   t.track_name, 
       avg(f.tempo) avg_tempo, 
       count(date_format(t.album_release_date, '%Y-%m')),
       date_format(t.album_release_date, '%Y-%m') as release_date
from tracks t
left join features f
on t.track_id = f.id
group by date_format(t.album_release_date, '%Y-%m');