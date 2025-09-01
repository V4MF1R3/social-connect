# Social Connect

A Django-based social networking backend with JWT authentication, posts, comments, follows, notifications, and an admin panel. Uses Supabase for media storage and PostgreSQL as the database.

## Features
- User registration, login, JWT authentication
- User profile with privacy settings
- Create, update, delete posts with image upload (Supabase Storage)
- Like/unlike posts
- Comment on posts
- Follow/unfollow users
- Notifications for likes, comments, follows
- Admin panel for user and post management

## Setup

### 1. Clone the repository
```
git clone <your-repo-url>
cd social-connect
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Configure environment variables
Edit `.env` with your Supabase, database, and email credentials.

### 4. Run migrations
```
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser
```
python manage.py createsuperuser
```

### 6. Start the server
```
python manage.py runserver
```

## API Usage
- All endpoints are under `/api/`
- Use JWT tokens for authenticated requests
- See `requirements.txt` for dependencies

## Supabase Storage
- Create a public bucket named `posts` for post images
- Set appropriate RLS policies for uploads

## Admin Panel
- Django admin: `/admin/`
- Custom adminpanel: `/api/admin/` endpoints (requires user with `UserProfile.role = 'admin'`)

## Testing
- Use Postman or similar tools for manual API testing
- See code and tests for endpoint details

---

**Developed with Django, DRF, Supabase, and PostgreSQL.**
