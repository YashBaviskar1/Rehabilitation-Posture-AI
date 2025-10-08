### Backend Stuff

make sure whie adding files in backend branch here

```bash
git checkout backend

git add backend/

git commit -m "Describe your changes here"

# Push to the backend branch
git push origin backend
```

Required secrets in .env file
JWT_SECRET
DATABASE_URL mysql+pymysql://username:password@localhost/db_name

Create environment
python -m virtualenv venv

Activate environment
(for windows)
venv\Scripts\activate.bat
(for mac)
source venv/bin/activate

Install dependencies
pip install -r requirements.txt
