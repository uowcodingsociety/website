from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class ExecMember(db.Model):
    __tablename__ = "execMembers"

    execID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    course = db.Column(db.String(128))
    bio = db.Column(db.String(612))
    nationality = db.Column(db.String(128))
    pronouns = db.Column(db.String(32))
    team = db.Column(db.String(128))
    title = db.Column(db.String(128))
    liLink = db.Column(db.String(512), default = "")
    ghLink = db.Column(db.String(512), default = "")
    year = db.Column(db.String(64), default = "")
    imageLink = db.Column(db.String(128), default = "")

    def __init__(self, name, course, bio, nationality, pronouns, team, title, liLink, year, ghLink=""):
        self.name = name
        self.course = course
        self.bio = bio
        self.nationality = nationality
        self.pronouns = pronouns
        self.team = team
        self.title = title
        self.liLink = liLink
        self.ghLink = ghLink
        self.imageLink = name.replace(" ", "")

class BlogPost(db.Model):
    __tablename__ = "blogPosts"

    postID = db.Column(db.Integer, primary_key=True)
    postTitle = db.Column(db.String(128))
    postDescription = db.Column(db.String(256))
    postTags = db.Column(db.String(256))
    postCreationDate = db.Column(db.Date)
    postContent = db.Column(db.Text)
    postAuthor = db.Column(db.String(256))
    postImageURL = db.Column(db.String(256))

    def __init__(self, postTitle, postDescription, postTags, postContent, postAuthor, postImageURL):
        self.postTitle = postTitle
        self.postDescription = postDescription
        self.postTags = postTags
        self.postContent = postContent
        self.postCreationDate = date.today()
        self.postAuthor = postAuthor
        self.postImageURL = postImageURL

class Sponsor(db.Model):
    __tablename__ = "sponsors"

    sponsorID = db.Column(db.Integer, primary_key=True)
    sponsorName = db.Column(db.String(256))
    sponsorDescription = db.Column(db.String(1024))
    sponsorIndustry = db.Column(db.String(256))
    sponsorTier = db.Column(db.String(128))
    sponsorSiteURL = db.Column(db.String(512))
    sponsorImageName = db.Column(db.String(256))

    def __init__(self, sponsorName, sponsorDescription, sponsorIndustry, sponsorTier, sponsorSiteURL, sponsorImageName):
        self.sponsorName = sponsorName
        self.sponsorDescription = sponsorDescription
        self.sponsorIndustry = sponsorIndustry
        self.sponsorTier = sponsorTier
        self.sponsorSiteURL = sponsorSiteURL
        self.sponsorImageName = sponsorImageName

class SponsorNews(db.Model):
    __tablename__ = "sponsorNews"

    newsID = db.Column(db.Integer, primary_key=True)
    sponsorID = db.Column(db.Integer)
    newsTitle = db.Column(db.String(256))
    newsDescription = db.Column(db.String(1024))
    newsURL = db.Column(db.String(1024))
    newsImageName = db.Column(db.String(256))

    def __init__(self, sponsorID, newsTitle, newsDescription, newsURL, newsImageName):
        self.sponsorID = sponsorID
        self.newsTitle = newsTitle
        self.newsDescription = newsDescription
        self.newsURL = newsURL
        self.newsImageName = newsImageName
