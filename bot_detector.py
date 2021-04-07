# Hi there.
# I wrote this code when I was learning python.
# If you dont want to see horrible code, please click away.
# I can code better than this now, but I'm too lazy to rewrite it.
# Submit a PR if you want to help.
#------------------------------------------------------------------

import praw
import datetime
import difflib

def score_helper(score):
    if score <= 34:
        return "-"
        
    if score >= 35:
        return "+"

def settings(input_reddit, debug_in):
    global im_a_bot
    im_a_bot = ["im a bot", "i am a bot", "i'm a bot", "beep boop", "boop beep"]
    global negative_substrings
    negative_substrings = ["bottle", "bottom", "both", "botched", "botanist", "botany"]

    # Amount of comments to fetch for the fast_reply check
    global amount_of_comments
    amount_of_comments = 10

    # How fast the replys in seconds have to be to count plus the fast_replies score
    global fast_reply_in_seconds
    fast_reply_in_seconds = 30

    # Calculate total time for have to be to count plus the fast_replies score
    global total_fast_reply_time
    total_fast_reply_time = int(amount_of_comments * fast_reply_in_seconds)
    
    # How many "Im a bot"s in % (of 1) have to appear in all the comments analysed for it to count plus the im_a_bot_in_comment score
    global im_a_bot_ratio
    im_a_bot_ratio = 0.8

    # Score settings
    global username_contains_bot
    global fast_replies
    global comments_similar
    global im_a_bot_in_comment
    global negative_substring_in_name
    global bot_in_robot
    
    username_contains_bot = 20
    fast_replies = 30
    comments_similar = 25
    im_a_bot_in_comment = 20

    negative_substring_in_name = -15
    bot_in_robot    = -5
    
    global reddit
    reddit = input_reddit
    global debug
    debug = debug_in

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def bot_in_word(input_text):
    if input_text[-4:].lower() == "_bot":
        return True
    if input_text[-4:].lower() == "-bot":
        return True
    if input_text[-3:].lower() == "bot":
        return True

    return False

def checkword(check_against_type, check_against, input_word):
    if check_against_type.lower() == "list":
        for check_word in check_against:
            if check_word.lower() in input_word.lower():
                return True
    else:
        if check_against in input_word:
            return True
            
    return False

def calc_bot_score(input_user):
    bot_score = 0

    # Starting algorithm

    try:
        comments = [comment for comment in reddit.redditor(input_user).comments.new(limit=amount_of_comments)]
    except Exception as e:
        return bot_score

    if checkword("list", negative_substrings, input_user):
        bot_score += negative_substring_in_name
    
    if bot_in_word(input_user):
        bot_score += username_contains_bot
    
    if "robot" in input_user.lower():
        bot_score += bot_in_robot
    
    if debug == True:
        print("Bot name score: " + str(bot_score))

    # Check fast replys
    comment_bodies = [comment.body for comment in comments]
    comments_root = [comment.is_root for comment in comments]
    
    # parent_ids = [comment.parent().fullname for comment in comments]

    parent_ids = []    
    for comment in comments:
        if not comment.is_root:
            parent_ids.append(comment.parent().fullname)
                
    parent_timestamps = [parent.created for parent in reddit.info(parent_ids)]
        
    submission_fullnames = [comment.link_id for comment in comments]
    submission_timestamps = [submission.created for submission in reddit.info(submission_fullnames)]
    
    if not len(comments) < amount_of_comments:
        total_time = 0
        while len(comments) != 0:
            comment = comments[0]
            comment_is_root = comments_root[0]
        
            if comment_is_root == True:

                submission_date = datetime.datetime.fromtimestamp(submission_timestamps[0])
                comment_date    = datetime.datetime.fromtimestamp(comment.created)
                difference = (submission_date - comment_date).total_seconds()
        
                total_time += difference
            else:
                # original_comment_id = comment.parent_id.split("t1_")[1]

                # original_comment = reddit.comment(id=original_comment_id)

                org_comment_date = datetime.datetime.fromtimestamp(parent_timestamps[0])
                comment_date    = datetime.datetime.fromtimestamp(comment.created)
                difference = (org_comment_date - comment_date).total_seconds()
        
                total_time += difference
                parent_timestamps.pop(0)
            if debug == True:
                print("Difference: " + str(difference))
                
            comments.pop(0)
            comments_root.pop(0)
            
            submission_timestamps.pop(0)

            


        total_time = int(total_time * -1)
        
        if debug == True:
            print("Total comment time: " + str(total_time))
    
        if total_time <= total_fast_reply_time:
            bot_score += fast_replies
        else:
            bot_score += int((fast_replies * -1) / 2)

        if debug == True:
            print("Fast reply score: " + str(bot_score))

        # Check comment similarity
        total_diff = 0
    
        chunk_comments = chunks(comment_bodies, 2)
        
        for chunk in chunk_comments:
            diff = difflib.SequenceMatcher(None, chunk[0], chunk[1]).ratio()
            total_diff += diff

        total_diff = int(total_diff * 7.5)
        bot_score += total_diff
    else:
        if debug == True:
            print("Not enough comments to determine score")
        return bot_score
    
    if debug == True:
        print("Comment similarity: " + str(bot_score))
    
    # Check if "Im a bot" (or similar) is in comment.body
    min_bot_comments = int(amount_of_comments * im_a_bot_ratio)
    
    im_a_bot_num = 0
    for comment in comment_bodies:
        if im_a_bot_num < min_bot_comments:
            for variation in im_a_bot:
                if variation.lower() in comment.lower():
                    if debug == True:
                        print("Im a bot detected")
                    im_a_bot_num += 1
                    
    if im_a_bot_num == min_bot_comments:
        bot_score += im_a_bot_in_comment


    return bot_score
