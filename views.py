from flask import Blueprint, render_template, request, flash


x = ''

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        subr = request.form.get('subreddit')
        global x 
        x = str(subr)
        nbr = request.form.get("numberOfPosts")
        if('r/' in subr):
            flash('Do not include r/ in the name. Just type the name as it is', category='error')
        elif(len(subr) < 1) or (len(nbr) < 1):
            flash('Do not keep the subreddit name field or the number of posts field empty.', category='error')
        elif(int(nbr) > 10):
            flash('Do not put a number greater than 10.', category='error')
        else:
            scraping(subr, nbr)
            flash('Results fetched! Go to the results tab.', category='success')
    return render_template("input.html")

def scraping(subr,nbr):
    import praw
    from decouple import config
    import pandas as pd
    import time
    from detoxify import Detoxify



    rro = praw.Reddit(client_id=config('CLIENT_ID'), client_secret=config('CLIENT_SEC'), user_agent=config('USER_AGENT'))
    sub = str(subr)
    #keyword = input("What keyword do you want to look up?\n")
    nb = int(nbr)
    start = time.time()
    subreddit = rro.subreddit(sub)
    

    max = 0

    posts = subreddit.hot(limit=nb)
    #pdict = {"Post Title":[], "Post Text":[], "Upvotes":[], "Comments":[], "URL":[], "Toxicity":[], "Insult":[]}
    cdict = {"Post Title":[], "Post ID":[],"Comment":[], "Toxicity":[], "Insult":[]}
    for post in posts:

        print("======Post ID: ", post.id,"======")
        i = 0
        for top_level_comment in post.comments:
            if isinstance(top_level_comment, praw.models.MoreComments):
                continue
            if(i > 0):
                tox = Detoxify('original-small').predict(top_level_comment.body)
                print("++Comment Number ", i,"analyzed!")
                cdict["Post Title"].append(post.title)
                cdict["Post ID"].append(post.id)
                cdict["Comment"].append(top_level_comment.body)
                cdict["Toxicity"].append(str(round(tox["toxicity"]*100, 2))+"%")
                cdict["Insult"].append(str(round(tox["insult"]*100, 2))+"%")
            i += 1
            if(i > 10):
                break
        if( post.score > max):
            max = post.score
        



    toxic_comments = pd.DataFrame(cdict)

    toxic_comments = toxic_comments.sort_values(by="Toxicity", ascending=False)

    print(toxic_comments)
    end = time.time()
    print("Time spent scraping: ", round(end - start, 2), " s")


    iid = subr

    toxic_comments.to_csv(iid, index=False)
    pdfer = pd.read_csv(iid, index_col=False)
    name = iid +"_comments.html"
    pdfer.to_html("templates/"+name)
@views.route('/results')
def results():
    
    name = x+'_comments.html'
    return render_template(name)