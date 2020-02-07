from flask import Flask, session, render_template, request, flash, redirect, send_file
from flask_session import Session
from time import sleep
import pandas as pd
import math
import numpy as np
from zipfile import ZipFile
import json
import os, shutil, io
import psycopg2

# self import
from psycopg2_blob import seventoten,query2,id_to_title,get_imdb_users,imdb_user_lookup,read_users
from w2v_inference import *
from r2v_inference import *
from functions import multi_read,multi_jsonify,multi_read_json,rec_edit,multi_dump,multi_session,multi_load,bool_func,links,highlight_watchlist

application = Flask(__name__)
application.secret_key = 'secret_bee'
SESSION_TYPE = 'filesystem'
application.config.from_object(__name__)
Session(application)

master_w2v = 'models/w2v_limitingfactor_v3.51.model'
master_r2v = 'models/r2v_Botanist_v1.1000.5.model'

@application.route("/")
def index():
    '''
    Main Page, has no real function as of now
    '''
    return render_template("public/Homepage.html")

@application.route("/letterboxd_upload", methods=["GET", "POST"])
def lb_upload():
    '''
    allows you to upload your ratings csv that you got from imdb
    '''
    return render_template('public/letterboxd_upload.html')

@application.route('/letterboxd_submission', methods=['GET','POST'])
def lb_submit():
    '''
    next step for letterboxd, this page gets the zipfile from the previous page, extracts four csvs and commits them
    to the session. HTML wise, this page presents two sliders that are used by the model
    '''
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # no file name
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if request.files:
            session.clear()
            file = request.files["file"]
            tag = str(np.random.uniform()) # make a temp folder with a random name
            with ZipFile(file, 'r') as zip:
                zip.extractall(path=f'temp{tag}', members=['ratings.csv',
                                                           'reviews.csv',
                                                           'watchlist.csv',
                                                           'watched.csv'])

            # letterboxd seems to always export as cp1252 encoding regardless of users' OS. Weird!
            ratings = pd.read_csv(f'temp{tag}/ratings.csv', encoding='cp1252')
            reviews, watched, watchlist = multi_read(['reviews','watched','watchlist'],tag)

            (session['ratings'],
            session['reviews'],
            session['watched'],
            session['watchlist']) = multi_jsonify([ratings,reviews,watched,watchlist])

            sleep(1) # wait for session to save
            shutil.rmtree(f'temp{tag}') # remove temp folder

            return render_template('public/letterboxd_submission.html',
                                    data=ratings.sort_values(by=['Date'],
                                    ascending=False).head().to_html(index=False))

@application.route('/groa_recommendations', methods=['GET', 'POST'])
def groa_recommend():
    '''
    Shows recommendations from your Letterboxd choices
    '''
    print('request1:'+str(request.referrer))
    if '/imdb_submission' in str(request.referrer):
        ratings = pd.read_json(session['ratings'])
        bad_rate = int(request.form['bad_rate'])/2
        good_rate = int(request.form['good_rate'])/2
        watched = pd.DataFrame() # IMDb user only uploads ratings
        watchlist = pd.DataFrame()
        extra_weight = "extra_weight" in request.form # user requests extra weighting
    elif '/user_reviews' in str(request.referrer):
        ratings,reviews = multi_read_json(['ratings','reviews'])
        watched = pd.DataFrame()
        watchlist = pd.DataFrame()
        bad_rate = int(request.form['bad_rate'])/2
        good_rate = int(request.form['good_rate'])/2
        hidden = "hidden" in request.form # user requests hidden gems
        cult = "cult" in request.form # user requests cult movies
        extra_weight = "extra_weight" in request.form # user requests cult movies
    else:
        ratings,reviews,watched,watchlist=multi_read_json(['ratings','reviews','watched','watchlist'])
        bad_rate = float(request.form['bad_rate'])
        good_rate = float(request.form['good_rate'])
        hidden = "hidden" in request.form # user requests hidden gems
        cult = "cult" in request.form # user requests cult movies
        extra_weight = "extra_weight" in request.form # user requests cult movies

    # initialize both models and connect them to database
    s = Recommender(master_w2v)
    s.connect_db()
    r = r2v_Recommender(master_r2v)
    r.connect_db()

    # prep user watch history
    good_list, bad_list, hist_list, val_list, ratings_dict = prep_data(
                                        ratings, watched, watchlist,
                                        good_threshold=good_rate,
                                        bad_threshold=bad_rate)

    # pass dictionary of ratings if the user requests extra weighting
    weighting = ratings_dict if extra_weight else {}

    # get recs based on ratings, watch history
    recs = pd.DataFrame(s.predict(good_list, bad_list, hist_list, val_list,
                        ratings_dict=weighting, scoring=True),
                        columns=['Title', 'Year', 'URL', 'Avg. Rating', '# Votes',
                        'Similarity Score','Movie ID'])
    print('request2:'+str(request.referrer))
    if ('letterboxd_submission' or 'user_reviews') in str(request.referrer):
        # prep user reviews
        reviews = prep_reviews(reviews)

        # make empty dataframes to return if either option is deselected
        hidden_df = pd.DataFrame(columns=['Title', 'Year', 'URL', '# Votes', 'Avg. Rating',
                'User Rating', 'Reviewer', 'Review', 'Movie ID'])
        cult_df = pd.DataFrame(columns=['Title', 'Year', 'URL', '# Votes', 'Avg. Rating',
                'User Rating', 'Reviewer', 'Review', 'Movie ID'])

        if hidden or cult:
            cult_results, hidden_results = r.predict(reviews, hist_list=hist_list)
            if cult:
                cult_df = pd.DataFrame(cult_results,
                    columns=['Title', 'Year', 'URL', '# Votes', 'Avg. Rating',
                            'User Rating', 'Reviewer', 'Review', 'Movie ID'])
                cult_df = rec_edit(cult_df, val_list)
            if hidden:
                hidden_df = pd.DataFrame(hidden_results,
                    columns=['Title', 'Year', 'URL', '# Votes', 'Avg. Rating',
                            'User Rating', 'Reviewer', 'Review', 'Movie ID'])
                hidden_df = rec_edit(hidden_df, val_list)
    else:
        hidden_df = cult_df = pd.DataFrame()
    recs['Liked by fans of...'] = recs['Movie ID'].apply(lambda x: s.get_most_similar_title(x, good_list))
    recs = rec_edit(recs, val_list)
    id_list = recs['Movie ID'].to_list()

    session.clear()
    if ('letterboxd_submission' or 'user_reviews') in str(request.referrer):
        if hidden:
            session['hidden_df'] = hidden_df.to_json()
        if cult:
            session['cult_df'] = cult_df.to_json()
    session['recs'] = recs.to_json()
    session['id_list'],session['good_list'],session['bad_list'],session['hist_list'],session['val_list'],session['ratings_dict']=multi_dump([id_list,good_list,bad_list,hist_list,val_list,ratings_dict])

    if ('letterboxd_submission' or 'user_reviews') in str(request.referrer):
        session['good_rate'],session['bad_rate'],session['hidden'],session['cult'],session['extra_weight']=multi_session([good_rate,bad_rate,hidden,cult,extra_weight])
    else:
        session['good_rate'],session['bad_rate'],session['extra_weight']=multi_session([good_rate,bad_rate,extra_weight])


    recs = recs.drop(columns='Movie ID')

    return render_template('public/Groa_recommendations.html',
                            data = recs.to_html(index=False,escape=False),
                            hidden_data = hidden_df.to_html(index=False,escape=False),
                            cult_data = cult_df.to_html(index=False,escape=False))

@application.route('/resubmission',methods=['POST'])
def resubmit():
    '''
    This page takes the ids from the recommedation page that the user liked and adds them to
    '''
    try:
        checked_list = json.loads(session['checked_list'])
    except:
        checked_list = []
    try:
        rejected_list = json.loads(session['rejected_list'])
    except:
        rejected_list = []
    checked_list.extend(request.form.getlist('upvote')) # log upvotes
    rejected_list.extend(request.form.getlist('downvote')) # log downvotes

    id_list,good_list,bad_list,hist_list,val_list=multi_load(['id_list','good_list','bad_list','hist_list','val_list'])

    ratings_dict = json.loads(session['ratings_dict'])
    try:
        hidden = session['hidden'] # TODO: add hidden and cult to resubmission
    except:
        pass
    try:
        cult = session['cult']
    except:
        pass
    extra_weight = session['extra_weight']
    s = Recommender(master_w2v)
    s.connect_db()

    # pass dictionary of ratings if the user requests extra weighting
    weighting = ratings_dict if extra_weight else {}

    stride = len(checked_list) + len(rejected_list) # number of recs to replace

    recs = pd.DataFrame(s.predict(good_list, bad_list, hist_list, val_list,
                ratings_dict=weighting, checked_list=checked_list,
                rejected_list=rejected_list,
                n=100+stride, harshness=1, scoring=False),
                columns=['Title', 'Year', 'URL', 'Avg. Rating', '# Votes',
                'Similarity Score','Movie ID'])

    recs['Liked by fans of...'] = recs['Movie ID'].apply(lambda x: s.get_most_similar_title(x, good_list))

    recs=rec_edit(recs, val_list)

    id_list2 = recs['Movie ID'].to_list()
    difference_list = list(set(id_list2).difference(set(id_list)))

    recs['New Rec?'] = bool_func(recs['Movie ID'],difference_list)
    recs['Title'] = highlight_watchlist(recs['Movie ID'], recs['Title'], val_list)
    cols=recs.columns.to_list()
    recs=recs[cols[-1:]+cols[:-1]] #puts New Rec? column as column number 1 or number 0 if you're a computer

    session['id_list'],session['checked_list'],session['rejected_list']=multi_dump([id_list2,checked_list,rejected_list])

    session['recs'] = recs.to_json()
    recs.drop(columns='Movie ID')
    return render_template('public/re_recommendations.html',
                            data=recs.to_html(escape=False,index=False))

@application.route('/imdb_upload')
def imdb_upload():
    '''
    allows you to upload your ratings csv that you got from imdb
    '''
    return render_template('public/imdb_upload.html')

@application.route('/imdb_submission',methods = ['GET','POST'])
def imdb_submit():
    '''
    the result of the imdb upload, you can see a table of your rated movies
    and adjust them according to year released and personal rating
    '''
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # no file name
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if request.files:
            session.clear()
            file = request.files["file"]
            try:
                ratings = pd.read_csv(file, encoding='cp1252')
            except:
                ratings = pd.read_csv(file, encoding='latin1')
            # strip leading "tt"s from ID column
            ratings['Const'] = ratings['Const'].str.strip('t')

            ratings = ratings.drop(columns=['Title Type','Num Votes','Directors','Genres',
                                    'URL','Release Date'], errors='ignore')
            session['ratings'] = ratings.to_json()

            return render_template('public/imdb_submission.html',
                    name='Watched List', data=ratings.sort_values(by=['Date Rated'],
                    ascending=False).head().to_html(index=False))

@application.route('/imdb_recommendations',methods=['GET','POST'])
def imdb_recommend():
    '''
    Shows recommendations from your IMDB choices
    '''

    ratings = pd.read_json(session['ratings'])

    bad_rate = int(request.form['bad_rate'])/2
    good_rate = int(request.form['good_rate'])/2

    watched = pd.DataFrame() # IMDb user only uploads ratings
    watchlist = pd.DataFrame()

    extra_weight = "extra_weight" in request.form # user requests extra weighting
    # connect
    s = Recommender(master_w2v)
    s.connect_db()

    # prep user watch history
    good_list, bad_list, hist_list, val_list, ratings_dict = prep_data(
                                        ratings, watched, watchlist, good_threshold=good_rate, bad_threshold=bad_rate)

    # pass dictionary of ratings if the user requests extra weighting
    weighting = ratings_dict if extra_weight else {}

    # get recs based on ratings, watch history
    recs = pd.DataFrame(s.predict(good_list, bad_list, hist_list, val_list,
                        ratings_dict=weighting, scoring=False),
                        columns=['Title', 'Year', 'URL', 'Avg. Rating',
                        '# Votes', 'Similarity Score','Movie ID'])

    recs['Liked by fans of...'] = recs['Movie ID'].apply(lambda x: s.get_most_similar_title(x, good_list))
    recs = rec_edit(recs,good_list)
    id_list = recs['Movie ID'].to_list()

    session.clear()
    session['recs'] = recs.to_json()

    session['id_list'],session['good_list'],session['bad_list'],session['hist_list'],session['val_list'],session['ratings_dict']=multi_dump([id_list,good_list,bad_list,hist_list,val_list,ratings_dict])
    session['good_rate'],session['bad_rate'],session['extra_weight']=multi_session([good_rate,bad_rate,extra_weight])

    recs = recs.drop(columns = 'Movie ID')

    return render_template('public/Groa_recommendations.html',
                            data=recs.to_html(index=False,escape=False))

@application.route('/export_recs', methods=['POST'])
def download_recs():
    """Creates a download popup"""
    try:
        tag = str(np.random.uniform())[2:7]
        os.makedirs('exports', exist_ok=True) # make temp dir with random name
        if "upvote" in request.form['button']:
            my_path = f'exports/Groa_upvotes{tag}.csv'
            try:
                checked_list = json.loads(session['checked_list'])
            except:
                checked_list = []
            checked_list.extend(request.form.getlist('upvote')) # log upvotes
            s = Recommender(master_w2v)
            s.connect_db()
            checked_list = [fill_id(x) for x in checked_list]
            checked_info = [s._get_info(x) for x in checked_list]
            recs_df = pd.DataFrame(checked_info,
                                    columns=['Title', 'Year', 'URL',
                                    'Avg. Rating', '# Votes','Blank', 'ID'])
            # drop ID because Excel truncates numbers with leading zeroes
            recs_df = recs_df.drop(columns=['Blank', 'ID'])
        elif "cult" in request.form['button']:
            my_path = f'exports/Groa_cult_movies{tag}.csv'
            try:
                recs_df = pd.read_json(session['cult_df'])
            except Exception as e:
                print(e)
                return None
        elif "hidden" in request.form['button']:
            my_path = f'exports/Groa_hidden_gems{tag}.csv'
            try:
                recs_df = pd.read_json(session['hidden_df'])
            except Exception as e:
                print(e)
                return None
        else:
            my_path = f'exports/Groa_recs{tag}.csv'
            recs_df = pd.read_json(session['recs'])
            recs_df = recs_df.drop(columns=['Vote Up', 'Vote Down'])
        recs_df.to_csv(my_path, index=False)
        return_data = io.BytesIO() # write file to memory so it can be deleted
        with open(my_path, 'rb') as myfile:
            return_data.write(myfile.read())
        return_data.seek(0) # move cursor to start
        os.remove(my_path) # delete temp directory
        return send_file(return_data, mimetype='text/csv')
    except Exception as e:
        print(e)

@application.route('/user_search',methods = ["GET","POST"])
def user_search():

    users = read_users("Usernames.txt")
    #users = get_imdb_users()
    return render_template('public/user_search.html',users = users)

@application.route('/user_reviews',methods = ["GET","POST"])
def user_reviews():
    name = request.form['Username']
    df,ratings,reviews = imdb_user_lookup(name)


    session['ratings'],session['reviews']=multi_jsonify([ratings,reviews])

    return render_template('public/user_reviews.html', data=df.head(10).to_html(index=False), name=name)

@application.route('/user_search_recommendations', methods=['GET', 'POST'])
def user_search_recommend():
    '''
    Shows recommendations from your Letterboxd choices
    '''


    ratings,reviews = multi_read_json(['ratings','reviews'])

    watched = pd.DataFrame()
    watchlist = pd.DataFrame()
    bad_rate = int(request.form['bad_rate'])/2
    good_rate = int(request.form['good_rate'])/2
    hidden = "hidden" in request.form # user requests hidden gems
    cult = "cult" in request.form # user requests cult movies
    extra_weight = "extra_weight" in request.form # user requests cult movies

    # connect
    s = Recommender(master_w2v)
    s.connect_db()
    r = r2v_Recommender(master_r2v)
    r.connect_db()

    # prep user watch history
    good_list, bad_list, hist_list, val_list, ratings_dict = prep_data(
                                        ratings, watched, watchlist,
                                        good_threshold=good_rate,
                                        bad_threshold=bad_rate)

    # pass dictionary of ratings if the user requests extra weighting
    if extra_weight:
        weighting = ratings_dict
    else:
        weighting = {}

    # get recs based on ratings, watch history
    recs = pd.DataFrame(s.predict(good_list, bad_list, hist_list, val_list,
                        ratings_dict=weighting, scoring=True),
                        columns=['Title', 'Year', 'URL', 'Avg. Rating', '# Votes',
                        'Similarity Score','Movie ID'])

    # prep user reviews
    reviews = prep_reviews(reviews)

    # make empty dataframes to return if either option is deselected
    hidden_df = pd.DataFrame(columns=['Title', 'Year', 'URL', '# Votes', 'Avg. Rating',
            'User Rating', 'Reviewer', 'Review', 'Movie ID'])
    cult_df = pd.DataFrame(columns=['Title', 'Year', 'URL', '# Votes', 'Avg. Rating',
            'User Rating', 'Reviewer', 'Review', 'Movie ID'])

    if hidden or cult:
        cult_results, hidden_results = r.predict(reviews, hist_list=hist_list)
        if cult:
            cult_df = pd.DataFrame(cult_results,
                columns=['Title', 'Year', 'URL', '# Votes', 'Avg. Rating',
                        'User Rating', 'Reviewer', 'Review', 'Movie ID'])
            cult_df = rec_edit(cult_df, val_list)
        if hidden:
            hidden_df = pd.DataFrame(hidden_results,
                columns=['Title', 'Year', 'URL', '# Votes', 'Avg. Rating',
                        'User Rating', 'Reviewer', 'Review', 'Movie ID'])
            hidden_df = rec_edit(hidden_df, val_list)

    recs['Liked by fans of...'] = recs['Movie ID'].apply(lambda x: s.get_most_similar_title(x, good_list))
    recs = rec_edit(recs,val_list)

    id_list = recs['Movie ID'].to_list()

    session.clear()
    if hidden:
        session['hidden_df'] = hidden_df.to_json()
    if cult:
        session['cult_df'] = cult_df.to_json()
    session['recs'] = recs.to_json()

    session['id_list'],session['good_list'],session['bad_list'],session['hist_list'],session['val_list'],session['ratings_dict']=multi_dump([id_list,good_list,bad_list,hist_list,val_list,ratings_dict])

    session['good_rate'],session['bad_rate'],session['hidden'],session['cult'],session['extra_weight']=multi_session([good_rate,bad_rate,hidden,cult,extra_weight])

    recs = recs.drop(columns='Movie ID')

    return render_template('public/Groa_recommendations.html',
                            data = recs.to_html(index=False,escape=False),
                            hidden_data = hidden_df.to_html(index=False,escape=False),
                            cult_data = cult_df.to_html(index=False,escape=False))

if __name__ == "__main__":
    application.run(port=5000, debug=True)
