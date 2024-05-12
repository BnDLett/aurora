from datetime import datetime
import asyncpraw
import interactions

# submission = None  # I'm not sure why this is here.


async def fetch_post(subreddit: str, reddit: asyncpraw.Reddit):
    reddit_post = await reddit.subreddit(subreddit, fetch=True)
    reddit_submission = await reddit_post.random()

    nsfw = bool(reddit_submission.over_18)
    desc = f"""```fix\nScore: {reddit_submission.score}\nUpvote ratio: {reddit_submission.upvote_ratio}```"""
    post_embed = interactions.Embed(title=reddit_submission.title, description=desc, url=reddit_submission.url)
    post_embed.set_image(reddit_submission.url)

    comments = ""
    i = 0
    for comment in await reddit_submission.comments():
        # comments += (f"**{comment.author}**\n{comment.body}\n`Score: {comment.score}`\n\n") Leaving this here for
        # legacy purposes
        if i > 5:
            pass
        i += 1
        comments += f"```yaml\nAuthor: {comment.author}\nScore: {comment.score}\n\n{comment.body}```\n"

    comments_embed = interactions.Embed(title="Comments", description=comments)
    return post_embed, comments_embed, nsfw, reddit_submission.author


async def fetch_profile(username: str, reddit: asyncpraw.Reddit) -> interactions.Embed:
    redditor = await reddit.redditor(name=username)
    await redditor.load()

    time = datetime.fromtimestamp(redditor.created_utc).strftime("%A, %B %d, %Y %I:%M:%S")
    embed = interactions.Embed(title=redditor.name,
                               description=f"```yaml\nComment karma: {redditor.comment_karma}\nID: {redditor.id}"
                                           f"\nAccount creation: {time}```"
                               )
    embed.set_thumbnail(url=redditor.icon_img)
    return embed
