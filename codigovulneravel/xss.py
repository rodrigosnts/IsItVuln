Cross-Site Scripting (XSS)

@app.route("/blogs")
def blogs():
    if not logged_in():
        return redirect("/login", code=302)

    username = request.args.get("u")
    if not username:
        username = session[SESSION_USERNAME]

    blogs = (
        blogmanager.get(username)
        if username != session[SESSION_USERNAME]
        else blogmanager.get(username, True)
    )
    return render_template("blogs.tpl", username=sanitize(username), blogs=blogs)