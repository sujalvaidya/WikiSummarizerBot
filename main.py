import wikipedia
import sentences
import warnings
import time
import praw
import threading
import bot_detector
from urllib.parse import unquote
from bs4 import BeautifulSoup


class logger:
    def log(*, type, message):
        print("[" + time.ctime() + "] [" + str(type) + "]: " + str(message))


warnings.filterwarnings("ignore")
wiki_links_list = []
USERNAME = 'WikiSummarizerBot'
reddit = praw.Reddit(
    client_id="Axy12sJ50CKKFQ",
    client_secret='yInibcPcl_6s-IcPEyghaPi-PaNrKA',
    user_agent="realmadridbot by u/realmadridbot",
    username=USERNAME,
    password='sujalyatin',
)
reddit1 = praw.Reddit(
    client_id="Axy12sJ50CKKFQ",
    client_secret='yInibcPcl_6s-IcPEyghaPi-PaNrKA',
    user_agent="realmadridbot by u/realmadridbot",
    username='realmadridbot',
    password='sujalyatin',
)

disallowed_strings = ["List_of", "Glossary_of", "Category:", "  File:", "Wikipedia:", "Help:"]
body_disallowed_strings = ["From a modification: This is a redirect from a modification of the target's title or a "
                           "closely related title. For example, the words may be rearranged, or punctuation may be "
                           "different.", "From a miscapitalisation: This is a redirect from a miscapitalisation. The "
                                         "correct form is given by the target of the redirect.", "{\displaystyle"]

subreddit_banned_file = "Blacklists/subreddit_banned.txt"
users_opted_out_file = "Blacklists/users_opted_out.txt"

exclude_strings = ["Opt Out", "Opt Out Of Subreddit"]
include = "OptIn"
footer_links = [
    ['F.A.Q', 'https://www.reddit.com/r/WikiSummarizer/wiki/index#wiki_f.a.q'],
    [exclude_strings[0],
     "https://reddit.com/message/compose?to=WikiSummarizerBot&message=" + exclude_strings[0].replace(" ",
                                                                                                     "") + "&subject="
     + exclude_strings[0].replace(" ", "")],
    [exclude_strings[1], "https://np.reddit.com/r/SUBREDDITNAMEHERE/about/banned"],
    ["GitHub", "https://github.com"]
]
user_already_excluded = "You already seem to have opted out of the bot.\n\nTo be included again, [message me]" \
                        "(https://reddit.com/message/compose?to=WikiSummarizerBot&message=" + include + "&subject=" + \
                        include + ").\n\nHave a nice day!"
user_exclude_done = "Done! If you want to be included again, [message me]" \
                    "(https://reddit.com/message/compose?to=WikiSummarizerBot&message=" + include + "&subject=" + \
                    include + ").\n\nHave a nice day!"
user_include_done = "Done!\n\nHave a nice day!"
user_not_excluded = "It seems you are not excluded from the bot. If you think this is false, " \
                    "[message](https://www.reddit.com/message/compose?to=Sujal_7) me.\n\nHave a nice day!"
active_subs_string = str(
    reddit.subreddit('WikiSummarizer').wiki['active_subs'].content_md.replace('\n', '').
        split('* ')[1:])[1:-1].replace(', ', '+').replace('*', '').replace("'", '')

users_opted_out_list = reddit.subreddit('WikiSummarizer').wiki['users_opted_out']. \
                           content_md.replace('\n', '').split('* ')[1:]
users_opted_out_list = [x.replace('*', '') for x in users_opted_out_list]

active_subs_list = reddit.subreddit('WikiSummarizer').wiki['active_subs']. \
                       content_md.replace('\n', '').split('* ')[1:]
active_subs_list = [x.replace('*', '') for x in active_subs_list]

bot_detector.settings(reddit, False)


def get_summary(wiki_links_list):
    all_wiki_summaries = ''
    for i in range(len(wiki_links_list)):
        comment_url = wiki_links_list[i]
        valid_url = True
        section = False
        wiki_para = ''
        wiki_title = ''
        wiki_title_section = ''
        if comment_url[:30] == 'https://en.wikipedia.org/wiki/':
            wiki_title = comment_url.split("https://en.wikipedia.org/wiki/")[1]
            wiki_title = wiki_title.split('#')[0]
        elif comment_url[:32] == 'https://en.m.wikipedia.org/wiki/':
            wiki_title = comment_url.split("https://en.m.wikipedia.org/wiki/")[1]
            wiki_title = wiki_title.split('#')[0]
        for string in disallowed_strings:
            if string.lower() in wiki_title.lower():
                valid_url = False
        if valid_url:
            try:
                if '#' in comment_url:
                    wiki_title_section = comment_url.split("#")[1]
                    wiki_title_section = wiki_title_section.replace('_', " ")
                    wiki_para = wikipedia.WikipediaPage(title=wiki_title).section(wiki_title_section)
                    if wiki_para != None:
                        section = True

                if not section:
                    wiki_para = wikipedia.WikipediaPage(title=wiki_title).summary
                wiki_summary_list = sentences.split(wiki_para)[:4]
                wiki_summary = ''
                noofsen = 0
                for sentence in wiki_summary_list:
                    if len(wiki_summary) <= 675:
                        if not wiki_summary:
                            wiki_summary = wiki_summary + sentence
                        else:
                            wiki_summary = wiki_summary + " " + sentence
                        noofsen += 1
                if len(wiki_summary) >= 675:
                    wiki_summary = ''
                    wiki_summary_list = wiki_summary_list[:noofsen - 1]
                    for sentence in wiki_summary_list:
                        if len(wiki_summary) <= 675:
                            if not wiki_summary:
                                wiki_summary = wiki_summary + sentence
                            else:
                                wiki_summary = wiki_summary + " " + sentence

                if (wiki_summary == ''):
                    valid_url = False

                for string in body_disallowed_strings:
                    if string.lower() in wiki_summary.lower():
                        valid_url = False
                if valid_url:
                    if section:
                        all_wiki_summaries = all_wiki_summaries + '**' + wiki_title + '** \n \n [' + wiki_title_section \
                                             + '](' + comment_url + ') \n \n >' + wiki_summary + '\n \n'
                    else:
                        all_wiki_summaries = all_wiki_summaries + '**[' + wiki_title + '](' + comment_url + \
                                             ')** \n \n >' + wiki_summary + '\n \n'
            except Exception as e:
                pass
    return all_wiki_summaries


def delete_downvoted():
    while True:
        print("Checking comments...")

        for comment in reddit.redditor(USERNAME).comments.controversial('all', limit=None):
            if comment.score <= -1:
                comment.delete()
                print(str(comment.score) + " got removed")

        print("Comments Checked!")
        time.sleep(60 * 10)


def comment_body(comment_reply, comment):
    comment_reply = comment_reply + "^([ )" + "^( | )".join(["[^(" + link[0] + ")](" + link[1] + ")" for link in
                                                             footer_links]) + \
                    "^( ] Downvote to remove | Credit: kittens_from_space)"
    comment_reply = comment_reply.replace("SUBREDDITNAMEHERE", str(comment.subreddit))
    return comment_reply


def check_inbox():
    global active_subs_string, users_opted_out_list, active_subs_list, execute
    while True:
        for message in reddit.inbox.unread():
            message.mark_read()
            author = str(message.author)
            if not author == USERNAME:
                if exclude_strings[0].replace(" ", "").lower() == message.subject.lower():
                    users_opted_out_data = reddit.subreddit('WikiSummarizer').wiki['users_opted_out'].content_md
                    if f' {author}\n\n*' in users_opted_out_data:
                        message.reply(user_already_excluded)
                    else:
                        logger.log(type="INFO", message="Excluding user {}".format(author))
                        reddit1.subreddit('WikiSummarizer').wiki['users_opted_out'].edit(users_opted_out_data +
                                                                                         f' {author}\n\n*')
                        users_opted_out_list = reddit.subreddit('WikiSummarizer').wiki['users_opted_out'].content_md. \
                                                   replace('\n', '').split('* ')[1:]
                        users_opted_out_list = [x.replace('*', '') for x in users_opted_out_list]
                        get_users_opted_out(users_opted_out_list)

                        message.reply(user_exclude_done)

                elif include.lower() == message.subject.lower():
                    users_opted_out_data = reddit.subreddit('WikiSummarizer').wiki['users_opted_out'].content_md
                    if f' {author}\n\n*' in users_opted_out_data:
                        logger.log(type="INFO", message="Including user {}".format(author))
                        reddit1.subreddit('WikiSummarizer').wiki['users_opted_out'].edit(users_opted_out_data.
                                                                                         replace(f' {author}\n\n*', ''))
                        users_opted_out_list = reddit.subreddit('WikiSummarizer').wiki['users_opted_out']. \
                                                   content_md.replace('\n', '').split('* ')[1:]
                        users_opted_out_list = [x.replace('*', '') for x in users_opted_out_list]
                        get_users_opted_out(users_opted_out_list)
                        message.reply(user_include_done)
                    else:
                        message.reply(user_not_excluded)
                elif "banned" in str(message.subject).lower():
                    author = str(message.subject).split("r/")[1]
                    banned_subs_data = reddit.subreddit('WikiSummarizer').wiki['banned_subs'].content_md
                    reddit1.subreddit('WikiSummarizer').wiki['banned_subs'].edit(banned_subs_data + f' {author}\n\n*')
                    logger.log(type="INFO", message="Banned from {}".format(author))
                elif 'you are an approved user' in str(message.subject).lower():
                    author = message.body.split('/r/')[1]
                    author = author.split(':')[0]
                    active_subs_data = reddit.subreddit('WikiSummarizer').wiki['active_subs'].content_md
                    reddit1.subreddit('WikiSummarizer').wiki['active_subs'].edit(active_subs_data + f' {author}\n\n*')
                    active_subs_string = str(
                        reddit.subreddit('WikiSummarizer').wiki['active_subs'].content_md.replace('\n', '').
                            split('* ')[1:])[1:-1].replace(', ', '+').replace('*', '').replace("'", '')
                    get_subs_list(active_subs_string)
                    active_subs_list = reddit.subreddit('WikiSummarizer').wiki['active_subs']. \
                                           content_md.replace('\n', '').split('* ')[1:]
                    active_subs_list = [x.replace('*', '') for x in active_subs_list]
                    get_active_subs_list(active_subs_list)
                    logger.log(type="INFO", message="Approved user of {}".format(author))
                execute = False
                submission_refresher = reddit.submission(id="mkfq6r")
                reddit1.submission(submission_refresher).reply(body='1')



def get_subs_list(*args):
    subs_string = active_subs_string
    return subs_string


def get_users_opted_out(*args):
    users_list = users_opted_out_list
    return users_list


def get_active_subs_list(*args):
    subs_list = active_subs_list
    return subs_list


execute = True


def main():
    global execute
    while True:
        for comment in reddit.subreddit(get_subs_list()).stream.comments(skip_existing=True) or not execute:
            if not execute:
                print('Refreshing...')
                execute = True
                break
            else:
                try:
                    wiki_links_list = []
                    comment_text = str(comment.body)
                    if 'https://en.m.wikipedia.org/wiki/' in comment_text or \
                            'https://en.wikipedia.org/wiki/' in comment_text:
                        if comment.author.name not in get_users_opted_out():
                            bot_score = bot_detector.calc_bot_score(comment.author.name)
                            if bot_score > 34:
                                logger.log(type="INFO",
                                           message="{} seems to be a bot (score: {}) Not responding.".format
                                           (comment.author.name, bot_score))
                            else:
                                logger.log(type="INFO",
                                           message="{} has a score of {}, responding.".format(comment.author.name,
                                                                                              bot_score))
                                soup = BeautifulSoup(comment.body_html, "lxml")
                                links_list = []
                                for url in soup.findAll('a'):
                                    links_list.append(url['href'])
                                for links in links_list:
                                    if ('https://en.m.wikipedia.org/wiki/' in links) or \
                                            ('https://en.wikipedia.org/wiki/' in links):
                                        links = unquote(links)
                                        if wiki_links_list.count(links) == 0:
                                            wiki_links_list.append(links)
                                if 0 < len(wiki_links_list) < 4:
                                    comment_reply = get_summary(wiki_links_list)
                                    if comment_reply and not (comment_reply.split('.')[0] in comment_text):
                                        try:
                                            comment.reply(comment_body(comment_reply, comment))
                                            logger.log(type="INFO",
                                                       message="Responded to {} by {}".format(
                                                           'https://www.reddit.com/' +
                                                           comment.permalink,
                                                           comment.author.name))
                                        except Exception as e:
                                            print(e)
                except Exception as e:
                    print(e)


'''
def main_all():
    while True:
        print('Refreshing...')
        cnt = 0
        for comment in reddit.subreddit('all').stream.comments(skip_existing=True):
            try:
                wiki_links_list = []
                comment_text = str(comment.body)
                comment_sub = str(comment.subreddit)
                comment_mods = reddit.subreddit(comment_sub).moderator()
                cnt += 1
                if 'BotTerminator' not in comment_mods and 'BotDefense' not in comment_mods:
                    if comment_sub not in get_active_subs_list():
                        if 'https://en.m.wikipedia.org/wiki/' in comment_text or \
                                'https://en.wikipedia.org/wiki/' in comment_text:
                            if comment.author.name not in get_users_opted_out():
                                bot_score = bot_detector.calc_bot_score(comment.author.name)
                                if bot_score > 34:
                                    logger.log(type="INFO",
                                               message="{} seems to be a bot (score: {}) Not responding.".format
                                               (comment.author.name, bot_score))
                                else:
                                    logger.log(type="INFO", message="{} has a score of {}, responding.".
                                               format(comment.author.name, bot_score))
                                    soup = BeautifulSoup(comment.body_html, "lxml")
                                    links_list = []
                                    for url in soup.findAll('a'):
                                        links_list.append(url['href'])
                                    for links in links_list:
                                        if ('https://en.m.wikipedia.org/wiki/' in links) or \
                                                ('https://en.wikipedia.org/wiki/' in links):
                                            links = unquote(links)
                                            if wiki_links_list.count(links) == 0:
                                                wiki_links_list.append(links)
                                    if 0 < len(wiki_links_list) < 4:
                                        comment_reply = get_summary(wiki_links_list)
                                        if comment_reply and not (comment_reply.split('.')[0] in comment_text):
                                            try:
                                                comment.reply(comment_body(comment_reply, comment))
                                                logger.log(type="INFO",
                                                           message="Responded to {} by {}".format
                                                           ('https://www.reddit.com/' + comment.permalink,
                                                            comment.author.name))
                                                break
                                            except Exception as e:
                                                print(e)
                if cnt > 15:
                    break
            except Exception as e:
                print(e)
'''


def run():
    threads = []
    main_thread = threading.Thread(target=main, args=(), name="WikiMain")
    # main_all_thread = threading.Thread(target=main_all, args=(), name="WikiMainAll")
    downvoted_thread = threading.Thread(target=delete_downvoted, args=(), name="Delete Downvoted")
    check_inbox_thread = threading.Thread(target=check_inbox, args=(), name="Check Inbox")
    threads.append(main_thread)
    # threads.append(main_all_thread)
    threads.append(downvoted_thread)
    threads.append(check_inbox_thread)
    for thread in threads:
        thread.start()
