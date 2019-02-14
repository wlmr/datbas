#### 4.
##### a. 
Theater -> Performance: theater_name
Movie -> Performance: movie_title

##### b.
Movie titles might be changed

##### c.
Ticket  as it has to use an id for its own uniqueness

##### d.
Ticket -> performance. We need to differentiate between the different tickets.

5: drawing

6:
theatres(_theatre_name_, capacity)
movies(title, _imdb_, year, running_time)
customers(_username_, name, pwd)
performances(/_theatre_name_/, /_movie_title_/, start_time, _performance_id_)
tickets(_identifier_, /_performance_id_/)


7:
	Either it could be done on the user side with(roughly):
select
    pz.movie_title,
    pz.start_time,
    t.theatre_name,
    t.capacity - coalesce(count(p.identifier), 0) as seats_left
from
    theatres t,
    tickets p,
    performances pz
where
    p.performance_id = pz.performance_id and
    pz.theatre_name = t.theatre_name
group by pz.movie_title
having count(p.identifier) > 0
;

which is a pretty complicated query, but it removes the need for additional data to be inserted into the table.

Also, one could add the column "seats_left" in the table "performances", and use a trigger to decrease the value
every time a new ticket is created (or increase it if a ticket is removed), which is less complicated, but adds
some redudancy as the information kept is already present.