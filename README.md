# flogger

Creating a Blog with Flask and Python

Most of this code is a guided lesson.

This repo is to get help with the final project: USERS CAN COMMENT 
* users do not need to be logged in - therefore can not edit or delete 
* comments users enter 'Your Name' and 'Your Comment' and submit 
* posted comments are displayed at the bottom of the comments list,  
oldest first/bottom and newest last/top

This is what I did

1. create a new blog post for commenting so I can test it out as I code it  
* Title: Commenting On A Post 
* Content: lorem ipsum generator @ https://www.lipsum.com/ 
* Category: Programming 
* Tags: flask, python, forms 

2. update root blog.models.py to include comment table, comments relationship, and Comment class

3. update root blog.forms.py to include CommentForm

4. update root blog.views.py to include @blog_app.route("/post/int:post_id/comment", methods=["GET", "POST"])

5. create root templates.blog.comment_posts.html

6. update root templates.blog.article.html

7. do database migration since new blog models were added

Issues: the CommentForm is not showing on the site so I do not know if this feature works.  
Also, I do not know how to test the Comments in tests.py
