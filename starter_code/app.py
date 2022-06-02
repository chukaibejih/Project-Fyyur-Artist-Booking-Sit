#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from models import db, Venue, Artist, Show
from flask_migrate import Migrate
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import null
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
db.init_app(app)
moment = Moment(app)
app.config.from_object('config')
migrate = Migrate(app, db)
     

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, datetime):
    value = value.strftime('%Y-%m-%d %H:%M:%S')
  date = dateutil.parser.parse(value, ignoretz=True)
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


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
# returned real data from querying the database
def venues():
  return render_template('pages/venues.html', venues=Venue.query.all())

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implemented a search on venues with partial string search. Ensure it is case-insensitive.
  search_term = request.form.get('search_term', '')
  if search_term != '':
      search_result = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
      response = {
          "count": len(search_result),
          "data": search_result
      }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id including it's upcoming and past shows

  current_date = datetime.now()
  upcoming_shows = []
  past_shows = []
  venue = Venue.query.get(venue_id)
  for show in venue.shows:
    if show.start_time > current_date:
          upcoming_shows.append(show)
    else:
      past_shows.append(show)
  data = vars(venue)
  data['upcoming_shows'] = upcoming_shows
  data['past_shows'] = past_shows
  data['upcoming_shows_count'] = len(upcoming_shows)
  data['past_shows_count'] = len(past_shows)

  # past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==Artist.id).filter
  # (Show.start_time<datetime.now())   
  # past_shows = []
  # for show in past_shows_query():
  #     past_shows.append(show)
  # data['past_shows'] = past_shows
  # data['past_shows_count'] = len(past_shows)

  # upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==Artist.id).filter
  # (Show.start_time>datetime.now())
  # upcoming_shows = []
  # for show in upcoming_shows_query():
  #     upcoming_shows.append(show)
  # data['upcoming_shows'] = upcoming_shows
  # data['upcoming_shows_count'] = len(upcoming_shows)
 

  data = Venue.query.get(venue_id)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion

  form = VenueForm()
  if form.validate_on_submit():

    try:
      new_venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        website_link = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
        )

      db.session.add(new_venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except:
      db.session.rollback()
      # on unsuccessful db insert, flash success
      flash('An error occurred. Venue ' + ' could not be listed.')
      print(sys.exc_info())

    finally:
      db.session.close()

  else:
    for field, message in form.errors.items():
        flash(field + ' - ' + str(message))
    
  return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # This endpoint takes a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handled cases where the session commit could fail.

  # Implemented a button to delete a Venue on a Venue Page, have it so that
  # deletes a venue it the db then redirect the user to the homepage
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be deleted.')
  finally:
    db.session.close()
    return jsonify({'success': True})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # returned real data from querying the database
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implemented a search on artists with partial string search. 

  search_term = request.form.get('search_term', '')
  if search_term != '':
    search_results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
    response = {
      "count": len(search_results),
      "data": search_results
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id

  current_date = datetime.now()
  upcoming_shows = []
  past_shows =[]
  artist=Artist.query.get(artist_id)
  for show in artist.shows:
    if show.start_time > current_date:
      upcoming_shows.append(show)
    else:
      past_shows.append(show)
    
  data = vars(artist)
  data['upcoming_shows'] = upcoming_shows
  data['past_shows'] = past_shows
  data['upcoming_shows_count'] = len(upcoming_shows)
  data['past_shows_count'] = len(past_shows)
  
  data = Artist.query.get(artist_id)    
  return render_template('pages/show_artist.html', artist=data) 

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # populateed the edit form with fields from artist with ID <artist_id>
  artist=Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  print(form.data)  
  return render_template('forms/edit_artist.html', form=form, artist=Artist.query.get(artist_id))

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)
  if form.validate_on_submit():
    try:
      artist = Artist.query.get(artist_id)
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = form.genres.data
      artist.facebook_link = form.facebook_link.data
      artist.image_link = form.image_link.data
      artist.website = form.website.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_artist', artist_id=artist_id))
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
      for field, message in form.errors.items():
        flash(field + ' - ' + str(message))
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # populated the edit form with values from venue with ID <venue_id>
  venue= Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  print(form.data)
  return render_template('forms/edit_venue.html', form=form, venue= Venue.query.get(venue_id))

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form)
  if form.validate_on_submit():
    try: 
      venue = Venue.query.get(venue_id)
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.genres = form.genres.data
      venue.facebook_link = form.facebook_link.data
      venue.image_link = form.image_link.data
      venue.website_link = form.website_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_venue', venue_id=venue_id))
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message))
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # inserts form data as a new Artist record in the db, instead
  # modify data to be the data object returned from db insertion

  form = ArtistForm()
  if form.validate_on_submit():
    try: 
      new_artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
      )

      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + 'was successfully listed!')
    except:
      db.rollback()
      flash('An error occured. Artist' + 'could not be listed.')
      print(sys.exc_info())
    finally:
      db.session.close()
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message))

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows') 
def shows():
  # displays list of shows at /shows

  data = []
  shows = Show.query.all()
  for show in shows:
    if show.start_time > datetime.now():
          data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # inserts form data as a new Show record in the db, instead

  form = ShowForm()
  try:
    new_show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
      )
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occured. Show could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
    
  return render_template('pages/home.html')

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
