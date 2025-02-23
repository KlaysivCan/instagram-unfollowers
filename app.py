from flask import Flask, render_template, request
import html.parser
import os

app = Flask(__name__)

class InstagramParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.usernames = []
        self.capture_username = False

    def handle_starttag(self, tag, attrs):
        # Kullanıcı adlarını çıkartmak için <a> etiketini kontrol et
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href' and 'instagram.com' in attr[1]:  # Instagram kullanıcı adlarını içeren bağlantılar
                    self.capture_username = True

    def handle_endtag(self, tag):
        if tag == 'a':
            self.capture_username = False

    def handle_data(self, data):
        if self.capture_username:
            self.usernames.append(data.strip())  # Kullanıcı adını eklemeden önce boşlukları temizle

def extract_usernames(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        parser = InstagramParser()
        parser.feed(file.read())
    return set(parser.usernames)

def find_unfollowers(followers_file, following_file):
    followers = extract_usernames(followers_file)
    following = extract_usernames(following_file)
    
    unfollowers = following - followers
    return unfollowers

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        followers_file = request.files['followers']
        following_file = request.files['following']

        # Geçici dosyalar oluştur
        followers_path = os.path.join('uploads', followers_file.filename)
        following_path = os.path.join('uploads', following_file.filename)
        
        followers_file.save(followers_path)
        following_file.save(following_path)

        unfollowers = find_unfollowers(followers_path, following_path)

        # Geçici dosyaları sil
        os.remove(followers_path)
        os.remove(following_path)

        return render_template('index.html', unfollowers=unfollowers)

    return render_template('index.html', unfollowers=None)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)