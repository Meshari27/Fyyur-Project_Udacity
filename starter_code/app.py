#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from model import *


from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# TODO: connect to a local postgresql database #DONE


#----------------------------------------------------------------------------#
# Models. #Done
#----------------------------------------------------------------------------#



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#-----------------------------------------------------------------#
#  Venues #Done
#  ---------------------------------------------------------------#


@app.route('/venues')
def venues():

  data = []
  

  City_State = db.session.query(Venue.city, Venue.state).group_by(Venue.city,Venue.state).distinct()
  

  
  for y in City_State:
    venues = Venue.query.filter(Venue.city==y.city).filter(Venue.state==y.state).all()
    data.append({'city': y.city, 'state': y.state, 'venues': venues})
    print(data)

  return render_template('pages/venues.html', areas=data)



#Done
@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  search_term = request.form['search_term']
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))
  
  response = {}
  response['count'] = venues.count()
  response['data'] = venues

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))



#Done
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()
  coming_shows = []
  past_shows = []
  current_time = datetime.now()


  for show in shows:
    data = {
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': format_datetime(str(show.start_time))
    }
    if show.start_time > current_time:
      coming_shows.append(data)
    else:
      past_shows.append(data)


  data = {
    'id': venue.id,
    'name': venue.name,
    'genres' : venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state':venue.state,
    'phone':venue.phone,
    'image_link':venue.image_link,
    'facebook_link': venue.facebook_link,
    'website': venue.website,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'past_shows': past_shows,
    'upcoming_shows': coming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(coming_shows)
  }
  
  return render_template('pages/show_venue.html', venue=data)



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

#  ----------------------------------------------------------------
#  Artists #Done
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  
  artist = Artist.query.order_by('name').all()

  return render_template('pages/artists.html', artists=artist)



@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form['search_term']
  artist = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))
  
  response = {}
  response['count'] = artist.count()
  response['data'] = artist
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).all()
  past_shows = []
  coming_shows = []
  current_time = datetime.now()

  for show in shows:
    data = {
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': format_datetime(str(show.start_time))
    }
    if show.start_time > current_time:
      coming_shows.append(data)
    else:
      past_shows.append(data)

  data = {
    'id': artist.id,
    'name': artist.name,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'genres': artist.genres,
    'image_link': artist.image_link,
    'facebook_link': artist.facebook_link,
    'website': artist.website,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'past_shows': past_shows,
    'upcoming_shows': coming_shows,
    'past_show_count': len(past_shows),
    'upcoming_show_count': len(coming_shows)
  }
 
  return render_template('pages/show_artist.html', artist=data)


#  ----------------------------------------------------------------
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET']) #Done
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  form = request.form
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form.get('name'),
    artist.city = request.form.get('city'),
    artist.state = request.form.get('state'),
    artist.phone = request.form.get('phone'),
    artist.genres = request.form.getlist('genres'),
    artist.facebook_link = request.form.get('facebook_link'),
    artist.website = request.form.get('website'),
    artist.image_link = request.form.get('image_link')
    artist.seeking_venue = True if request.form.get('seeking_venue') in ('Yes') else False
    artist.seeking_description = request.form.get('seeking_description')
    
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Artist ' + form['name'] + ' was successfully updated!')
  else:
    flash('An error occured. Artist ' + form['name'] + ' could not be update')


  return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  form = request.form
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form.get('name'),
    venue.city = request.form.get('city'),
    venue.state = request.form.get('state'),
    venue.phone = request.form.get('phone'),
    venue.genres = request.form.getlist('genres'),
    venue.facebook_link = request.form.get('facebook_link'),
    venue.website = request.form.get('website'),
    venue.image_link = request.form.get('image_link'),
    venue.seeking_talent = True if request.form.get('seeking_talent') in ('Yes') else False
    venue.seeking_description = request.form.get('seeking_description')
    
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Artist ' + form['name'] + ' was successfully updated!')
  else:
    flash('An error occured. Artist ' + form['name'] + ' could not be update')


  return redirect(url_for('show_venue', venue_id=venue_id))


#  ----------------------------------------------------------------
#  Create Artist, Venue, and Show #Booooooooooooom DONE
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_venue = True if request.form.get('seeking_venue') in ('Yes') else False
    seeking_description = request.form.get('seeking_description')

    artist = Artist(name=name, city=city, state=state, phone=phone,
    genres=genres, image_link=image_link, facebook_link=facebook_link, website=website,
    seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An booom occured. Artist ' + request.form['name']+ ' could not be listed.')
  if not error:
    flash('Artist ' + request.form['name']+ ' was successfully listed!')
  return render_template('/pages/home.html')



@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    seeking_talent = True if request.form.get('seeking_talent') in ('Yes') else False
    seeking_description = request.form.get('seeking_description')

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone,
    genres=genres, image_link=image_link, facebook_link=facebook_link, website=website,
    seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An booom occured. Venue ' + request.form['name']+ ' could not be listed.')
  if not error:
    flash('Venue ' + request.form['name']+ ' was successfully listed!')
  return render_template('/pages/home.html')



@app.route('/shows/create')
def create_shows():
  
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    start_time = request.form['start_time']

    show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
   error = True
   db.session.rollback()
   print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed')

  return render_template('pages/home.html')




#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
 
 shows = db.session.query(Show).join(Artist).join(Venue).all()
 data = [{
   'venue_id' : show.venue_id,
   'venue_name': show.venue.name,
   'artist_id': show.artist.id,
   'artist_name': show.artist.name,
   'artist_image_link': show.artist.image_link,
   'start_time': format_datetime(str(show.start_time), 'full')
 } for show in shows]
   
 return render_template('pages/shows.html', shows=data)






@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')



#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
